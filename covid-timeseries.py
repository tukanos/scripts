#!/usr/bin/env python3

# Plot COVID data from the Corona Data Scraper.

import json
import argparse

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

import sys, os


DATAFILEURL = 'https://coronadatascraper.com/timeseries-byLocation.json'

DATA_DIR = os.path.expanduser("~/Data/covid")


def fetch_data():
    datafile = os.path.join(DATA_DIR, 'timeseries-byLocation.json')

    # XXX Check last-mod date and update if needed
    if not os.path.exists(datafile):
        r = requests.get(DATAFILEURL)
        with open(datafile, 'wb') as datafd:
            datafd.write(r.content)
        print("Wrote", datafile)
    else:
        print(datafile, "was already cached")

    with open(datafile) as infp:
        return json.loads(infp.read())


covid_data = fetch_data()


def show_locations(matches):
    print("matches:", matches)
    for k in covid_data.keys():
        if matches:
            for m in matches:
                if m in k:
                    print(k)
                    break
        else:
            print(k)


def get_timeseries(location):
    dates = []
    timeseries = {
        'dates': [],
        'cases': [],
        'newcases': [],
        'deaths': [],
        'recovered': []
    }

    def append_or_zero(timeseries, key, dic):
        if key in dic:
            timeseries[key].append(dic[key])
        else:
            timeseries[key].append(0)

    for d in covid_data[location]['dates']:
        dates.append(datetime.datetime.strptime(d, '%Y-%m-%d'))
        append_or_zero(timeseries, 'cases',
                       covid_data[location]['dates'][d])
        if len(timeseries['cases']) >= 2:
            timeseries['newcases'].append(timeseries['cases'][-1]
                                          - timeseries['cases'][-2])
        else:
            timeseries['newcases'].append(0)
        append_or_zero(timeseries, 'deaths',
                       covid_data[location]['dates'][d])
        append_or_zero(timeseries, 'recovered',
                       covid_data[location]['dates'][d])

    return dates, timeseries


def plot_timeseries_matplotlib(dates, timeseries):

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(10, 10))
    ax1.plot(dates, timeseries['cases'], label='Total cases')
    ax1.set_title('Total cases')
    ax2.plot(dates, timeseries['newcases'], color='green', label='New cases')
    ax2.set_title('New cases')
    ax3.plot(dates, timeseries['deaths'], color="red", label='Deaths')
    ax3.set_title('Deaths')

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.gcf().autofmt_xdate()
    plt.tight_layout(pad=2.0, w_pad=10.0, h_pad=3.0)

    plt.show()


# Location can be something like "NM, USA" or "Bernalillo County, NM, USA"
# Run with -L to see all locations, or -L 'pat' to show all locations
# that include a pattern.

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Plot COVID-19 data by location")
    parser.add_argument('-L', "--show-locations", dest="show_locations",
                        default=False, action="store_true",
                        help="Show all available locations")
    parser.add_argument('locations', nargs='*',
                        help="Locations to show")
    args = parser.parse_args(sys.argv[1:])

    if args.show_locations:
        show_locations(args.locations)
        sys.exit(0)

    try:
        dates, timeseries = get_timeseries(args.locations[0])
        plot_timeseries_matplotlib(dates, timeseries)

    except IndexError:
        parser.print_help()
        sys.exit(1)


