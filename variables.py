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
	G.add_nodes_from(data.id.unique())
	itty = data[data.apply(pred, axis=1)][['id','id_opp','year','week','host']].itertuples()
	stat_vectors = data[data.apply(pred, axis=1)][stats].fillna(0).itertuples()
	def edge(x,y):
		return (x[1], x[2], {'year':x[3], 'week':x[4], 'host':x[5], 'stats':np.array(y)})
	G.add_edges_from([edge(*x) for x in it.izip(itty, stat_vectors)])
	return G

def game_attributes(home, visitor, year, week):
	pass

def prevN(week, N=3):
	return [((week - x) % 16) + 1 for x in xrange(2,2+N)]

def gameFilter(year, week):
	def pred(rec):
		last3 = prevN(week, N=3)
		return (rec.year == year) and (rec.week in last3)
	return pred
	
graph = build_graph(data, gameFilter(2010, 4))

def N_shortest(graph, home, visitor, N=5):
	return sorted(list(nx.all_simple_paths(graph, home, visitor, N)), cmp=lambda x,y: len(x) - len(y))




