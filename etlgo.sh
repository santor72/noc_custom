#!/bin/bash

/opt/noc/noc etl extract RNUserside
datadir='administrativedomain authprofile managedobjectprofile networksegment networksegmentprofile'
for n1 in $datadir
do
  rm -f /var/lib/noc/import/RNUserside/$n1/archive/*
  cp /var/lib/noc/import/RNUserside/$n1/import.jsonl.gz /var/lib/noc/import/RNUserside/$n1/archive/import-2024-01-01-00-00-00.jsonl.gz
done

