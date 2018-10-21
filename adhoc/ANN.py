import tensorflow as tf
import sqlite3
import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split
conn = sqlite3.connect('/Users/carljonsson/Python/hockeystats/hockeystats.db')
c = conn.cursor()

#hello = tf.constant('Hello world')
#print(type(hello))
#x = tf.constant(100)
#print(type(x))

#sess = tf.Session()

#print(sess.run(x))

#z1 = tf.placeholder(tf.int32)
#z2 = tf.placeholder(tf.int32)

#add = tf.add(z1+z2)

c.execute("SELECT HWPT, AWPT, HSCORE, ASCORE, CASE WHEN OUT1 = 1 THEN 0 WHEN OUT2 = 1 THEN 1 ELSE 2 END AS OUTCOME FROM OUTCOME_PREDICTER")
train_data = pd.DataFrame(c.fetchall())
#print(type(train_data))


train_data.columns = ('x0','x1','x2','x3','y')

train_data['y'].apply(int)

x = train_data[train_data.columns[0:4]]

y = train_data[train_data.columns[4]]

print(x)
print(y)


#Create test and train datasets

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.3)

print(y_test)

feat_cols = []




for col in x.columns:
    feat_cols.append(tf.feature_column.numeric_column(col))

#Create input function
input_func = tf.estimator.inputs.pandas_input_fn(x=x_train,y=y_train,batch_size=10,num_epochs=5,shuffle=True)

#Create estimator
classifier = tf.estimator.DNNClassifier(hidden_units = [4,5],n_classes=3,feature_columns=feat_cols)

classifier.train(input_fn=input_func,steps=5)

pred_fn = tf.estimator.inputs.pandas_input_fn(x=x_test, batch_size=len(x_test),shuffle=False)
predictions = list(classifier.predict(input_fn=pred_fn))

final_preds = []

for pred in predictions:
    final_preds.append(pred['class_ids'][0])

print(predictions)



print(pred)

