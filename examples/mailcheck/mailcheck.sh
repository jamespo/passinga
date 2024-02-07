#!/bin/bash

# mailcheck.sh - pipe autoforwarded mail into this (via procmail / imapfilter)

# first match only - hotmail rewrites from, gmail doesn't (so use XFF)
EMAIL=$(perl -ne 'if (/^(?:From:.+<|X-Forwarded-For:) *([^ >]+@[^ >]+)/i) { print $1; exit }' < /dev/stdin)

CHECKNAME="mail_relay_${EMAIL}"

DATE=$(date)

# always assume success
/usr/local/bin/passinga.py -n "$CHECKNAME" -o "Last Update: $DATE" -s 0
