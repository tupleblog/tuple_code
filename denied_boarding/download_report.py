import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
from dateutil import parser

years = range(2011, 2017)
uris = ['https://www.rita.dot.gov/bts/sites/rita.dot.gov.bts/files/subject_areas/airline_information/passengers_denied_confirmed_space_report/%s/index.html' % str(year) for year in years]

def get_table_uris(uris):
    """get all HTML link from all given uris"""
    html_uris = []
    for uri in uris:
        page = requests.get(uri)
        soup = BeautifulSoup(page.text, "lxml")
        html_uri = [uri.replace('index.html', '') + 'html/' + u.get('href').split('/')[-1] for u in soup.find_all('a') if u.text == 'HTML']
        html_uris.extend(html_uri)
    return html_uris

def get_report(html_uri):
    """given HTML, get report dataframe as a dataframe"""
    page = requests.get(html_uri)
    soup = BeautifulSoup(page.text, "lxml")
    table = soup.find('tbody')
    trs = [tr for tr in table.find_all('tr')]
    report_table = []
    for i, tr in enumerate(trs):
        if i == 0:
            columns = [th.text.strip() for th in tr.find_all('th')]
        else:
            report_table.append([th.text.strip() for th in tr.find_all('td')])
    report_df = pd.DataFrame(report_table, columns=columns)
    return report_df

def parse_time(q):
    """Parse time in format of '2014_q4' to datetime format"""
    year = q.split('_')[0]
    quarter = q.split('_')[-1]
    if quarter == '1q':
        month = 'January'
    elif quarter == '2q':
        month = 'April'
    elif quarter == '3q':
        month = 'July'
    else:
        month = 'October'
    return parser.parse('1 ' + month + ' ' + year)

if __name__ == '__main__':
    html_uris = get_table_uris(uris)
    reports = []
    for html_uri in html_uris:
        report_df = get_report(html_uri)
        report_df.loc[:, 'time'] = html_uri.split('/')[-1].split('.')[0]
        report_df.loc[:, 'uri'] = html_uri
        reports.append(report_df)
    reports_all_df = pd.concat(reports, axis=0)
    reports_all_df.to_csv('denied_boarding.csv', index=False)
