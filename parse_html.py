#!/usr/bin/env python

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import re
import csv
import sys
from dateutil.parser import parse

# select only columns with all non-null data
# out.loc[np.all(pd.notnull(out),axis=0)]

def parse_table(html, home_id, visitor_id):
	t = re.sub('<colgroup.*</colgroup>', '', re.sub('\n', '', html))
	header = []
	soup = BeautifulSoup(t)
	for tag in soup.find_all('thead')[0].find_all('th'):
		if tag.has_attr('data-stat') and not re.match('^header|player|team|^$', tag['data-stat']):
			header.append(tag['data-stat'])
			
	t = re.sub('<colgroup.*</thead>', '', re.sub('\n', '', html))
	df = pd.read_html(t, header=None)[0]
	teams = df[df[0].notnull()][1].unique()

	#visitor = df[df[1] == teams[0]].iloc[:,2:].fillna(0).astype(float)
	visitor = df[df[1] == visitor_id].iloc[:,2:].fillna(0).astype(float)
	if len(visitor):
		visitor.columns = header
		visitor = pd.DataFrame(visitor.sum()).T
	else:
		visitor = pd.DataFrame(np.zeros(len(header))).T
		visitor.columns = header

	#home = df[df[1] == teams[1]].iloc[:,2:].fillna(0).astype(float)
	home = df[df[1] == home_id].iloc[:,2:].fillna(0).astype(float)
	if len(home):
		home.columns = header
		home = pd.DataFrame(home.sum()).T
	else:
		home = pd.DataFrame(np.zeros(len(header))).T
		home.columns = header

	return visitor, home

def parse_game_info(html):
	soup = BeautifulSoup(html)

	game_info = {x.text.strip():y.text.strip() for x,y in zip(soup.findAll('td')[0::2], soup.findAll('td')[1::2])}

	if 'Attendance' in game_info:
		game_info['Attendance'] = int(game_info['Attendance'].replace(',',''))

	'''
	weather = dict(zip(['temp','humidity','wind','wind_chill'],
		[x.strip() for x in game_info['Weather'].split(',')]))

	if 'temp' in weather:
		weather['temp'] = weather['temp'].split()[0]
	if 'wind_chill' in weather:
		weather['wind_chill'] = weather['wind_chill'].split()[0]
	if 'humidity' in weather:
		weather['humidity'] = weather['humidity'].split()[-1][:-1]
	if 'wind' in weather:
		weather['wind'] = weather['wind'].split()[2]
	del game_info['Weather']

	game_info.update(weather)
	'''

	return game_info

def parse_linescore(html):
	soup = BeautifulSoup(html)
	ids = [x.attrs['href'].split('/')[2].upper() for x in soup.findAll('a')]

	tbl = [x.text for x in soup.findAll('td')]

	header = ['score_1st','score_2nd','score_3rd','score_4th','score_final']
	if len(tbl) == 14:
		header.insert(4,'score_ot')

	mid = len(tbl)/2

	v = dict(zip(header, [int(x) for x in tbl[1:mid]]))
	rec,team = [x[::-1] for x in tbl[0][::-1].split(' ', 1)]
	v['team'] = team
	v['id'] = ids[0]
	v['id_opp'] = ids[1]
	v.update(dict(zip(['wins','losses','ties'], [int(x) for x in rec[1:-1].split('-')])))

	h = dict(zip(header, [int(x) for x in tbl[mid+1:]]))
	rec,team = [x[::-1] for x in tbl[mid][::-1].split(' ', 1)]
	h['team'] = team
	h['id'] = ids[1]
	h['id_opp'] = ids[0]
	h.update(dict(zip(['wins','losses','ties'], [int(x) for x in rec[1:-1].split('-')])))

	return v, h

	
def main():
	reader = csv.DictReader(open('boxscores.csv'))
	#reader = csv.DictReader(open('error.csv'))
	out = []

	# ['week', 'scoring', 'skill_stats', 'title', 'game_info', 'def_stats', 'team_stats', 'url', 'linescore', 'kick_stats']
	for rec in reader:
		try:
			match, date = rec['title'].split(r'|')[0].split(r'-')
			date = parse(date)
			day = date.strftime('%d')
			month = date.strftime('%m')
			year = date.strftime('%Y')
			match = [x.strip() for x in match.split(' at ')]

			soup = BeautifulSoup(rec['scoring'])
			ids2 = [x.text for x in soup.findAll('th') if x.text]

			visitor = {	'host':False, 
						'name':match[0], 
						'day': day,
						'month': month,
						'year': year,
						'week': int(rec['week'].split()[-1]),
						'url': rec['url'],
						'id2': ids2[0],
						'id2_opp': ids2[1]
						}

			home = {	'host':True, 
						'name':match[1], 
						'day': day,
						'month': month,
						'year': year,
						'week': int(rec['week'].split()[-1]),
						'url': rec['url'],
						'id2': ids2[1],
						'id2_opp': ids2[0]
						}

			v,h = parse_linescore(rec['linescore'])
			visitor.update(v)
			home.update(h)

			for i in ['def_stats','skill_stats','kick_stats']:
				v,h = parse_table(rec[i], home['id'], visitor['id'])
				visitor.update({k:v[0] for k,v in v.to_dict().iteritems()})
				home.update({k:v[0] for k,v in h.to_dict().iteritems()})

			game_info = parse_game_info(rec['game_info'])

			home.update(game_info)
			visitor.update(game_info)

		except:
			sys.stderr.write('Failed to parse: %s on %s\n' % (' at '.join(match), date))
			sys.stderr.write('url: %s\n' % (rec['url']))
			exc_info = sys.exc_info()
			sys.stderr.write('message: %s at line %d\n' % (exc_info[1], exc_info[2].tb_lineno))
			continue

		out.append(home)
		out.append(visitor)

	return pd.DataFrame(out)

if __name__ == '__main__':
	out = main()
	out.to_csv('db.csv', index=False)



