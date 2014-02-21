#!/bin/bash

cat ./lines/nfl20* > tmp
join -t, -11 -24 <(cat teams.csv | sort -t, -k1,1) <(cat tmp | sort -t, -k4,4) > tmp2
join -t, -11 -24 <(cat teams.csv | sort -t, -k1,1) <(cat tmp2 | sort -t, -k4,4) > tmp3

cat tmp3 | cut -d, -f2,4,5,6,7,8 | awk -F, '{
	split($3, d, "/");
	date = d[3] d[1] d[2];
	printf("%s,%s,%s,%s,%s,%s,%d.0\n", date, $1, $2, $4, $5, $6, (($4 + $6) > $5));
}' | sort -t, -k1,1 > tmp4
cat <(echo 'date,vis,hom,vis_score,hom_score,line,tag') tmp4 > lines.csv
rm tmp*

