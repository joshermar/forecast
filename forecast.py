#!/usr/bin/env python3
import json
import requests
import pytz
from datetime import datetime
from dateutil import parser
from dateutil.tz import tzlocal

url = 'https://api.weather.gov/gridpoints/TOP/31,80/forecast'
forecast_file = 'forecast.json'
update_freq = 7200


def decode_data(file_name):
    # May throw an error for missing file or unable to parse
    with open(file_name) as file:
            text = file.read()
    return json.loads(text)


def updated_time_obj(data):
    time_str = data['properties']['updated']
    return parser.parse(time_str)


def up_to_date(file_name, seconds):
    try:
        data = decode_data(file_name)

        now = datetime.now(pytz.utc)

        delta = now - updated_time_obj(data)

        if delta.seconds <= seconds:
            return True

    except (json.decoder.JSONDecodeError, FileNotFoundError, KeyError):
        pass

    return False


def update(file_name, url=url):
    response = requests.get(url)

    if response.ok:
        with open(file_name, 'w') as file:
            file.write(response.text)


def main():
    if not up_to_date(forecast_file, update_freq):
        try:
            update(forecast_file)

        except requests.exceptions.ConnectionError:
            print('Could not update forecast. Do you have a connection?', '\n', sep='')

    try:
        data = decode_data(forecast_file)

        upd = updated_time_obj(data)
        upd_local = upd.astimezone(tzlocal())

        periods = data['properties']['periods']

        print(
            '\n',
            'Last update: ', upd_local.strftime('%c'), "\n",
            '=' * 80, sep='')

        for i in range(0, len(periods), 2):
            print(
                periods[i]['name'], ':', '\n',
                periods[i]['detailedForecast'], '\n',
                '\n',
                periods[i + 1]['name'], ':', '\n',
                periods[i + 1]['detailedForecast'], '\n',
                '=' * 80,
                sep='')

    except (FileNotFoundError, json.decoder.JSONDecodeError, KeyError):
        print('Forecast data file is missing or damaged!', '\n', sep='')


if __name__ == '__main__':
    main()
