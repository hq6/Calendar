#!/usr/bin/python

import sys, calendar, os
from datetime import datetime, date
import re
import Events
from xml.sax.saxutils import escape, unescape

def createLatexCalendar(events, month, year):
    def renderDate(month, year, day, events):
       if not events:
          return "\\day{}{\\vspace{2.5cm}} %% %d\n" % day

       # Extract the events on a given day
       dayEvents = filter(lambda x: x.date == date(year, month, day), events)
       if not dayEvents:
          return "\\day{}{\\vspace{2.5cm}} %% %d\n" % day

       def cleanForLatex(x):
          return re.sub(r"((?<!\\)[#\$%\^&_\{\}~])", r"\\\1", x)

       out = "\\day{}{"
       for event in dayEvents:
          if event.startTime == None:
             out+= "%s \\\\" % event.description
          else:
             out+= "%s \\daysep %s \\\\" % (event.getTimeString(), cleanForLatex(event.description))
       out+= "} %% %d\n" % day
       return out
    # Convert to get month name
    month_name = calendar.month_name[month]

    # start by generating the correct calendar for any month and year
    prefix = open("res/Prefix.tex").read();
    suffix = open("res/Suffix.tex").read();
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

def createHTMLCalendar(events, month, year):
    def renderDate(month, year, day, events):
       if not events:
          return '<td><div class="dayOfMonth">%d</div></td>' % day

       # Extract the events on a given day
       dayEvents = filter(lambda x: x.date == date(year, month, day), events)
       if not dayEvents:
          return '<td><div class="dayOfMonth">%d</div></td>' % day

       def escapeHTMLEntity(x):
          return escape(x)

       out = '<td><div class="dayOfMonth">%d</div><div class="dayContents">' % day
       for event in dayEvents:
          if event.startTime == None:
             out+= "<span>%s</span><br />\n" % event.description
          else:
              out+= "<span style='text-decoration: underline'>%s</span><br />\n<span>%s</span><br />\n" % \
                  (event.getTimeString(), escapeHTMLEntity(event.description))
       out+= "</div></td>"
       return out
    # Convert to get month name
    month_name = calendar.month_name[month]

    prefix = open("res/Prefix.html").read();
    suffix = "</table></html>"
    prefix = prefix.replace("MONTH", month_name).replace("YEAR", str(year))

    # Calculate the number of blank days from Sunday
    firstOfMonth = datetime(year, month, 1)
    numBlankFromSunday = firstOfMonth.isoweekday() % 7

    # Handle any spillover days by putting them on the left of the first row
    numDaysInMonth = calendar.monthrange(year,month)[1]

    # Start building the body
    body = "<tr>\n"
    dayCounter = 0

    # Add blank days
    for i in xrange(numBlankFromSunday):
       body += "<td><div class='dayContents'></div></td>\n"
       dayCounter += 1

    # Add the actual days
    for i in xrange(numDaysInMonth):
        body += renderDate(month,  year, i + 1, events)
        dayCounter += 1
        if dayCounter % 7 == 0:
            body += "</tr>\n"
            body += "<tr>\n"

    # Create directory if it does not exist
    try:
        os.mkdir("out");
    except:
        pass

    HTML_FILE = "out/%s.html" % month_name

    with open(HTML_FILE, "w") as f:
      f.write(prefix)
      f.write(body)
      f.write(suffix)

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

    # Read events
    try:
        events = Events.readEvents(eventsFile)
    except:
        events = None

    createLatexCalendar(events, month, year)
    createHTMLCalendar(events, month, year)

if __name__ == "__main__": main()
