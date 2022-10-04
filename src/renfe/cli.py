#!/usr/bin/env python
import json
import logging
import colorama
from datetime import date

from renfe.timetable import get_timetable, get_date, get_days
from renfe.stations import get_station_and_key, station_exists, get_station_name
from renfe.utils import RenfeException, ConfigurationMgmt, parse_args


def main():
    # defaults
    config = ConfigurationMgmt()
    today = date.today()

    options = parse_args(config)

    colorama.init(autoreset=True)
    print(colorama.Fore.GREEN + f"Today is: {today}" + colorama.Fore.RESET)

    if options.search == '':
        # print timetable for given origin and to stations for a given date
        if not (station_exists(options.origin) and (options.to)):
            logging.error(
                "Please, provide right values for origin and destination station names")
            exit(1)
        try:
            origin_name = get_station_name(options.origin)
            destination_name = get_station_name(options.to)
            print(colorama.Fore.GREEN + f"Searching timetable for date: {options.date or get_date(int(options.days))}")
            print(colorama.Fore.GREEN + f"From {origin_name} to {destination_name}" + colorama.Fore.RESET)
            print(colorama.Fore.GREEN + "Be patient, navigating through renfe site now..." + colorama.Fore.RESET)
            days = options.days or get_days(options.date)
            times = get_timetable(
                origin_name,
                destination_name,
                days,
                options.browser,
                int(options.search_timeout))
            print(colorama.Fore.GREEN + "=================================TIMETABLE================================")
            print(colorama.Fore.GREEN + " {:<10} | {:<10} | {:<10} | {:<12} | {:<10}".format(
                'Train', 'Departure', 'Arrival', 'Duration', "Prices"))

            for time in times:
                print(colorama.Fore.GREEN + "--------------------------------------------------------------------------")
                print(colorama.Fore.GREEN + " {:<10} | {:<10} | {:<10} | {:<12} | {:<10} ".format(
                    time["type"], time["departure"], time["arrival"], time["duration"],  " - ".join(time["price"])))
            print(colorama.Fore.GREEN + "==========================================================================" + colorama.Fore.RESET)

            if not times:
                print(colorama.Fore.YELLOW + "Timetable was empty. \
                    Maybe no more trains for today? \
                    Also, try increasing search timeout (-e flag, see help). \
                    Please, open an issue if problem does persist." + colorama.Fore.RESET)

            if options.output:
                with open(options.output, 'w') as f:
                    json.dump(times, f, ensure_ascii=False, indent=4)

        except (RenfeException, ValueError) as err:
            logging.error(err)
            logging.error(
                "No timetables found... Check your inputs and enable debug. If the problem persists,"
                " create an issue at http://www.github.com/gerardcl/renfe-cli/issues")
            exit(1)
    else:
        # search into list of Station names and its Renfe identifiers
        try:
            print(colorama.Fore.GREEN + f"Searching stations like: {options.search}")
            stations_infos = get_station_and_key(options.search)
            for station_info in stations_infos:
                print(colorama.Fore.GREEN + f"{station_info}")

            if not stations_infos:
                print(colorama.Fore.RED + f"Oops! No stations found by key value: {options.search}" + colorama.Fore.RESET)
        except RenfeException as err:
            logging.error(err)
            logging.error(
                "Error searching stations IDs... Check your inputs and enable debug. If the problem persists,"
                " create an issue at http://www.github.com/gerardcl/renfe-cli/issues")
            exit(1)


if __name__ == '__main__':
    main()
