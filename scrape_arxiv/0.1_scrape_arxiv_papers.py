import logging
import os
import time
import xmltodict
import pandas as pd
from datetime import datetime, timedelta
from sickle import Sickle
from urllib.error import HTTPError
from requests.exceptions import RequestException
from tqdm import tqdm

logging.basicConfig(filename=f"{os.path.splitext(os.path.basename(__file__))[0]}.log", level=logging.INFO,
                    format='%(asctime)s: %(message)s', filemode='w', datefmt='%Y-%m-%d %H:%M:%S', force=True)

# Config section - edit these values as needed
#################
CONFIG = {
    "N_YEARS": 7,
    "RAW_FILE": "../data/arxiv/arxiv_metadata_raw.xml",
    "CSV_FILE": "../data/arxiv/arxiv_papers.csv",
    "SET": "cs"
}


def setup_config(config):
    """Set up config parameters"""
    # Create parent directories if they don't exist
    for file_path in [config["RAW_FILE"], config["CSV_FILE"]]:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    print(f"Raw file: {config['RAW_FILE']}")
    print(f"CSV file: {config['CSV_FILE']}")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * config["N_YEARS"])
    config["FROM_DATE"] = start_date.strftime('%Y-%m-%d')
    config["UNTIL_DATE"] = end_date.strftime('%Y-%m-%d')

    logging.info("Using this config:")
    for key, value in config.items():
        logging.info(f"{key}: {value}")

    return config


CONFIG = setup_config(CONFIG)


##################


def get_next_record_with_retry(data_iterator, max_attempts=10):
    """
    Get the next record with simple retry logic that respects server's Retry-After header
    """
    attempts = 0
    while attempts < max_attempts:
        try:
            return next(data_iterator)
        except StopIteration:
            # This is normal, just re-raise
            raise
        except (HTTPError, RequestException) as e:
            attempts += 1

            # Get the retry interval from the response headers
            retry_after = None
            if hasattr(e, 'response') and hasattr(e.response, 'headers'):
                retry_after = e.response.headers.get('Retry-After')

            if retry_after:
                wait_time = int(retry_after)
                logging.info(
                    f"Server requested retry after {wait_time} seconds (attempt {attempts}/{max_attempts}). Waiting...")
            else:
                wait_time = 30
                logging.info(
                    f"No Retry-After header found. Using default wait time of 30 seconds (attempt {attempts}/{max_attempts}).")

            time.sleep(wait_time)

            # If this was the last attempt, re-raise the exception
            if attempts >= max_attempts:
                logging.error(f"Maximum retry attempts ({max_attempts}) reached. Giving up.")
                raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise


def download_metadata(config):
    """
    Download metadata based on config parameters"

    Args:
        config (dict): Configuration dictionary containing parameters for downloading metadata.

    """
    connection = Sickle('http://export.arxiv.org/oai2')
    logging.info(f'Getting {config["SET"]} papers from {config["FROM_DATE"]} to {config["UNTIL_DATE"]}...')
    params = {
        'metadataPrefix': 'arXiv',
        'from': config["FROM_DATE"],
        'until': config["UNTIL_DATE"],
        'ignore_deleted': True,
        'set': config["SET"]
    }

    try:
        data = connection.ListRecords(**params)
        logging.info('Papers retrieved. Beginning to process records.')
    except Exception as e:
        logging.error(f'Failed to establish initial connection: {e}')
        raise

    iters = 0
    errors = 0

    pbar = tqdm(desc="Downloading records", unit="records")

    with open(config["RAW_FILE"], 'w', encoding="utf-8") as f:
        while True:
            try:
                record = get_next_record_with_retry(data)
                f.write(record.raw)
                f.write('\n')
                errors = 0
                iters += 1

                # Update progress bar
                pbar.update(1)

                if iters % 1000 == 0:
                    pbar.set_description(f"Downloaded {iters} records")
                    logging.info(f'{iters} Processing Attempts Made Successfully.')

            except StopIteration:
                pbar.close()
                logging.info(
                    f'Metadata download complete. {iters} total records retrieved for {config["FROM_DATE"]} - {config["UNTIL_DATE"]}.')
                break

            except Exception as e:
                errors += 1
                logging.error(f'Unexpected error: {e}')
                if errors > 5:
                    pbar.close()
                    logging.critical('Too many consecutive errors, stopping the harvester.')
                    raise

    return iters


