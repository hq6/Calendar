import datetime

# Represent a single event on a calendar
class Event:
  # The inputs are stirngs and are parsed into the appropriate types.
  # datetime.date date
  # datetime.time startTime
  # datetime.time endTime
  # string        description
  # Expected format:
  # Date: MM-DD-YYYY || MM-DD
  # StartTime: Noon || All Day || hh:mm (am|pm)?
  # EndTime: Noon || All Day || hh:mm (am|pm)?
  def __init__(self, date, startTime, endTime, description):
    self.date = date
    self.startTime = startTime
    self.endTime = endTime
    self.description = description


# Output is a list of events.
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
