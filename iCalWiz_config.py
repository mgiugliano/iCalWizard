#
# Configuration file
#

# ------------------------------------------------------------------------------
# Daily work schedule: [startWorkingtime ; stopWorkingTime].
# Outside this interval, no free time allocation is allowed.
# Example:
# startWorkingTime = "09:00:00"  # (note the full format: H:M:S)
# stopWorkingTime = "19:00:00"   # (note the full format: H:M:S)

startWorkingTime = "09:00:00"  # (note the full format: H:M:S)
stopWorkingTime = "19:00:00"   # (note the full format: H:M:S)
# ------------------------------------------------------------------------------

# Weekly work schedule, specified in terms of working days.
# Outside these days, no free time allocation is allowed.
# Example:
# workingDays = ["monday", "tuesday", "wednesday", "thursday", "friday"]

workingDays = ["monday", "tuesday", "wednesday", "thursday", "friday"]
# ------------------------------------------------------------------------------

# Switching time (minutes), required between successive (scheduled) events.
# Example:
# swTime = 5   # in minutes

swTime = 5   # in minutes
# ------------------------------------------------------------------------------

# Comma-separated list of iCal calendars to include (escape spaces, if needed)
# Example:
#
inclCals = "fix,Work,Habits,Neuronal\ Dynamics\ Laboratory"
# ------------------------------------------------------------------------------
