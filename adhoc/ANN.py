import tensorflow as tf
import sqlite3
import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split
from create_pre_match_tables import get_ANN_odds
conn = sqlite3.connect('/Users/carljonsson/Python/hockeystats/hockeystats.db')
c = conn.cursor()


#Train data

c.execute("SELECT OFF_SCORE_HOME, DEF_SCORE_HOME, OFF_SCORE_AWAY, DEF_SCORE_AWAY, OUTCOME1X2, OUTCOME45 FROM ANN_TABLE WHERE GAMEDATE > ? AND SEASONID < ?",['2015-10-15',2019])
train_data = pd.DataFrame(c.fetchall())

train_data.columns = ('OSH','DSH','OSA','DSA','OUT1X2','OUT45')

train_data['OUT1X2'].apply(int)
train_data['OUT45'].apply(int)

x = train_data[train_data.columns[0:4]]
y = train_data[train_data.columns[4]]


#Test data

c.execute("SELECT OFF_SCORE_HOME, DEF_SCORE_HOME, OFF_SCORE_AWAY, DEF_SCORE_AWAY, OUTCOME1X2, OUTCOME45 FROM ANN_TABLE WHERE GAMEDATE > ? AND SEASONID = ?",['2015-10-15',2019])
test_data = pd.DataFrame(c.fetchall())

test_data.columns = ('OSH','DSH','OSA','DSA','OUT1X2','OUT45')

test_data['OUT1X2'].apply(int)
test_data['OUT45'].apply(int)

x_test = test_data[train_data.columns[0:4]]
y_test = test_data[train_data.columns[4]]


#Create test and train datasets

feat_cols = []

for col in x.columns:
    feat_cols.append(tf.feature_column.numeric_column(col))

#Create input function
input_func = tf.estimator.inputs.pandas_input_fn(x=x,y=y,batch_size=20,num_epochs=20000,shuffle=True)

#Create estimator
classifier = tf.estimator.DNNClassifier(hidden_units = [8,10,8],n_classes=3,feature_columns=feat_cols)

classifier.train(input_fn=input_func,steps=5)

pred_fn = tf.estimator.inputs.pandas_input_fn(x=x_test, batch_size=len(x_test),shuffle=False)
predictions = list(classifier.predict(input_fn=pred_fn))

final_preds = []

for pred in predictions:
    final_preds.append(pred['class_ids'][0])

print(predictions)


print(pred)



update = 1
