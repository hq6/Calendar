## Henry's Calendar

This is a simple tool for generating a pdf calendar from a lightweight
text-based format. The code quality is not great, but it was hacked together in
a couple of hours, and is sufficient for its current purpose.


In order to use it, one must edit the `Events.txt` file and run `make` to
generate the calendar for the current month of the current year.

    vim Events.txt
    make

If one wishes to generate a calendar for a different month or year such as
10/2016, one can manually provide the numerical month and/or year arguments.

    ./Calendar.py 10 2016
