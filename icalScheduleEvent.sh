#!/usr/bin/env bash #
# iCal Schedule an event
# -=-=-=-=-=-=-=-=-=-=-=
#
# 16 Jan 2021 - Michele Giugliano
#

#
# e.g. icalScheduleEvent.sh fix 1610892000 1610894700 "this is a test"
#

if [ $# -eq 0 ]
  then
	  echo 'USAGE: icalScheduleEvent.sh calendarName startEvent stopEvent (both as Epoch dates) "eventTitle" (within double quotes)'
    exit
fi
#clear

calendar=$1
startt=$2
stopt=$3
title=$4

loc=SISSA
URL="http://0.0.0.0:5678/tasks/pending"
notes="taskWarrior integration"
alarmMinutesBefore=-34

startEventDate=$(date -jf %s $startt '+%d/%m/%Y %H:%M:%S')
stopEventDate=$(date -jf %s $stopt '+%d/%m/%Y %H:%M:%S')

cmd1=$(eval echo 'tell application \"Calendar\"')
cmd2=$(eval echo 'tell calendar \"$calendar\"')
cmd3=$(eval echo 'set newEvent to make new event with properties {summary:\"$title\", start date:date \"$startEventDate\", end date:date \"$stopEventDate\", location:\"$loc\", URL:\"$URL\", description:\"$notes\"}')
cmd4=$(eval echo 'make new sound alarm at end of sound alarms of newEvent with properties {trigger interval:$alarmMinutesBefore, sound name:\"Basso\"}')
cmd5=$(eval echo 'end tell')
cmd6=$(eval echo 'end tell')
cmd7=$(eval echo 'return newEvent')

cmd1=$(echo "'$cmd1'")
cmd2=$(echo "'$cmd2'")
cmd3=$(echo "'$cmd3'")
cmd4=$(echo "'$cmd4'")
cmd5=$(echo "'$cmd5'")
cmd6=$(echo "'$cmd6'")
cmd7=$(echo "'$cmd7'")

output=$(eval osascript -e $cmd1 -e $cmd2 -e $cmd3 -e $cmd4 -e $cmd5 -e $cmd6 -e $cmd7)
eventID=$(echo $output | awk '{print $3}')
#calID=$(echo $output | awk '{print $7}')
#echo $eventID $calID
echo $eventID
