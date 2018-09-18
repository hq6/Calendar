import datetime
import sys
import re
from functools import total_ordering

# Represent a single event on a calendar
@total_ordering
class Event:
  # The inputs are of the following types, although endTIme is allowed to be None.
  # datetime.date date
  # datetime.time startTime
  # datetime.time endTime
  # string        description
  def __init__(self, date, startTime, endTime, description):
    self.date = date
    self.startTime = startTime
    self.endTime = endTime
    self.description = description

  def __str__(self):
    return ",".join([str(self.date), str(self.startTime), str(self.endTime), str(self.description)])

  __repr__ = __str__

  def __eq__(self, other):
    return self__dict__ == other.__dict__

  def __lt__(self, other):
    if self.date != other.date:
      return self.date < other.date
    if self.startTime == None or self.startTime == "All Day":
      return True
    if other.startTime == None or other.startTime == "All Day":
      return False
    return self.startTime < other.startTime

def parseDate(ds):
   parts = ds.split("-")
   if len(parts) == 3:
     t = (int(x) for x in parts)
     return datetime.date(t[2], t[0], t[1])
   elif len(parts) == 2:
     return datetime.date(datetime.datetime.now().year, int(parts[0]), int(parts[1]))
   # An error occurred
   sys.stderr.write("Error parsing date '%s'" % ds)
   return None

# Interpret start and possibly end times.
def parseTime(ts):
   def parseOneDate(ts):
     ts = ts.strip()
     # Special cases
     if ts == "All Day":
       return "All Day"
     if ts == "Noon":
       return datetime.time(12, 0)
     if ts == "NULL":
       return None

     amOrPm = re.search("am|pm", ts, re.IGNORECASE)
     ts = re.sub("am|pm| ", "", ts, 0, re.IGNORECASE).strip()
     if ":" in ts:
         ts = ts.split(":")
         hours, minutes = int(ts[0]), int(ts[1])
     else:
         hours, minutes = int(ts), 0

     if amOrPm:
       isPm = amOrPm.group(0).lower() == 'pm'
       if isPm and hours != 12:
         hours += 12
       elif not isPm and hours == 12:
         hours = 0
     return datetime.time(hours, minutes)

   # Only startTime is available
   if '-' not in ts:
     return parseOneDate(ts), None
   else:
     start, end = ts.split("-")
     return parseOneDate(start), parseOneDate(end)

def readEvent(line):
   parts = line.split(",", 2)
   date = parseDate(parts[0])
   startTime, endTime = parseTime(parts[1])
   return Event(date, startTime, endTime, parts[2])

# Expected format:
# Date: MM-DD-YYYY || MM-DD
# StartTime: Noon || All Day || hh:mm (am|pm)?
# EndTime: Noon || All Day || hh:mm (am|pm)?
def readEvents(events_file):
    events = list()
    curDate = None
    with open(events_file) as f:
     for line in f:
      # Comments are Python style
      line = line.strip()
      if line == "" or line.startswith("#"): continue
      if re.match(r"^\d\d?-\d\d?(-\d{4}|\d{2})?$", line): # Long form start
        curDate = parseDate(line)
      elif re.search(r"^\d\d?-\d\d?(-\d{4}|\d{2})?", line): # Short form supercedes long form
        curDate = None
        events.append(readEvent(line))
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
    print "\n".join(str(x) for x in sorted(readEvents(events_file)))

if __name__ == "__main__": main()
