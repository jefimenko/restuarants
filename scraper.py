from bs4 import BeautifulSoup
from copy import copy
import requests
import sys
import re

TARGET_DOMAIN = 'http://info.kingcounty.gov'
TARGET_PATH = '/health/ehs/foodsafety/inspections/Results.aspx'
TARGET_QUERY = {
    'Output': 'W',
    'Business_Name': '',
    'Business_Address': '',
    'Longitude': '',
    'Latitude': '',
    'City': '',
    'Zip_Code': '',
    'Inspection_Type': 'All',
    'Inspection_Start': '',
    'Inspection_End': '',
    'Inspection_Closed_Business': 'A',
    'Violation_Points': '',
    'Violation_Red_Points': '',
    'Violation_Descr': '',
    'Fuzzy_Search': 'N',
    'Sort': 'H',
}


def get_inspection_page(**kwargs):
    url = TARGET_DOMAIN + TARGET_PATH
    params = copy(TARGET_QUERY)

    for key, val in kwargs.items():
        if key in TARGET_QUERY:
            params[key] = val
    response = requests.get(url, params=params)
    response.raise_for_status
    return response.content, response.encoding


def load_inspection_page():
    with open('inspection_page.html') as page:
        data = page.readlines()
    doc = ''
    enc = data[-1]
    for line in data[:-1]:
        doc = '{}{}'.format(doc, line)
    return doc, enc


def save_inspection_page(content, encoding):
    with open('inspection_page.html', 'w') as page:
        page.write(content)
        page.write('\r\n' + encoding)


def parse_source(content, encoding='utf-8'):
    parsed = BeautifulSoup(content, from_encoding=encoding)
    return parsed


def extract_data_listings(soup):
    # Select a list of all html tags with class pattern PR[]~
    return soup.find_all(id=re.compile(r'PR\d+~'))


def extract_restuarant_metadata(listing):
    metadata = {}
    metadata_rows = listing.find('tbody').find_all(
        has_two_tds, recursive=False)
    for row in metadata_rows:
        key, value = row.find_all('td', recursive=False)
        key, value = clean_data(key), clean_data(value)
        if key:
            metadata[key] = value
        else:
            metadata['Address'] = '{}, {}'.format(metadata['Address'], value)

    return metadata


def extract_score_data(listing):
    inspection_rows = listing.find_all(is_inspection_row)
    total, high_score, inspections, average = 0, 0, 0, 0
    for row in inspection_rows:
        score = int(row.find_all('td', recursive=False)[2].text)
        if score > high_score:
            high_score = score
        total += score
        inspections += 1

    if inspections:
        average = float(total)/inspections
    return {
        'Average Score': average,
        'High Score': high_score,
        'Total Inspections': inspections}


def has_two_tds(tag):
    return tag.name == 'tr' and len(tag.find_all('td', recursive=False)) == 2


def is_inspection_row(tag):
    if tag.name == 'tr':
        row_cells = tag.find_all('td', recursive=False)
        tag_text = clean_data(row_cells[0]).lower()
        return len(row_cells) == 4 \
            and not tag_text.startswith('inspection') \
            and 'inspection' in tag_text
    else:
        return False


def generate_results(new):
    if new:
        params = {}
        params['Inspection_Start'] = '2/1/2014'
        params['Inspection_End'] = '2/1/2015'
        params['Zip_Code'] = '98006'
        content, encoding = get_inspection_page(**params)
        save_inspection_page(content, encoding)
    else:
        content, encoding = load_inspection_page()

    doc = parse_source(content, encoding)
    listings = extract_data_listings(doc)
    for listing in listings:
        metadata = extract_restuarant_metadata(listing)
        restuarant_data = extract_score_data(listing)
        restuarant_data.update(metadata)
        yield restuarant_data
        print

    print len(listings)


def clean_data(cell):
    try:
        return cell.string.strip('- :\n')
    except AttributeError:
        return ''

if __name__ == '__main__':
    for result in generate_results(len(sys.argv) == 1):
        print result

    # if len(sys.argv) == 1:
    #     params = {}
    #     params['Inspection_Start'] = '2/1/2014'
    #     params['Inspection_End'] = '2/1/2015'
    #     params['Zip_Code'] = '98006'
    #     content, encoding = get_inspection_page(**params)
    #     save_inspection_page(content, encoding)
    # else:
    #     content, encoding = load_inspection_page()

    # doc = parse_source(content, encoding)
    # listings = extract_data_listings(doc)
    # for listing in listings:
    #     metadata = extract_restuarant_metadata(listing)
    #     restuarant_data = extract_score_data(listing)
    #     restuarant_data.update(metadata)
    #     print restuarant_data
    #     print

    # print len(listings)
    # print listings[0].prettify()
