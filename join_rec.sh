#!/bin/bash

join -t, -11 -2103 <(cat rec.csv | sort -t, -k1,1) <(cat data.csv | sort -t, -k103,103) | sort -r > data2.csv
