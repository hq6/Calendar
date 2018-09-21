import datetime
import sys
import re
from functools import total_ordering
import calendar

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

  # Return a textual description of the start and optionally end time.
  def getTimeString(self):
    if not self.startTime:
       return None
    if self.startTime == "All Day":
       return self.startTime
    startString = self.startTime.strftime("%I:%M %p")
    if self.endTime:
      return "-".join([startString, self.endTime.strftime("%I:%M %p")])
    return startString

  def __str__(self):
    return ",".join([str(self.date), str(self.startTime), str(self.endTime), str(self.description)])

  __repr__ = __str__

  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  def __lt__(self, other):
    if self.date != other.date:
      return self.date < other.date
    if self.startTime == None or self.startTime == "All Day":
      return True
    if other.startTime == None or other.startTime == "All Day":
      return False
    return self.startTime < other.startTime

def getDates(from_date, to_date, day_list):
    date_list = list()
    ## Creates a list of all the dates falling between the from_date and to_date range
    for x in xrange((to_date - from_date).days+1):
        date_record = from_date + datetime.timedelta(days=x)
        if date_record.weekday() in day_list:
            date_list.append(date_record)
    return date_list

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

def generateRecurring(line):
    def convertToNumber(dayNameOrAbbr):
        try:
          num = list(calendar.day_name).index(dayNameOrAbbr)
        except:
          num = list(calendar.day_abbr).index(dayNameOrAbbr)
        return num
    parts = line.split(",", 4)
    startDate = parseDate("1-1") if parts[1] == "NULL" else parseDate(parts[1])
    endDate = parseDate("12-31")  if parts[2] == "NULL" else parseDate(parts[2])
    days = getDates(startDate, endDate, [convertToNumber(parts[0])])
    startTime, endTime = parseTime(parts[3])
    return [Event(x, startTime, endTime, parts[4]) for x in days]

# Expected format:
# Date: MM-DD-YYYY || MM-DD
# StartTime: Noon || All Day || hh:mm (am|pm)?
# EndTime: Noon || All Day || hh:mm (am|pm)?
def readEvents(events_file):
    events = list()
    eventsToDelete = list()
    curDate = None
    with open(events_file) as f:
     for line in f:
      # Comments are Python style
      line = line.strip()
      if line == "" or line.startswith("#"): continue
      # Event negation requires short form
      if line.startswith("!"):
        eventsToDelete.append(readEvent(line[1:]))
      if re.match(r"^\d\d?-\d\d?(-\d{4}|\d{2})?$", line): # Long form start
        curDate = parseDate(line)
      elif re.search(r"^\d\d?-\d\d?(-\d{4}|\d{2})?", line): # Short form supercedes long form
        curDate = None
        events.append(readEvent(line))
      # Line is of the form DOW,StartDate,EndDate,Time,Description
      elif re.search(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)", line):
        recurringEvents = generateRecurring(line)
        for e in recurringEvents:
            events.append(e)
      # Continuation of long form is assumed if long form already started.
      # Otherwise we ignore.
      elif curDate:
        parts = line.split(",", 1)
        events[curDate].append(parts)

    events = filter(lambda x: x not in eventsToDelete, events)
    return events

def main():
    events_file = "Events.txt"
    print "\n".join(str(x) for x in sorted(readEvents(events_file)))

if __name__ == "__main__": main()
