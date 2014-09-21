#!/usr/bin/env python

import pandas as pd
import numpy as np

stats = ['def_int','def_int_long','def_int_td','def_int_yds','fga','fgm','fumbles_forced','fumbles_rec','fumbles_rec_td','fumbles_rec_yds','kick_ret','kick_ret_long','kick_ret_td','kick_ret_yds','kick_ret_yds_per_ret','pass_att','pass_cmp','pass_int','pass_long','pass_td','pass_yds','punt','punt_long','punt_ret','punt_ret_long','punt_ret_td','punt_ret_yds','punt_ret_yds_per_ret','punt_yds','punt_yds_per_punt','rec','rec_long','rec_td','rec_yds','rush_att','rush_long','rush_td','rush_yds','sacks','score_1st','score_2nd','score_3rd','score_4th','score_final','xpa','xpm']

data = pd.read_csv('db.csv')
stat_vectors = data[stats].fillna(0).values
