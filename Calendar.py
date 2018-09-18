#!/usr/bin/python

import sys,  calendar, os
from datetime import datetime
import re
import Events

def renderDate(month, year, curDate, events):
   if not events or not events[(month, curDate, year)]:
      return "\\day{}{\\vspace{2.5cm}} %% %d\n" % curDate
   def getStartTime(s):
      if s == 'Noon': s = "12 pm"
      # Find am / pm string
      # default to pm
      am = False
      match = re.search("am|pm", s, re.IGNORECASE)
      if match and match.group(0).lower() == 'am':
          am = True

      if '-' in s:
        s = s.split("-")[0].strip()
      s = re.sub("am|pm| ", "", s, 0, re.IGNORECASE).strip()

      if am: retVal = 0
      else: retVal = 10000000 # Make PM much higher
      if ':' in s:
         s = s.split(":")
         return retVal + (int(s[0]) % 12) * 60 + int(s[1])
      return retVal + (int(s[0]) % 12) * 60

   def DSSorter(x,y):
      if x[0] == 'NULL': return -1
      if y[0] == 'NULL': return 1
      xTime = getStartTime(x[0])
      yTime = getStartTime(y[0])
      return xTime - yTime

   def cleanForLatex(x):
      return re.sub(r"((?<!\\)[#\$%\^&_\{\}~])", r"\\\1", x)


   day = events[(month, curDate, year)]
   day.sort(cmp=DSSorter)
   b = "\\day{}{"
   for x in day:
      x = [e.strip() for e in x]
      if x[0] == "NULL":
         b+= "%s \\\\" % x[1]
      else:
         b+= "%s \\daysep %s \\\\" % (x[0], cleanForLatex(x[1]))
   b+= "} %% %d\n" % curDate
   return b


def main():
    # Default arguments
    now = datetime.now()
    month = now.month
    year = now.year
    eventsFile = "Events.txt"

    # Read argument
    num_args = len(sys.argv)
    if num_args > 1: month = int(sys.argv[1])
    if num_args > 2: year = int(sys.argv[2])
    if num_args > 3: eventsFile = sys.argv[3]

    # Convert  to get month name
    month_name = calendar.month_name[month]

    # Read events
    try:
        events = Events.readEvents(eventsFile)
    except: # Blank map if Events does not exist
        events = None
    print events

    # start by generating the correct calendar for any month and year
    prefix = open("Prefix.tex").read();
    suffix = open("Suffix.tex").read();
    prefix = prefix.replace("MONTH", month_name).replace("YEAR", str(year))

    # Calculate the number of blank days from Sunday
    firstOfMonth = datetime(year, month, 1)
    # TODO: Verify this computation  for all possible starting days of the week
    numBlankFromSunday = firstOfMonth.isoweekday() % 7

    # Handle any spillover days by putting them on the left of the first row
    numDaysInMonth = calendar.monthrange(year,month)[1]
    numDaysOnFirstRow = 7 - numBlankFromSunday
    numDaysRemaining = numDaysInMonth - numDaysOnFirstRow

    # Start building the body
    body = ""
    numSpillOver = 0
    # Add the spillover days
    if numDaysRemaining > 28: # Number of days we can store in the rest of the calendar
        # Compute the date of spillover and number of spillover days
        spillOverDate = 28 + numDaysOnFirstRow + 1
        numSpillOver = numDaysInMonth - spillOverDate + 1
        numBlankFromSunday -= numSpillOver
        body += "\\setcounter{calendardate}{%d}\n" % spillOverDate
        curDate = spillOverDate
        # TODO: This will eventually be replaced by pulling the contents from an
        # array / map that is modified by events
        for i in xrange(numSpillOver):
            body += renderDate(month,  year, curDate, events)
            curDate += 1

    # Add blank days
    for i in xrange(numBlankFromSunday):
       body += "\\BlankDay\n"

    body += "\\setcounter{calendardate}{1}\n"
    curDate = 1
    # Add the actual days
    for i in xrange(numDaysInMonth - numSpillOver):
        body += renderDate(month,  year, curDate, events)
        curDate += 1

    # Write files
    TEX_FILE = "out/%s.tex" % month_name
    PDF_FILE = "out/%s.pdf" % month_name

    # Create directory if it does not exist
    try:
        os.mkdir("out");
    except:
        pass

    with open(TEX_FILE, "w") as f:
      f.write(prefix)
      f.write(body)
      f.write(suffix)

    # Generate pdf
    os.system("pdflatex -output-directory out %s" % TEX_FILE)

    # Open it
    os.system("evince %s &" % PDF_FILE)

if __name__ == "__main__": main()
