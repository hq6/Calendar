#!/usr/bin/python

import re
from datetime import datetime, timedelta
from collections import defaultdict
import calendar


def getCurrentYear():
   return datetime.now().year

def readDate(ds):
   parts = ds.split("-")
   if len(parts) == 3:
     if len(parts[2]) == 2:
       parts[2] = "20" + parts[2] # hardcoding is bad but it's good for another 85 years 
     return tuple(int(x) for x in parts)
   elif len(parts) == 2:
     return tuple(int(x) for x in parts) + (getCurrentYear(),)

def readEvent(line):
   parts = line.split(",", 2)
   date = readDate(parts[0])
   return (date, parts[1:])

def get_dates(from_date, to_date, day_list):
    tmp_list = list()
    date_list = list()
    ## Creates a list of all the dates falling between the from_date and to_date range
    for x in xrange((to_date - from_date).days+1):
        tmp_list.append(from_date + timedelta(days=x))
    for date_record in tmp_list:
        if date_record.weekday() in day_list:
            date_list.append(date_record)
    return [(x.month, x.day, x.year) for x in date_list]

def generateRecurring(line):
    def convertToNumber(dayNameOrAbbr):
        try:
          num = list(calendar.day_name).index(dayNameOrAbbr)
        except:
          num = list(calendar.day_abbr).index(dayNameOrAbbr)
        print num
        return num
    parts = line.split(",", 4)
    startDate = readDate("1-1") if parts[1] == "NULL" else readDate(parts[1])
    endDate = readDate("12-31")  if parts[2] == "NULL" else readDate(parts[2])
    days = get_dates(datetime(startDate[2], startDate[0], startDate[1]),
            datetime(endDate[2], endDate[0], endDate[1]),
            [convertToNumber(parts[0])])
    return [(x, parts[3:]) for x in days]

# Events is a map from 3-tuples of integers (month, day, year) to tuples of strings (timestring, description)
# Extract all and then filter
def readEvents(events_file):
    events = defaultdict(list)
    curDate = None
    with open(events_file) as f:
     for line in f:
      # Comments are Python style
      line = line.strip()
      if line == "" or line.startswith("#"): continue
      if re.match(r"^\d\d?-\d\d?(-\d{4}|\d{2})?$", line): # Long form start
        curDate = readDate(line)
      elif re.search(r"^\d\d?-\d\d?(-\d{4}|\d{2})?", line): # Short form supercedes long form
        curDate = None
        event = readEvent(line)
        events[event[0]].append(event[1])
      # Line is of the form DOW,StartDate,EndDate,Time,Description
      elif re.search(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)", line):
        recurringEvents = generateRecurring(line)
        for e in recurringEvents:
            events[e[0]].append(e[1])
      # Continuation of long form is assumed if long form already started.
      # Otherwise we ignore.
      elif curDate:
        parts = line.split(",", 1)
        events[curDate].append(parts)

    return events



def main():
    events_file = "Events.txt"
    print readEvents(events_file)

if __name__ == "__main__": main()
