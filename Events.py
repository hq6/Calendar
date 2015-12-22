#!/usr/bin/python

import re
from datetime import datetime
from collections import defaultdict


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
