#!/usr/bin/env python

import ipdb
import sys
from sets import Set
from collections import deque

graph = {} # opp, score = sum

def rank(team1, team2, graph):
	q = deque([[team1]])
	visited = Set([team1])
	paths = []
	depth = [sys.maxint]
	def rec_graph():
		#ipdb.set_trace()
		if len(q):
			path = q.popleft()
			if len(path) <= depth[0]:
				for team,score in graph[path[-1]].iteritems():
					if not team in visited:
						tmp = path + [team]
						if team == team2:
							depth[0] = len(path)
							#depth[0] = len(tmp)
							paths.append(tmp)
						else:
							visited.add(team)
							q.append(tmp)
			rec_graph()
	rec_graph()
	total = 0
	for p in paths:
		for i in range(len(p)-1):
			total += graph[p[i]][p[i+1]]
	#print '%s : %s' % (team1, graph[team1])
	#print '%s : %s' % (team2, graph[team2])
	#print paths
	#if len(paths) > 1:
	#	ipdb.set_trace()
	#return sum([sum(y.values()) [p for p in paths])
	return total

filein = '/dev/stdin' if len(sys.argv) < 2 else sys.argv[1]

i = 0
first = ''
for line in open(filein):
	line = line.strip()
	rec = line.split(',')
	t1,t2,w = rec[1:]

	if i == 0: 
		first = int(rec[0])
	if (int(rec[0]) - first) > 20:
		#ipdb.set_trace()
		print '%s,%d' % (line, rank(t1, t2, graph))
		#print '%s,%d' % (line, rank(t2, t1, graph))

	if t1 in graph:
		if t2 in graph[t1]:
			graph[t1][t2] += int(w)
		else:
			graph[t1][t2] = int(w)
	else:
		graph[t1] = {t2 : int(w)}
	i += 1






