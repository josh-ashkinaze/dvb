
"""
Date: 2025-04-04 10:39:04

Description: Scrapes arxiv papers.

CREDIT: Using parts of the code from the following sources
- https://jacktol.net/posts/arxiv_rag_project_part_1/
- https://christinakouridi.wordpress.com/2019/06/16/harvesting-metadata-of-1-5million-arxiv-papers/

An improvement in this one is better rate limit handling, but the underlyng Sickle logic is similar

Input files:
- None

Output files:
- ../data/arxiv/cs_arxiv_metadata_raw.xml: Raw metadata from arxiv
- ../data/arxiv/cs_arxiv_papers.csv:


"""




import logging
import os
import time
import xmltodict
import pandas as pd
from datetime import datetime, timedelta
from sickle import Sickle
from urllib.error import HTTPError
from requests.exceptions import RequestException
from tenacity import retry, stop_after_attempt, retry_if_exception_type, before_sleep_log
from tqdm import tqdm

logging.basicConfig(filename=f"{os.path.splitext(os.path.basename(__file__))[0]}.log", level=logging.INFO, format='%(asctime)s: %(message)s', filemode='w', datefmt='%Y-%m-%d %H:%M:%S', force=True)

# Config section - edit these values as needed
#################
CONFIG = {
    "N_YEARS": 7,
    "OUTPUT_DIR": "../data/arxiv",
    "SET": "cs",
    "FILE_PREFIX": "cs_arxiv"
}


def setup_directories_and_files(config):
    """Set up directories and file paths based on config"""
    os.makedirs(config["OUTPUT_DIR"], exist_ok=True)

    raw_file = os.path.join(config["OUTPUT_DIR"], f"{config['FILE_PREFIX']}_metadata_raw.xml")
    csv_file = os.path.join(config["OUTPUT_DIR"], f"{config['FILE_PREFIX']}_papers.csv")

    config["RAW_FILE"] = raw_file
    config["CSV_FILE"] = csv_file

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * config["N_YEARS"])
    config["FROM_DATE"] = start_date.strftime('%Y-%m-%d')
    config["UNTIL_DATE"] = end_date.strftime('%Y-%m-%d')

    logging.info("Using this config:")
    for key, value in config.items():
        logging.info(f"{key}: {value}")

    return config


CONFIG = setup_directories_and_files(CONFIG)


##################


def wait_retry_after(retry_state):
    """
    Tries to parse retry after from arxiv since arxiv will give a specific
    number. If cant find it, we will default to 30 seconds.

    """
    exception = retry_state.outcome.exception()
    if isinstance(exception, HTTPError) and hasattr(exception, 'response'):
        retry_after = exception.response.headers.get('Retry-After')
        if retry_after:
            seconds = int(retry_after)
            logging.info(f"Server requested retry after {seconds} seconds. Waiting...")
            return seconds
    return 30


@retry(
    retry=retry_if_exception_type((HTTPError, RequestException)),
    stop=stop_after_attempt(10),
    wait=wait_retry_after,
    before_sleep=before_sleep_log(logging.getLogger(), logging.INFO)
)
def get_next_record(data_iterator):
    """Get the next record with retry logic"""
    try:
        return next(data_iterator)
    except HTTPError as e:
        raise e


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
                record = get_next_record(data)
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