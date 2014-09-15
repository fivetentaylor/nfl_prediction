#!/usr/bin/env python

import csv
import sys
import ipdb

reader = csv.reader(open('boxscores.csv'), delimiter=',')

for rec in reader:
	print rec[int(sys.argv[1])]
