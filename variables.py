#!/usr/bin/env python

import ipdb
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

#train_1 = train(data, 2013, 10)
#test_1 = test(data, 2013, 11)

from sklearn import ensemble
from sklearn import linear_model
#model_1 = ensemble.RandomForestRegressor()
#model_1 = linear_model.LinearRegression()
#model_1.fit(train_1['data'], train_1['target'])
#model_1.predict(test_1['data'])

def teamRank(graph, N=15, func=np.mean, debug=True):
	# initialize the node rank
	for team in graph.nodes():
		graph.node[team]['rank'] = graph.node[team].get('rank', {})
		game_stats = []
		for t,o in graph.edges([team]):
			for td,od in zip(graph.edge[t][o].values(), graph.edge[o][t].values()):
				game_stats.append(td['stats'] - od['stats'])
		graph.node[team]['rank'][func.__name__] = func(game_stats, axis=0)

	# iterate the node rank N times
	for i in xrange(N):
		for team in graph.nodes():
			rank_stats = []
			for t,o in graph.edges([team]):
				a = func([x['stats'] for x in graph.edge[t][o].values()], axis=0)
				rank_stats.append((a - graph.node[o]['rank'][func.__name__]) / 2)
			graph.node[team]['rank'][func.__name__] = func(rank_stats, axis=0)
			#graph.node[team][i+1] = func(rank_stats, axis=0)

	'''
	if debug:
		ipdb.set_trace()
		for k,v in graph.node['SDG'].iteritems():
			print '%d: %s' % (k,v)

	for team in graph.nodes():
		graph.node[team]['rank'] = graph.node[team][N]
	'''
		
	
def trainTeamRank(data, year, week, hist=64):
	train, target, spread, names = [], [], [], []
	for y,w in prevX(year,week,hist):
		games = data[(data.year == y) & (data.week == w)]
		graph = build_graph(data, gameFilter(y, w))
		teamRank(graph, func=np.max)
		teamRank(graph, func=np.min)
		teamRank(graph, func=np.median)
		#teamRank(graph, func=np.mean)
		for h,v in games[data.host == True][['id2','id2_opp']].itertuples(False):
			H = games[games.id2 == h]
			V = games[games.id2 == v]
			h_final = H.score_final.iloc[0]
			v_final = V.score_final.iloc[0]
			target.append(v_final - h_final)
			names.append(H.name.iloc[0])
			spread.append(getSpread(names[-1], H['Vegas Line'].iloc[0]))
			#ipdb.set_trace()
			train.append(np.hstack(it.chain(graph.node[h]['rank'].itervalues(), graph.node[v]['rank'].itervalues())))
	return { 'home': names,
			 'data': np.array(train),
			 'target': np.array(target),
			 'spread': np.array(spread) }

def testTeamRank(data, year, week):
	test, target, spread, names = [], [], [], []
	games = data[(data.year == year) & (data.week == week)]
	graph = build_graph(data, gameFilter(year, week))
	teamRank(graph, func=np.max)
	teamRank(graph, func=np.min)
	teamRank(graph, func=np.median)
	#teamRank(graph, func=np.mean)
	for h,v in games[data.host == True][['id2','id2_opp']].itertuples(False):
		H = games[games.id2 == h]
		V = games[games.id2 == v]
		h_final = H.score_final.iloc[0]
		v_final = V.score_final.iloc[0]
		target.append(v_final - h_final)
		names.append(H.name.iloc[0])
		spread.append(getSpread(names[-1], H['Vegas Line'].iloc[0]))
		#test.append(np.hstack([graph.node[h]['rank'], graph.node[v]['rank']]))
		#ipdb.set_trace()
		test.append(np.hstack(it.chain(graph.node[h]['rank'].itervalues(), graph.node[v]['rank'].itervalues())))

	return { 'home': names,
			 'data': np.array(test),
			 'target': np.array(target),
			 'spread': np.array(spread) }

'''
train_2 = trainTeamRank(data, 2014, 4)
test_2 = testTeamRank(data, 2014, 5)

model_2 = ensemble.RandomForestRegressor()
model_2 = linear_model.LinearRegression()
model_2.fit(train_2['data'], train_2['target'])
model_2.predict(test_2['data'])
'''

for year, week in prevX(2014, 5, 24)[::-1]:
	train = None
	if week > 1:
		train = trainTeamRank(data, year, week-1)
	else:
		train = trainTeamRank(data, year-1, 16)
	test = testTeamRank(data, year, week)
	model = linear_model.LinearRegression()
	model.fit(train['data'], train['target'])
	correct = []
	for p,t,s in zip(model.predict(test['data']), test['target'], test['spread']):
		correct.append(((p-s) > 0) == ((t-s) > 0))
	print '%d-%d %f correct' % (year, week, sum(correct) / float(len(correct)))
		





