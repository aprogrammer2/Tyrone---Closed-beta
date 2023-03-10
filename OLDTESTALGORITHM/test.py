import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
df = pd.read_csv('TESTDATA.csv')
X= df.iloc[:,1:14]
Y= df.iloc[:,1] 
best_features= SelectKBest(score_func=chi2, k=3)
fit= best_features.fit(X,Y)
df_scores= pd.DataFrame(fit.scores_)
df_columns= pd.DataFrame(X.columns)
features_scores= pd.concat([df_columns, df_scores], axis=1)
features_scores.columns= ['Features', 'Score']
features_scores.sort_values(by = 'Score')
print(features_scores)