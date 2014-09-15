#!/bin/bash

cat <(echo 'week,scoring,skill_stats,title,game_info,def_stats,team_stats,url,linescore,kick_stats') \
<(cat boxscores.csv | \
	grep -v '^week,scoring,skill_stats,title,game_info,def_stats,team_stats,url,linescore,kick_stats') > tmp
mv tmp boxscores.csv
