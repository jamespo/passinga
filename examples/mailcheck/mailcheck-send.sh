#!/bin/bash

TO=$1
FROM=$2
EPOCH=$(date +%s)
SUBJECT="JPMAILCHECK $EPOCH"

swaks -S --to $TO --from $FROM --header "Subject: $SUBJECT" --server localhost
