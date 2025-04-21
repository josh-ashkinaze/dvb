import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import re
import pandas as pd


def scrape_yc_companies():
    """
    Scrape YCombinator companies from the AI Assistant category URL

    Returns:
        list: A list of dictionaries containing company metadata
    """
    url = "https://www.ycombinator.com/companies/industry/ai-assistant"

    print(f"Scraping companies from: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception for 4XX/5XX status codes
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve data: {e}")
        return []

    # Parse HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all company elements
    companies_data = []

    # Try multiple selectors for finding company elements
    selectors = [
        'li.my-2.flex.h-auto.w-full.flex-col',  # Common format
        'li.flex.h-auto.w-full.flex-col',  # Alternative format
        'li.my-2.flex',  # Shorter format
        'li.flex.w-auto'  # Another variation
    ]

    company_elements = []
    for selector in selectors:
        elements = soup.select(selector)
        if elements:
            company_elements = elements
            print(f"Found {len(elements)} companies using selector: {selector}")
            break

    if not company_elements:
        company_elements = soup.select('li[class*="flex"][class*="border"]')
        print(f"Found {len(company_elements)} companies with fallback selector")

    for company in company_elements:
        try:
            company_data = {}

            name_element = company.select_one('span.text-2xl') or company.select_one('span.font-bold')
            if name_element:
                company_data['name'] = name_element.text.strip()

            logo_element = company.select_one('img.rounded-full') or company.select_one('img.h-20')
            if logo_element and logo_element.has_attr('src'):
                company_data['logo_url'] = logo_element['src']

            profile_links = company.select('a[href^="/companies/"]')
            if profile_links:
                company_data['yc_profile'] = f"https://www.ycombinator.com{profile_links[0]['href']}"


            for span in company.select('span'):
                text = span.text.strip()
                if re.match(r'^[WSF]\d{4}$', text):
                    company_data['batch'] = text
                    break

            info_elements = company.select('span.text-gray-700')
            for element in info_elements:
                text = element.text.strip()

                if text == "Active":
                    company_data['status'] = "Active"

                employees_match = re.search(r'(\d+)\s*employees', text)
                if employees_match:
                    company_data['employees'] = int(employees_match.group(1))

                if ", " in text and "employees" not in text:
                    company_data['location'] = text

            description_element = company.select_one('div.mt-1.line-clamp-3') or company.select_one('div.text-gray-600')
            if description_element:
                company_data['description'] = description_element.text.strip()

            tags = []
            tag_elements = company.select('div.yc-tw-Pill')

            for tag in tag_elements:
                tag_text = tag.text.strip()


                if tag_text and not re.match(r'^[WSF]\d{4}$', tag_text):
                    if not tag.select_one('svg'):
                        tags.append(tag_text)

            company_data['tags'] = [t for t in list(set(tags)) if t]

            # Only add companies that have at least a name
            if 'name' in company_data and company_data['name']:
                companies_data.append(company_data)

        except Exception as e:
            print(f"Error processing company: {str(e)}")

    return companies_data


def save_to_json(data, filename):
    """Save scraped data to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Data saved to {filename}")



def main():
    print("Starting to scrape YC AI Assistant companies...")

    companies = scrape_yc_companies()

    if companies:

        save_to_json(companies, "../data/raw/yc_ai_assistant_companies.json")

        tags = {}
        for company in companies:
            for tag in company.get('tags', []):
                if tag not in tags:
                    tags[tag] = 0
                tags[tag] += 1
        tag_df = pd.DataFrame.from_dict(tags, orient='index', columns=['count']).reset_index()
        tag_df.columns = ['tag', 'count']
        print(f"Unique tags found: {len(tag_df)}")
        tag_df.to_json("../data/raw/yc_ai_assistant_tags.jsonl", orient='records', lines=True)




if __name__ == "__main__":
    main()