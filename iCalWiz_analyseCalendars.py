# AnalyseCalendars.py Library (work in progress)
#
# July 25th 2021 - Michele Giugliano
#

# exec(open('AnalyseCalendars.py').read())

from datetime import date, datetime, timedelta
import subprocess
import sys
import os


DEBUG = 0                  # Toggles verbose output


def logme(message):
    if DEBUG == 1:
        print(message)

# ------------------------------------------------------------------------------
# Invoking iCalBuddy - a simple icalendar parser for macOS
# ------------------------------------------------------------------------------


def launch_iCalBuddy(Ndays, inclCals):
    logme("Launching iCalBuddy to extract a list of all scheduled events...")
    # iCalBuddy flags, to specify calendars and to control and minimize its output..
    flags = "-b '' -n -nrd -ea -ic " + inclCals + \
        " -iep datetime -df %Y-%m-%d -tf %H:%M:%S"

    t0 = datetime.now()
    # Date/time interval for getting currently scheduled events:
    # startDate = t0.strftime("%Y-%m-%d %H:%M:%S")  # Rendered as string
    startDate = t0.strftime("%Y-%m-%d 00:00:00")  # Rendered as string
    tF = t0 + timedelta(days=Ndays)               # Date and time + Ndays
    endDate = tF.strftime("%Y-%m-%d %H:%M:%S")    # Rendered as string

    # Note: the definition of 'startDate' is not the current time but the
    # midnight of the current day. This makes possible to avoid artifacts
    # at later stages of the analysis.

    # Command to invoke icalBuddy...
    cmd = "icalBuddy " + flags + ' eventsFrom:"' + \
        startDate + '" to:"' + endDate + '"'
    P = subprocess.run(cmd, shell=True, capture_output=True)
    logme("Launching iCalBuddy by: > " + cmd)

    stdout = P.stdout.decode("utf-8")

    return stdout


# ------------------------------------------------------------------------------
# Parsing icalBuddy output into a pair of lists:
# ------------------------------------------------------------------------------
def parse_iCalBuddy(Ndays, stdout, startWorkingTime, stopWorkingTime, workingDays, swTime):
    logme("Parsing the output from iCalBuddy for the next " +
          str(Ndays) + " days...")
    tstart = []  # array containing the start time of each event
    tstop = []   # array containing the stop time of each event

    for line in stdout.splitlines():    # For each line in the output...
        if len(line) == 47:             # as in '2021-09-01 at 10:00:00 - 2021-09-03 at 14:00:00'
            a1 = line[0:10]   # This is the date of the current event (string)
            a2 = line[14:22]  # Start time of the current event (string)
            # This is the end date of the current event (string)
            b1 = line[25:35]
            b2 = line[38:47]  # End time of the current event (string)
            # Full start date/time of current event (string)
            start = a1 + " " + a2
            # Full end date/time of current event (string)
            stop = b1 + " " + b2
        else:
            a1 = line[0:10]   # This is the date of the current event (string)
            a2 = line[14:22]  # Start time of the current event (string)
            # This is the end time of the current event (string)
            a3 = line[25:33]
            # Full start date/time of current event (string)
            start = a1 + " " + a2
            # Full end date/time of current event (string)
            stop = a1 + " " + a3

        # Let's now add the event's starting and end to the list of events
        t1 = datetime.strptime(start, '%Y-%m-%d %H:%M:%S') - \
            timedelta(minutes=swTime)
        tstart.append(t1)
        t2 = datetime.strptime(stop, '%Y-%m-%d %H:%M:%S') + \
            timedelta(minutes=swTime)
        tstop.append(t2)
        # Note: starting and ending times have been already altered to take the
        # switching times into account.

    # Now let's add "artificial" events (midnight-8am, and 7pm-midnight) to the list
    # capturing intervals of the day when no events should ever be scheduled.
    logme("Generating (midnight-8am and 7pm-midnight) unavailability events...")
    for days in range(Ndays+1):     # For each day in the interval...
        t = date.today() + timedelta(days=days)
        dayName = t.strftime("%A")  # Name of the day (string)
        dayName = dayName.lower()             # Make it lowercase

        if dayName in workingDays:  # If the day is a working day...
            t1 = datetime.combine(t, datetime.strptime(
                "00:00:00", '%H:%M:%S').time())        # midnight
            tstart.append(t1)                          # Add to the list
            t2 = datetime.combine(t, datetime.strptime(
                startWorkingTime, '%H:%M:%S').time())  # 8am, start of the day
            tstop.append(t2)                           # Add to the list
            t3 = datetime.combine(t, datetime.strptime(
                stopWorkingTime, '%H:%M:%S').time())   # 7pm, end of the day
            tstart.append(t3)                          # Add to the list
            t4 = t1 + timedelta(days=1)                # midnight, next day
            tstop.append(t4)                           # Add to the list

        else:   # If the day is NOT a working day...
            t1 = datetime.combine(t, datetime.strptime(
                "00:00:00", '%H:%M:%S').time())  # midnight
            tstart.append(t1)                    # Add to the list
            t4 = t1 + timedelta(days=1)          # midnight, next day
            tstop.append(t4)                     # Add to the list

    return tstart, tstop