def convert_dict(record_xml):
    """Convert XML record to dictionary format"""
    try:
        record_dict = xmltodict.parse(record_xml, process_namespaces=False)['record']['metadata']['arXiv']

        # Ensure id is a string
        record_dict['id'] = str(record_dict['id'])

        # Process authors
        if 'authors' in record_dict and record_dict['authors']:
            if not isinstance(record_dict['authors']['author'], list):
                authors = [record_dict['authors']['author']]
            else:
                authors = record_dict['authors']['author']

            # Format author names
            authors = [(author['forenames'] + ' ' if 'forenames' in author.keys() else '') + author['keyname'] for
                       author in authors]
            record_dict['authors'] = authors
        else:
            record_dict['authors'] = []

        # Add url field
        record_dict['url'] = f"https://arxiv.org/abs/{record_dict['id']}"

        return record_dict
    except Exception as e:
        logging.error(f"Error converting record to dict: {e}")
        return None


def parse_raw_data(config):
    """Parse the raw XML data into a structured format"""
    logging.info("Starting to parse raw metadata...")

    raw_data = ""
    logging.info("Reading raw data file...")
    with open(config["RAW_FILE"], 'r', encoding="utf-8") as f:
        with tqdm(desc="Reading raw data", unit="bytes") as pbar:
            while True:
                data = f.read(100_000_000)
                if not data:
                    break
                else:
                    raw_data += data
                    pbar.update(len(data))

    # Split into individual records
    logging.info("Splitting raw data into individual records...")
    list_of_xml = raw_data.split('</record>')
    list_of_xml = [_ + '</record>' for _ in list_of_xml[:-1]]  # Last element will be empty
    total_records = len(list_of_xml)
    logging.info(f"Found {total_records} records to process")

    logging.info("Converting records to dictionaries...")
    list_of_dicts = []

    # Process records with a progress bar
    for i, xml in tqdm(enumerate(list_of_xml), total=total_records, desc="Processing records", unit="records"):
        if xml.strip():  # Skip empty records
            try:
                record_dict = convert_dict(xml)
                if record_dict:
                    list_of_dicts.append(record_dict)
            except Exception as e:
                logging.error(f"Error processing record {i}: {e}")

    logging.info("Creating DataFrame...")
    df = pd.DataFrame(list_of_dicts)
    print(df)

    # Add URL and clean up categories
    logging.info("Processing categories and authors...")
    if 'categories' in df.columns:
        df['keywords'] = df['categories'].apply(
            lambda x: x if isinstance(x, str) else ', '.join(x) if isinstance(x, list) else "")

    if 'authors' in df.columns:
        df['authors_str'] = df['authors'].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x))

    logging.info(f"Saving to CSV: {config['CSV_FILE']}")
    df.to_csv(config["CSV_FILE"], index=False)
    logging.info(f"Saved {len(df)} records to {config['CSV_FILE']}")

    return df


def analyze_papers(df, config):
    """Analyze the papers and print statistics"""
    logging.info("\n=== Statistics ===")
    logging.info(f"Total {config['SET']} papers: {len(df)}")

    if 'created' in df.columns:
        logging.info(f"Date range: {min(df['created'])} to {max(df['created'])}")

    if 'categories' in df.columns:
        all_cats = []
        logging.info("Analyzing categories...")
        for cats in tqdm(df['categories'], desc="Counting categories"):
            if isinstance(cats, str):
                all_cats.extend([c.strip() for c in cats.split()])
            elif isinstance(cats, list):
                all_cats.extend(cats)

        from collections import Counter

        cat_counts = Counter(all_cats)
        logging.info(f"Top 10 most common {config['SET']} subcategories:")
        for cat, count in cat_counts.most_common(10):
            if cat.startswith(f"{config['SET']}."):
                logging.info(f"  {cat}: {count} papers")


def main(config=None):
    """Main function to download and process arXiv papers"""
    if config is None:
        config = CONFIG

    logging.info(
        f"Starting arXiv papers download for {config['SET']} from {config['FROM_DATE']} to {config['UNTIL_DATE']}")

    try:
        num_records = download_metadata(config)

        if num_records > 0:
            df = parse_raw_data(config)

            analyze_papers(df, config)
        else:
            logging.warning("No records were downloaded.")

    except Exception as e:
        logging.critical(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    main()