#!/bin/bash

#1	date
#52	home
#103	visitor

#1	date
#2	vis
#3	hom
#4	vis_score
#5	hom_score
#6	line
#7	tag

join -t, -11 -21 <(tail -n +2 vars.csv | awk -F, '{printf("%s%s%s,%s\n", $1, $103, $52, $0)}' | sort -t, -k1,1) \
	<(tail -n +2 lines.csv | awk -F, '{printf("%s%s%s,%s,%s\n", $1, $2, $3, $6, $7)}' | sort -t, -k1,1) | \
	cut -d, -f2-106 > tmp

cat <(head -1 vars.csv | tr -d '\n') <(echo ',line,tag') tmp > data.csv
rm tmp
