import requests
import time
import datetime


BASE_URL = "http://58.181.223.158/srttts/view/"

def scrape_schedule(url, numdays=250):
    """
    Request schedule from today date until numdays before
    """
    today = datetime.datetime.today()
    date_list = [today - datetime.timedelta(days=x) for x in range(0, numdays)]
    date_list = [dt.strftime('%d/%m/%Y') for dt in date_list]

    all_trains = []
    for i, date in enumerate(date_list):
        r = requests.post(url, data={'date': date})
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.find('tbody')
        trs = body.find_all('tr')
        trains = []
        for tr in trs:
            trains.append([td.text.strip() for td in tr.find_all('td')])
        all_trains.append(trains)
        if i % 20 == 0:
            print('finish %d pages' % i)
    return all_trains


if __name__ == '__main__':
    all_trains = scrape_schedule(BASE_URL)
    train_list = []
    for train in all_trains:
        train_list.extend(train)
    cols = ['train_number', 'date', 'departure',
            'stations', 'arrival', 'current',
            'arrival_local', 'departure_local', 'delay']
    train_df = pd.DataFrame(train_list, columns=cols)
    train_df.to_csv('train_arrival.csv', index=False)
