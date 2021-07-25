#!/usr/bin/env python3
#
#
#

from AnalyseCalendars import *
import sys
# import collections

USAGE = "\nUSAGE:\n bookme.py howLong (min) howSoon (days) priority (1,2,3,4) title\n"

arguments = len(sys.argv) - 1
if arguments < 4:
    print(USAGE)
    exit(1)
elif arguments == 4:
    howLong = int(sys.argv[1])
    howSoon = int(sys.argv[2])
    priority = int(sys.argv[3])
    title = sys.argv[4]
    email = ''
else:
    howLong = int(sys.argv[1])
    howSoon = int(sys.argv[2])
    priority = int(sys.argv[3])
    title = sys.argv[4]
    email = sys.argv[5]


# Daily work schedule: [startWorkingtime ; stopWorkingTime].
# Outside this interval, no free time allocation is allowed.
startWorkingTime = "09:00:00"  # (note the full format: H:M:S)
stopWorkingTime = "19:00:00"   # (note the full format: H:M:S)

# Weekly work schedule, specified in terms of working days.
# Outside these days, no free time allocation is allowed.
workingDays = ["monday", "tuesday", "wednesday", "thursday", "friday"]

# Switching time (minutes), required between successive (scheduled) events.
swTime = 5   # in minutes

# Days ahead for scheduling ToDos (i.e. from right now, onwards)
# Ndays = 60
Ndays = howSoon

# Comma-separated list of iCal calendars to include (escape spaces, if needed)
inclCals = "fix,Work,Habits,Neuronal\ Dynamics\ Laboratory"
# ------------------------------------------------------------------------------


stdout = launch_iCalBuddy(Ndays, inclCals)

tstart, tstop = parse_iCalBuddy(
    Ndays, stdout, startWorkingTime, stopWorkingTime, workingDays, swTime)

ftstart, ftstop, dur = get_free_time(tstart, tstop)

# print(str(fNev) + " chunks of free-time found, over the next " +
#       str(Ndays) + " days.")

# for i in range(fNev):
#     free_t = free_tstart[i].strftime("%a %d %b %H:%M")
#     print("Free time chunk of " +
#           str(duration[i]) + " min on\t " + free_t)

fNev = len(ftstart)     # Number of free chunks found

r = list(range(fNev))       # A interatable list of indexes is defined
r = rotate(r, -(fNev//4) * (priority - 1))  # Rotate the list (as in a ring)
# priority == 1 implies iteration start from the start of the list
# priority == 2 implies iteration start from the 1/3rd of the list
# priority == 3 implies iteration start from the 2/3rd of the list
found = False   # Flag to indicate if a free-time chunk was found
for i in r:     # Iterate over the list of free-time chunks
    if dur[i] >= howLong:  # If the chunk is long enough
        found = True           # We found a free-time chunk
        break                  # No need to keep searching, let's exit the loop


if not found:                  # If no free-time chunk was found
    print("No free time found in the next " + str(Ndays) + " days.")
    print("Extend the range of days or split into multiple sittings.")
    exit(1)
else:
    print("Found! Book it on " + ftstart[i].strftime("%a %d %b %H:%M"))
    print("(" + str(dur[i]) + " min available)")
    print(title)
    print(email)