# ------------------------------------------------------------------------------
# Get free time chunks from a (merged) list of events (tstart and tstop):
# ------------------------------------------------------------------------------
def get_free_time(tstart, tstop):
    logme("Extracting free time intervals from the list of events...")

    Nev = len(tstart)  # Number of events (i.e. number of scheduled events)
    logme("Analyzing " + str(Nev) + " events...")
    # ------------------------------------------------------------------------------
    # Solving the inverse 'merge interval' problem:
    # ------------------------------------------------------------------------------
    logme("Solving the 'merge interval' problem...")
    # Rearraging tstop on the (corresponding) sorted start times
    # Sorting tstop on tstart
    tstop = [t for _, t in sorted(zip(tstart, tstop))]
    tstart = sorted(tstart)                            # Sorting tstart

    # array containing the start time of each event (merged)
    merged_tstart = []
    merged_tstop = []   # array containing the stop time of each event (merged)

    for i in range(Nev):
        if i == 0:
            merged_tstart.append(tstart[i])
            merged_tstop.append(tstop[i])
        else:
            if tstart[i] <= merged_tstop[-1]:
                merged_tstart[-1] = min(merged_tstart[-1], tstart[i])
                merged_tstop[-1] = max(merged_tstop[-1], tstop[i])
            else:
                merged_tstart.append(tstart[i])
                merged_tstop.append(tstop[i])

    mNev = len(merged_tstart)
    logme(str(Nev) + " events merged into " + str(mNev) + " events!")

    # ------------------------------------------------------------------------------
    logme("Deriving the free slots now...")

    free_tstart = []  # array containing the start time of free time intervals
    free_tstop = []   # array containing the stop time of free time intervals
    duration = []     # array containing the duration of each free time interval

    # By construction, I only return free time slot that are in the future and
    # not in the past (day), or at least in the present.
    t0 = datetime.now()

    # Calculating the free time intervals (managing special case of "right now")
    for i in range(mNev-1):
        if t0 >= merged_tstop[i] and t0 <= merged_tstart[i+1]:
            free_tstart.append(t0)
            free_tstop.append(merged_tstart[i+1])
        elif t0 >= merged_tstop[i] and t0 >= merged_tstart[i+1]:
            continue  # Skip the iteration of the loop, 'cause it's in the past
        else:
            free_tstart.append(merged_tstop[i])
            free_tstop.append(merged_tstart[i+1])
        T = free_tstop[-1] - free_tstart[-1]
        duration.append(T.total_seconds()/60)

    # fNev = len(free_tstart)
    # logme(str(fNev) + " chunks of free-time found, over the next " +
    #       str(Ndays) + " days.")

    # for i in range(fNev):
    #     free_t = free_tstart[i].strftime("%a %d %b %H:%M")
    #     logme("Free time chunk of " +
    #           str(duration[i]) + " min on\t " + free_t)

    # t0 = datetime.now()
    # epochtime = int(t0.timestamp())

    return free_tstart, free_tstop, duration


# ------------------------------------------------------------------------------
# Rotate anything slice-able (as a ring buffer):
# Taken from: https://stackoverflow.com/questions/50839765
# ------------------------------------------------------------------------------
def rotate(l, y=1):
    if len(l) == 0:
        return l
    y = -y % len(l)     # flip rotation direction
    return l[y:] + l[:y]


# ------------------------------------------------------------------------------
# Schedule and event on a calendar:
# ------------------------------------------------------------------------------
def schedule_iCal(cal, title, starttime, endtime, location, notes, URL, alarm, email):
    t1 = starttime.strftime("%d/%m/%Y %H:%M:%S")
    t2 = endtime.strftime("%d/%m/%Y %H:%M:%S")

    with open("tmp.scpt", "w") as file:
        file.write('tell application "Calendar"\n')
        file.write('tell calendar "' + cal + '"\n')
        file.write('set newEvent to make new event with properties {summary:"' + title +
                   '", start date:date "' + t1 + '", end date:date "' + t2 + '", location:"' +
                   location + '", URL:"' + URL + '", description:"' + notes + '"}\n')

        if email != '':
            file.write('tell newEvent\n')
            file.write(
                'make new attendee at end of attendees with properties {email:"' + email + '"}\n')
            file.write('end tell\n')

        file.write(
            'make new sound alarm at end of sound alarms of newEvent with properties {trigger interval:' + alarm + ', sound name:"Basso"}\n')
        file.write('end tell\n')
        file.write('show newEvent\n')
        file.write('end tell\n')
        file.write('return newEvent\n')

    cmd = "osascript tmp.scpt"
    P = subprocess.run(cmd, shell=True, capture_output=True)
    stdout = P.stdout.decode("utf-8")
    P = subprocess.run("rm ./tmp.scpt", shell=True, capture_output=True)
    return stdout


# ------------------------------------------------------------------------------
# Display the list of events (for debugging):
# ------------------------------------------------------------------------------
def display_intervals(tstart, tstop):
    for i in range(len(tstart)):
        t1 = tstart[i].strftime("%a %d %b %H:%M")
        t2 = tstop[i].strftime("%a %d %b %H:%M")
        print(t1 + " - " + t2)


# ------------------------------------------------------------------------------
# Ask the user to answer a question:
# ------------------------------------------------------------------------------
def query_yes_no(question):
    sys.stdout.write(question)
    # raw_input returns the empty string for "enter"
    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}

    answered = False

    while not answered:
        choice = input().lower()
        if choice in yes:
            answered = True
            return True
        elif choice in no:
            answered = True
            return False
        else:
            answered = False
            sys.stdout.write("Please respond with 'yes'(default) or 'no': ")
