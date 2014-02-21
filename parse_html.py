#!/usr/bin/env python

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import re
import csv
import ipdb
import sys

# select only columns with all non-null data
# out.loc[np.all(pd.notnull(out),axis=0)]

def parse_table(html):
	t = re.sub('<colgroup.*</thead>', '', re.sub('\n', '', html))
	header = []
	soup = BeautifulSoup(t)
	for tag in soup.find_all('th'):
		if tag.has_attr('data-stat') and not re.match('^header|player|team|^$', tag['data-stat']):
			header.append(tag['data-stat'])
			
	df = pd.read_html(t, infer_types=False, header=None)[0]
	teams = df[df[0] != ""][1].unique()

	visitor = df[df[1] == teams[0]].iloc[:,2:].replace(to_replace='', value='0').astype(float)
	visitor.columns = ['vis_' + x for x in header]
	visitor = pd.DataFrame(visitor.sum()).T

	home = df[df[1] == teams[1]].iloc[:,2:].replace(to_replace='', value='0').astype(float)
	home.columns = ['hom_' + x for x in header]
	home = pd.DataFrame(home.sum()).T

	return teams, pd.merge(home, visitor, how='outer', right_index=True, left_index=True)

def parse_game(html):
	pass

def parse_line(html):
	line = ['wins','losses','ties','1st','2nd','3rd','4th','final']
	line_ot = ['wins','losses','ties','1st','2nd','3rd','4th','ot','final']

	df = pd.read_html(html, infer_types=False, header=0)[0]

	record = [float(x) for x in re.findall('\([0-9\-]*\)', df.iloc[0,0])[0][1:-1].split('-')]
	record += [float(x) for x in df.iloc[0,1:]]
	visitor = pd.DataFrame(record).T
	#ipdb.set_trace()
	if len(visitor.columns) == 8:
		visitor.columns = ['vis_' + x for x in line]
	else:
		visitor.columns = ['vis_' + x for x in line_ot]

	record = [float(x) for x in re.findall('\([0-9\-]*\)', df.iloc[1,0])[0][1:-1].split('-')]
	record += [float(x) for x in df.iloc[1,1:]]
	home = pd.DataFrame(record).T
	#ipdb.set_trace()
	if len(home.columns) == 8:
		home.columns = ['hom_' + x for x in line]
	else:
		home.columns = ['hom_' + x for x in line_ot]
	#ipdb.set_trace()

	return pd.merge(home, visitor, how='outer', right_index=True, left_index=True)

def parse_team(html):
	pass

counts = []
reader = csv.reader(open('boxscore.csv'))
header = reader.next()
out = pd.DataFrame()

rec = reader.next()
for rec in reader:
	# ['scoring', 'kick_stats', 'skill_stats', 'title', 'game_info', 'def_stats', 'team_stats', 'url', 'linescore']
	try:
		teams, defense = parse_table(rec[5])
		teams, offense = parse_table(rec[2])
		teams, kick = parse_table(rec[1])
		line = parse_line(rec[8])
	except:
		print rec[3]
		print kick
		continue

	tmp = pd.merge(pd.merge(pd.merge(defense, offense, how='outer', right_index=True, left_index=True), kick, how='outer', right_index=True, left_index=True), line, how='outer', right_index=True, left_index=True)

	tmp['date'] = pd.datetools.parse(rec[3].split('-')[1].strip()).strftime('%Y%m%d')
	tmp['visitor'] = teams[0]
	tmp['home'] = teams[1]

	out = out.append(tmp)

out.to_csv('vars.csv', index=False)



