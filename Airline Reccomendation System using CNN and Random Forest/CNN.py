import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score

from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.layers import Embedding
from keras.layers import Conv1D, GlobalMaxPooling1D

def build_model():
    model_conv = Sequential()
    model_conv.add(Embedding(100, 100, input_length=50))
    model_conv.add(Dropout(0.2))
    model_conv.add(Conv1D(64, 5, activation='relu'))
    model_conv.add(MaxPooling1D(pool_size=4))
    model_conv.add(LSTM(100))
    model_conv.add(Dense(1, activation='sigmoid'))
    model_conv.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model_conv 


def process():
	# ensure the dates are parsed correctly with parse_dates argument
	reviews = pd.read_csv("scraped_reviews.csv", parse_dates = ["date_of_review", "date_flown"])
	print(reviews.head(5))
	reviews=reviews.fillna(0)

	print("Percentage of missing values for each column: \n")
	print((reviews.isna().sum()/reviews.shape[0])*100)

	x_dataset=reviews.drop(columns=['title', 'reviewer_name','date_of_review','review_text','aircraft','traveller_type','seat_type','route','date_flown','recommendation','source','destination','airlines'])
	#reviews['recommendation'] = pd.Categorical(reviews.recommendation)
	reviews['recommendation'] = reviews['recommendation'].replace(['no','yes'],[0,1])
	y=reviews['recommendation']
	print(x_dataset)



	max_features = 5000
	maxlen = 13772
	batch_size = 32
	embedding_dims = 50
	filters = 250
	kernel_size = 3
	hidden_dims = 250
	epochs = 3

	
	
	
	x_train, x_test, y_train, y_test = train_test_split(x_dataset, y, test_size=0.2, random_state=42)


	print('Build model...')
	model = Sequential()

	model.add(Embedding(max_features,embedding_dims,input_length=maxlen))
	model.add(Conv1D(filters,kernel_size,padding='valid',activation='relu',strides=1))
	# we use max pooling:
	model.add(GlobalMaxPooling1D())

	# We add a vanilla hidden layer:
	model.add(Dense(hidden_dims))
	model.add(Dropout(0.2))
	model.add(Activation('relu'))
	
	# We project onto a single unit output layer, and squash it with a sigmoid:
	model.add(Dense(1))
	model.add(Activation('sigmoid'))

	model.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy'])
	history = model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_data=(x_test, y_test))

	pred=model.predict(x_test)
	y_pred=[]
	for i in pred:
		#print(i[0])
		if i[0]>0.5:
			y_pred.append(1)
		else:
			y_pred.append(0)
			
	mse=mean_squared_error(y_test, y_pred)
	mae=mean_absolute_error(y_test, y_pred)
	r2=r2_score(y_test, y_pred)
	
	
	print("---------------------------------------------------------")
	print("MSE VALUE FOR CNN IS %f "  % mse)
	print("MAE VALUE FOR CNN IS %f "  % mae)
	print("R-SQUARED VALUE FOR CNN IS %f "  % r2)
	rms = np.sqrt(mean_squared_error(y_test, y_pred))
	print("RMSE VALUE FOR CNN IS %f "  % rms)
	ac=accuracy_score(y_test,y_pred)
	print ("ACCURACY VALUE CNN IS %f" % ac)
	print("---------------------------------------------------------")

	
	acc = [mse,mae,r2,rms,ac]
	alc = ["MSE","MAE","R-SQUARED","RMSE","ACCURACY"]
	colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#8c564b"]
	explode = (0.1, 0, 0, 0, 0)  
		
	fig = plt.figure()
	plt.bar(alc, acc,color=colors)
	plt.xlabel('Parameter')
	plt.ylabel('Value')
	plt.title('CNN Metrics Value')
	plt.savefig('static/results/CNNMetricsValue.png') 
	#plt.show()

	
	#print(history.history.keys())
	# summarize history for accuracy
	fig = plt.figure()
	plt.plot(history.history['accuracy'])
	plt.plot(history.history['val_accuracy'])
	plt.title('model accuracy')
	plt.ylabel('accuracy')
	plt.xlabel('epoch')
	plt.legend(['train', 'test'], loc='upper left')
	plt.savefig('static/results/CNNAccuracy.png') 
	#plt.show()
	
	
	# summarize history for loss
	fig = plt.figure()
	plt.plot(history.history['loss'])
	plt.plot(history.history['val_loss'])
	plt.title('model loss')
	plt.ylabel('loss')
	plt.xlabel('epoch')
	plt.legend(['train', 'test'], loc='upper left')
	plt.savefig('static/results/CNNLoss.png') 
	#plt.show()
		
	
