#!/usr/bin/env bash #
# iCal Remove an event
# -=-=-=-=-=-=-=-=-=-=-=
#

if [ $# -eq 0 ]
  then
	  echo 'USAGE: icalRemoveEvent.sh eventID calendar_name'
    exit
fi
#clear

eventID=$1
calID=$2

cmd1=$(eval echo 'tell application \"Calendar\"')
cmd2=$(eval echo 'tell calendar \"$calID\"')
cmd3=$(eval echo 'set theEvent to first event whose uid = \"$eventID\"')
cmd4=$(eval echo 'delete theEvent')
cmd5=$(eval echo 'end tell')
cmd6=$(eval echo 'end tell')

cmd1=$(echo "'$cmd1'")
cmd2=$(echo "'$cmd2'")
cmd3=$(echo "'$cmd3'")
cmd4=$(echo "'$cmd4'")
cmd5=$(echo "'$cmd5'")
cmd6=$(echo "'$cmd6'")

eval osascript -e $cmd1 -e $cmd2 -e $cmd3 -e $cmd4 -e $cmd5 -e $cmd6
