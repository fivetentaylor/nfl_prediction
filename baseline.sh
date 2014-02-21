#!/bin/bash

#date,vis,hom,vis_score,hom_score,line,tag
#20000903,ARI,NYG,16,21,6.5,1.0
#20000903,BAL,PIT,16,0,-2.5,1.0
#20000903,CAR,WAS,17,20,10.5,1.0
#20000903,CHI,MIN,27,30,4.5,1.0

tail -n +2 data.csv | cut -d, -f1,103,105 | awk -F, '{if(substr($1,1,4) != "2012")print $2","$3;}' | h | sort -t, -k1,1 | awk '{if((NR+1) % 2) print}' | cut -d, -f1,3 > tmp
cat <(echo 'visitor,rec') <(cat tmp | awk '{print $0".0"}') | sed -E 's/ //g' > rec.csv

tail -n +2 lines.csv | cut -d, -f1,2,3,7 | awk -F, '{if(substr($1,1,4) == "2012")print $2","$3","$4;}' > tmp2
join -t, -12 -21 <(cat tmp2 | sort -t, -k2,2) <(cat tmp | sort -t, -k1,1) | sort -t, -k2,2 |
	join -t, -12 -21 - <(cat tmp | sort -t, -k1,1) | awk -F, '{printf("%s-%d\n", $3, ($4 > $5));}' > tmp3

#rm tmp* 

