import csv
import pandas as pd
import requests
from bs4 import BeautifulSoup
from itertools import groupby
from operator import itemgetter
from difflib import get_close_matches


def get_all_station_links(link='http://www.transitbangkok.com/bangkok_bus_routes.php'):
    """
    Get all Bus stations from Bangkok Bus Routes
    """
    body = requests.get(link)
    soup = BeautifulSoup(body.text, "lxml")
    stations = []
    for link in soup.find_all('a'):
        if '/stations/' in link.get('href'):
            stations.append(link.get('href'))
    stations = list(set(stations))
    return stations

def get_all_stations(link='http://www.transitbangkok.com/bangkok_bus_routes.php'):
    """
    Load all unique stations available and
    get all stations details
    """
    stations_links = get_all_station_links()
    stations_links = list(set(['http://www.transitbangkok.com' + s for s in stations_links]))
    station_soup = []
    for station_link in stations_links:
        body = requests.get(station_link)
        soup = BeautifulSoup(body.text, "lxml")
        station_soup.append([station_link, soup])

    stations = []
    for (station_link, soup) in stations_soup:
        station_name = soup.find('span', attrs={'itemprop': 'name'}).get_text()
        for tag in soup.find_all("b"):
            if 'Name in Thai' in tag.text:
                station_thai_name = tag.next_sibling.replace(":", "").strip()
        connecting_lines = []
        c_lines = soup.find('span', attrs={'itemprop': 'description'})
        for c_line in c_lines.find_all('a'):
            if '/lines/bangkok-bus-line/' in (c_line.get('href')):
                connecting_lines.append('http://www.transitbangkok.com' + c_line.get('href'))
        stations.append({'station_link': station_link,
                         'station_name': station_name,
                         'station_thai_name': station_thai_name,
                         'connecting_lines': connecting_lines})
    return stations

def get_all_stations_dataframe(link='http://www.transitbangkok.com/bangkok_bus_routes.php'):
    stations = get_all_stations(link)
    stations_expand = []
    for station in stations:
        for ct in station['connecting_lines']:
            stations_expand.append({'station_link': station['station_link'],
                                    'station_name': station['station_name'],
                                    'station_thai_name': station['station_thai_name'],
                                    'connecting_line': ct})
    stations_df = pd.DataFrame(stations_expand)
    return stations_df

def read_stations(path='data/stations.csv'):
    reader = list(csv.DictReader(open(path)))
    grouper = itemgetter("station_link", "station_thai_name", "station_name")
    stations = []
    for key, group in groupby(sorted(reader, key=grouper), grouper):
        temp_dict = dict(zip(["station_link", "station_thai_name", "station_name"], key))
        temp_dict["connecting_lines"] = [item for item in group]
        stations.append(temp_dict)
    return stations

def query_station(query, stations):
    """
    Get closest bus or train station for given query
    """
    stations_english = [station['station_name'] for station in stations]
    stations_thai = [station['station_thai_name'] for station in stations]
    station_closest = get_close_matches(query , stations_thai + stations_english, n=1, cutoff=0.6)

    if station_closest is not None:
        query_first = station_closest[0]
        query_dict = [station for station in stations if (query_first == station['station_name'] or query_first in station['station_thai_name'])]
        if query_dict:
            query_dict = query_dict[0]
            query_text = '+'.join(query_dict['station_name'].split())
            query_text = query_text.replace(',', '%2C').replace('(', '%28').replace(')', '%29') # replace , with %2C
            query_dict.update({'query': query_text})
            return query_dict
    else:
        return None

def get_commute_instruction_link(start, end, stations):
    query_link = ''
    station_start = query_station(start, stations)
    station_end = query_station(end, stations)
    if not station_start:
        print('something wrong with start location')
        return None
    if not station_end:
        print('something wrong with end location')
        return None
    if station_start and station_end:
        query_link = 'http://www.transitbangkok.com/showBestRoute.php?from=%s&to=%s&originSelected=false&destinationSelected=false&lang=en' \
                    % (station_start['query'], station_end['query'])
    return query_link

def get_commute_instruction(start, end, stations):
    """
    Give start and end destination of the trip,
    return dictionary output of query link and how to get there in list format

    ref: http://stackoverflow.com/questions/43302864/beautifulsoup-getting-all-links-after-given-tag/
    """
    query_link = get_commute_instruction_link(start, end, stations)
    if query_link:
        station_start = query_station(start, stations)
        station_end = query_station(end, stations)

        route_request = requests.get(query_link)
        soup_route = BeautifulSoup(route_request.content, 'lxml')
        routes = soup_route.find('div', attrs={'id': 'routeDescription'})

        parsed_routes = list()
        for img in routes.find_all('img'):
            action = img.next_sibling
            to_station = action.next_sibling
            links = list()
            for sibling in img.next_siblings:
                if sibling.name == 'a':
                    links.append(sibling)
                elif sibling.name == 'img':
                    break

            lines = list()
            if 'travel' in action.lower():
                lines.extend([to_station.find_next('b').text])
                lines.extend([link.contents[0] for link in links])
            parsed_route = {'action': action.replace(' to', '').replace('Travel', 'Public Transport').strip(),
                            'to': to_station.text,
                            'lines': lines}
            parsed_routes.append(parsed_route)
        return {'query_link': query_link,
                'route_descrtions': parsed_routes,
                'station_start': {'station_name': station_start.get('station_name'),
                                   'station_thai_name': station_start.get('station_thai_name'),
                                   'station_link': station_start.get('station_link')},
                'station_end': {'station_name': station_end.get('station_name'),
                                'station_thai_name': station_end.get('station_thai_name'),
                                'station_link': station_end.get('station_link')}
                }
    return None
