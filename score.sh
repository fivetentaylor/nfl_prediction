#!/bin/bash

#20120101,SFO,STL,-5,11
#20120101,STL,SFO,5,-11
#20120101,TAM,ATL,-11,2
#20120101,ATL,TAM,11,-2
#20120101,TEN,HOU,-1,-36

input=${1:-/dev/stdin}
cat $input | awk -F, '{
	if($4 * $5 > 0)
		print 1;
	else
		print 0;
}' | h
