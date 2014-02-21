#!/usr/bin/env python

import pandas as pd
import numpy as np
import re
import ipdb

from sklearn.cross_validation import cross_val_score
#from sklearn.ensemble import AdaBoostClassifier
from sklearn import linear_model

df = pd.read_csv('./data2.csv').sort('date', ascending=False)
df = df.dropna(axis=1)
df.index = np.arange(len(df.index))[::-1]
#df.iloc[:5,:8].T.to_dict().values()

data = []
target = []
floats = df.dtypes == float

for i, rec in df.iterrows():
	j = i
	#tag = int((rec['hom_final'] - rec['vis_final']) > 0)

	tag = rec['tag']
	line = rec['line']
	rec10yr = rec['rec']
	home, home_rec = rec['home'], None
	vis, vis_rec = rec['visitor'], None
	while j > 0 and ((home_rec is None) or (vis_rec is None)):
		j -= 1
		r = df.loc[j]
		if vis_rec is None: 
			if r['home'] == vis:
				vis_rec = np.array([x[1] for x in r[floats].iteritems() if re.match('^hom', x[0])]) - np.array([x[1] for x in r[floats].iteritems() if re.match('^vis', x[0])])
			elif r['visitor'] == vis:
				vis_rec = np.array([x[1] for x in r[floats].iteritems() if re.match('^vis', x[0])]) - np.array([x[1] for x in r[floats].iteritems() if re.match('^hom', x[0])])
		if home_rec is None:
			if r['home'] == home:
				home_rec = np.array([x[1] for x in r[floats].iteritems() if re.match('^hom', x[0])]) - np.array([x[1] for x in r[floats].iteritems() if re.match('^vis', x[0])])
			elif r['visitor'] == home:
				home_rec = np.array([x[1] for x in r[floats].iteritems() if re.match('^vis', x[0])]) - np.array([x[1] for x in r[floats].iteritems() if re.match('^hom', x[0])])
	if not home_rec is None and not vis_rec is None:
		#ipdb.set_trace()
		target.append(tag)
		data.append(list(np.concatenate((home_rec, vis_rec))) + [line,rec10yr])

data = np.array(data)
target = np.array(target)

clf = linear_model.LogisticRegression()
print cross_val_score(clf, data, target)

#df = pd.DataFrame(data, index=None)
#df.to_csv('training')
		
		

