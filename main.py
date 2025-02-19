import logging
import argparse

import datetime
from pathlib import Path

import cses
from icalendar import Calendar, Event, vText

def calc_start_end_CN():
    now = datetime.datetime.now()
    month = now.month

    if 9 <= month <= 12 or 1 <= month <= 2:
        # Term 1 (September to January)
        start_date = datetime.date(now.year if month >= 9 else now.year - 1, 9, 1)
        end_date = datetime.date(now.year + 1 if month >= 9 else now.year, 1, 31)
    else:
        # Term 2 (March to July)
        start_date = datetime.date(now.year, 2, 1)
        end_date = datetime.date(now.year, 7, 31)

    return start_date, end_date

def main():
    parser = argparse.ArgumentParser(description='Class schedule generator.')
    parser.add_argument('--calendar-start-date', type=str, help='Calendar start date (YYYY-MM-DD)')
    parser.add_argument('--calendar-end-date', type=str, help='Calendar end date (YYYY-MM-DD)')
    #parser.add_argument('--ignore-start-time', type=str, help='Ignore timespan start (HH:MM)')
    #parser.add_argument('--ignore-end-time', type=str, help='Ignore timespan end (HH:MM)')
    #parser.add_argument('--ignore-class-names', type=str, help='Comma-separated list of class names to ignore')
    parser.add_argument('--start-time', type=str, help='Single week start time in ISO format')
    parser.add_argument('--output-filename', type=str, help='Output filename', default='schedule.ics')
    parser.add_argument('profile', nargs='?', help='CSES filename as a positional argument')
    args = parser.parse_args()
    
    profile_path = args.profile
    
    if not profile_path:
        logging.fatal("No CSES file provided")
        return

    # Check if the file is valid CSES file
    if not cses.CSESParser.is_cses_file(profile_path):
        logging.fatal("Not a valid CSES file")
        return
    #Try loading CSES
    parser = cses.CSESParser(profile_path)

    # Load subjects
    subjects = parser.get_subjects()
    # Load Schedule
    schedules = parser.get_schedules()
    logging.debug("Subjects: %s", subjects)
    # Get subjects
    for subject in parser.get_subjects():
        print("Name:", subject["name"])
        print("Simplified Name:", subject["simplified_name"])
        print("Teacher:", subject["teacher"])
        print("Room:", subject["room"])
        print("")

    # Get schedules
    for schedule in parser.get_schedules():
        print("Name:", schedule["name"])
        print("Enable Day:", schedule["enable_day"])
        print("Weeks:", schedule["weeks"])
        print("Classes:")
        for class_ in schedule["classes"]:
            print("  Subject:", class_["subject"])
            print("  Start Time:", class_["start_time"])
            print("  End Time:", class_["end_time"])
        print("")

    # Create Calendar
    cal = Calendar()
    profile_name = Path(profile_path).stem
    cal['summary'] = f'CSES iCalendar {profile_name}'
    if args.calendar_start_date:
        cal['dtstart'] = datetime.datetime.strptime(args.calendar_start_date, '%Y-%m-%d').date()
    else:
        cal['dtstart'] = calc_start_end_CN()[0]
    if args.calendar_end_date:
        cal['dtend'] = datetime.datetime.strptime(args.calendar_end_date, '%Y-%m-%d').date()
    else:
        cal['dtend'] = calc_start_end_CN()[1]
    
    output_file = args.output_filename
    with open(output_file, 'wb') as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')
    try:
        main()
    except Exception as e:
        logging.fatal(e)
        raise