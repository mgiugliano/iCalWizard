#!/usr/bin/env python3
#
#
#

from iCalWiz_analyseCalendars import *
import sys
# import collections

USAGE = "\nUSAGE:\n bookme.py howLong (min) howSoon (days) priority (1,2,3,4) title [email]\n"

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


# Let's read the configuration from file...
exec(open('iCalWiz_config.py').read())

# Days ahead for scheduling ToDos (i.e. from right now, onwards)
# Ndays = 60
Ndays = howSoon
# ------------------------------------------------------------------------------

# MAIN
# 1. launch iCalBuddy
stdout = launch_iCalBuddy(Ndays, inclCals)

# 2. parse iCalBuddy output
tstart, tstop = parse_iCalBuddy(
    Ndays, stdout, startWorkingTime, stopWorkingTime, workingDays, swTime)


# 3. find free time slots
ftstart, ftstop, dur = get_free_time(tstart, tstop)


# print(str(fNev) + " chunks of free-time found, over the next " +
#       str(Ndays) + " days.")

# for i in range(fNev):
#     free_t = free_tstart[i].strftime("%a %d %b %H:%M")
#     print("Free time chunk of " +
#           str(duration[i]) + " min on\t " + free_t)

# ------------------------------------------------------------------------------
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
    print("[" + str(i) + "]: Found! Book it on " +
          ftstart[i].strftime("%a %d %b %H:%M"))
    print("(" + str(dur[i]) + " min available)")
    # print(title)
    # print(email)

    if query_yes_no("Schedule an actual event [Y/n]?"):
        print("Writing on the Calendar!")
        stdout = schedule_iCal('fix', title, ftstart[i], ftstart[i] + timedelta(
            minutes=howLong), 'SISSA', 'taskWarrior integration', 'http://0.0.0.0:5678/tasks/pending', '34', email)
        print(stdout)
        print()
    # ------------------------------------------------------------------------------
