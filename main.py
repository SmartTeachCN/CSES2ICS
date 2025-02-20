import logging
import argparse

import datetime
from pathlib import Path

import cses
from icalendar import Calendar, Event, vText

def find_first_monday(start_date):
    while start_date.weekday() != 0:  # 0 represents Monday
        start_date += datetime.timedelta(days=1)
    return start_date

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

    return find_first_monday(start_date), end_date

def get_date_time_with_offset(start_date, time, offset):
    #FIXME: time sometimes become int, dirty fix that.
    if type(time) == int:
        time = datetime.time(hour=time // 3600, minute=(time % 3600) // 60, second=time % 60).strftime('%H:%M:%S')
    time = datetime.datetime.strptime(time, '%H:%M:%S').time()
    return datetime.datetime.combine(start_date, time) + datetime.timedelta(days=offset)

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
    raw_subjects = parser.get_subjects()
    # Load Schedule
    schedules = parser.get_schedules()
    logging.debug("Subjects: %s", raw_subjects)
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
    
    # Make subjects a dict with name as key
    subjects = {subject["name"]: subject for subject in raw_subjects}

    # Declare start and end date
    start_date, end_date = calc_start_end_CN()
    if args.calendar_start_date:
        start_date = find_first_monday(datetime.datetime.strptime(args.calendar_start_date, '%Y-%m-%d').date())
    if args.calendar_end_date:
        end_date = datetime.datetime.strptime(args.calendar_end_date, '%Y-%m-%d').date()

    profile_name = Path(profile_path).stem
    # Create Calendar
    cal = Calendar()
    cal.add('prodid', '-//CSES2ICS//cses//')
    cal.add('version', '2.0')
    cal.add('summary', vText(f'CSES iCalendar {profile_name}'))
    cal.add('dtstart', start_date)
    cal.add('dtend', end_date)

    # Create Events
    # Create an array of length 14, each element is a list of events for that day
    days = [None for _ in range(14)]
    dedup_days = [False for _ in range(7)]
    # Extract schedules based on weeks (all/odd/even)
    all_schedules = [s for s in schedules if s["weeks"] == 'all']
    odd_schedules = [s for s in schedules if s["weeks"] == 'odd']
    even_schedules = [s for s in schedules if s["weeks"] == 'even']

    # Add schedules to days
    logging.info("Phase 1: Fill schedules")
    for i in range(7):
        current_day_all_schedules = [s for s in all_schedules if s["enable_day"] == i+1]
        current_day_odd_schedules = [s for s in odd_schedules if s["enable_day"] == i+1]
        current_day_even_schedules = [s for s in even_schedules if s["enable_day"] == i+1]
        if not current_day_all_schedules and not current_day_odd_schedules and not current_day_even_schedules:
            continue
        elif not current_day_odd_schedules and not current_day_even_schedules:
            days[i] = current_day_all_schedules[-1]
            days[i+7] = current_day_all_schedules[-1]
            dedup_days[i] = True
            continue
        else:
            days[i] = current_day_odd_schedules[-1] if len(current_day_odd_schedules)>0 else current_day_all_schedules[-1]
            days[i+7] = current_day_even_schedules[-1] if len(current_day_even_schedules)>0 else current_day_all_schedules[-1]
            continue
    
    logging.info("Phase 2: Fill events")
    print(days)
    for i in range(1,8):
        current_schedule = days[i-1]
        for class_ in current_schedule['classes']:
            current_event = Event()
            current_event.add('summary', vText(class_["subject"]))
            current_event.add('dtstart', get_date_time_with_offset(start_date, class_["start_time"], i-1))
            current_event.add('dtend', get_date_time_with_offset(start_date, class_["end_time"], i-1))
            current_event.add('location', vText(subjects[class_["subject"]]['teacher']))
            current_event.add('rrule', {'freq': 'weekly', 'interval': 1 if dedup_days[i-1] else 2})
            cal.add_component(current_event)
    for i in range(8,15):
        if dedup_days[i-8]:
            continue
        current_schedule = days[i-1]
        for class_ in current_schedule['classes']:
            current_event = Event()
            current_event.add('summary', vText(class_["subject"]))
            current_event.add('dtstart', get_date_time_with_offset(start_date, class_["start_time"], i-1))
            current_event.add('dtend', get_date_time_with_offset(start_date, class_["end_time"], i-1))
            current_event.add('location', vText(subjects[class_["subject"]]['teacher']))
            current_event.add('rrule', {'freq': 'weekly', 'interval': 2})
            cal.add_component(current_event)
    
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