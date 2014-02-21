from sklearn.cross_validation import cross_val_score
from sklearn.datasets import load_iris
from sklearn.ensemble import AdaBoostClassifier

#iris = load_iris()
clf = AdaBoostClassifier(n_estimators=500)
scores = cross_val_score(clf, data, target)
scores.mean() 
