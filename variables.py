#!/usr/bin/env python

import pandas as pd
import numpy as np
import networkx as nx
import itertools as it

stats = ['def_int','def_int_long','def_int_td','def_int_yds','fga','fgm','fumbles_forced','fumbles_rec','fumbles_rec_td','fumbles_rec_yds','kick_ret','kick_ret_long','kick_ret_td','kick_ret_yds','kick_ret_yds_per_ret','pass_att','pass_cmp','pass_int','pass_long','pass_td','pass_yds','punt','punt_long','punt_ret','punt_ret_long','punt_ret_td','punt_ret_yds','punt_ret_yds_per_ret','punt_yds','punt_yds_per_punt','rec','rec_long','rec_td','rec_yds','rush_att','rush_long','rush_td','rush_yds','sacks','score_1st','score_2nd','score_3rd','score_4th','score_final','xpa','xpm']

data = pd.read_csv('db.csv')
data['game_id'] = data['url'].factorize()[0]

def build_graph(data, pred=lambda x: True):
	G = nx.MultiDiGraph()
	G.add_nodes_from(data.id2.unique())
	itty = data[data.apply(pred, axis=1)][['id2','id2_opp','year','week','host']].itertuples()
	stat_vectors = data[data.apply(pred, axis=1)][stats].fillna(0).itertuples()
	def edge(x,y):
		return (x[1], x[2], {'year':x[3], 'week':x[4], 'host':x[5], 'stats':np.array(y)})
	G.add_edges_from([edge(*x) for x in it.izip(itty, stat_vectors)])
	return G

def game_attributes(home, visitor, year, week):
	pass

def prevN(week, N=3):
	return [((week - x) % 16) + 1 for x in xrange(2,2+N)]

def prevX(year, week, N=5):
	return [(year + ((week - x) / 16), ((week - x) % 16) + 1) for x in xrange(2,2+N)]

def gameFilter(year, week):
	last_weeks = set(prevX(year, week, N=5))
	def pred(rec):
		#return (rec.year == year) and (rec.week in last3)
		return (rec.year, rec.week) in last_weeks
	return pred
	
graph = build_graph(data, gameFilter(2010, 4))

def N_shortest(graph, home, visitor, N=5):
	return sorted(list(nx.all_simple_paths(graph, home, visitor, N)), cmp=lambda x,y: len(x) - len(y))

def stat(graph,x,y):
	a = np.mean([z['stats'] for z in graph.edge[x][y].itervalues()], axis=0)
	b = np.mean([z['stats'] for z in graph.edge[y][x].itervalues()], axis=0)
	#return graph.edge[x][y][0]['stats'] - graph.edge[y][x][0]['stats']
	return a - b

def getSpread(host, spread):
	if spread == 'Pick':
		return 0
	s,t = [x[::-1] for x in spread[::-1].split(' ', 1)]
	return float(s) if t == host else -float(s)

def train(data, year, week, hist=16):
	train, target, spread = [], [], []
	for y,w in prevX(year,week,hist):
		games = data[(data.year == y) & (data.week == w)]
		graph = build_graph(data, gameFilter(y, w))
		for h,v in games[data.host == True][['id2','id2_opp']].itertuples(False):
			h = games[games.id2 == h]
			v = games[games.id2 == v]
			h_final = h.score_final.iloc[0]
			v_final = v.score_final.iloc[0]
			target.append(v_final - h_final)
			spread.append(getSpread(h.name.iloc[0], h['Vegas Line'].iloc[0]))
			
			top3 = N_shortest(graph, h.id2.iloc[0], v.id2.iloc[0], N=5)[:3]
			if not len(top3):
				raise Exception('Match %s vs %s had no paths' % (h,v))

			vect = []
			for path in top3:
				for m in zip(path[:-1], path[1:]):
					vect.append(stat(graph,*m))
			train.append(np.mean(vect, axis=0))
	return { 'data': np.array(train),
			 'target': np.array(target),
			 'spread': np.array(spread) }

def test(data, year, week):
	test, target, spread = [], [], []
	games = data[(data.year == year) & (data.week == week)]
	graph = build_graph(data, gameFilter(year, week))
	for h,v in games[data.host == True][['id2','id2_opp']].itertuples(False):
		h = games[games.id2 == h]
		v = games[games.id2 == v]
		h_final = h.score_final.iloc[0]
		v_final = v.score_final.iloc[0]
		target.append(v_final - h_final)
		spread.append(getSpread(h.name.iloc[0], h['Vegas Line'].iloc[0]))

		top3 = N_shortest(graph, h.id2.iloc[0], v.id2.iloc[0], N=5)[:3]
		if not len(top3):
			raise Exception('Match %s vs %s had no paths' % (h,v))

		vect = []
		for path in top3:
			for m in zip(path[:-1], path[1:]):
				vect.append(stat(graph,*m))
		test.append(np.mean(vect, axis=0))
	return { 'data': np.array(test),
			 'target': np.array(target),
			 'spread': np.array(spread) }

def classificationPerf(pred, actual, spread):
	for p,a,s in zip(pred, actual, spread):
		pass

train = train(data, 2013, 10)
test = test(data, 2013, 11)

from sklearn import ensemble
model = ensemble.RandomForestRegressor()
model.fit(train['data'], train['target'])
model.predict(test['data'])




