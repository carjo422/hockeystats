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


#tensor_train_output = train_data[:,28:31]

#print(tensor_train_data.shape)
#print(tensor_train_output.shape)


#OLD CODE

if 1 == 2:

    x = tf.placeholder(tf.float32,shape=[396,28])

    W = tf.Variable(tf.zeros([28,3]))
    b = tf.Variable(tf.zeros([3]))
    y = tf.matmul(x,W) + b
    y_true = tf.placeholder(tf.float32, shape=[396,3])
    cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(labels=y_true,logits=y))
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=1)
    train = optimizer.minimize(cross_entropy)

    init = tf.global_variables_initializer()

    with tf.Session() as sess:
        sess.run(init)

        batch_x = tensor_train_data
        batch_y = tensor_train_output

        sess.run(train,feed_dict={x:batch_x,y_true:batch_y})

        matches = tf.equal(tf.argmax(y,1),tf.argmax(y_true,1))
        acc = tf.reduce_mean(tf.cast(matches,tf.float32))

        print(matches)
        print(acc)

        print(sess.run(acc,feed_dict={x:tensor_train_data, y_true:tensor_train_output}))
