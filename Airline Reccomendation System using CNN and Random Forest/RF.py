import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
from sklearn.ensemble import RandomForestClassifier



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

	
	x_train, x_test, y_train, y_test = train_test_split(x_dataset, y, test_size=0.2, random_state=42)

	model = RandomForestClassifier(max_depth=50, random_state=0,n_estimators=25)
	model.fit(x_train,y_train)

	y_pred=model.predict(x_test)


	mse=mean_squared_error(y_test, y_pred)
	mae=mean_absolute_error(y_test, y_pred)
	r2=r2_score(y_test, y_pred)
	
	
	print("---------------------------------------------------------")
	print("MSE VALUE FOR RF IS %f "  % mse)
	print("MAE VALUE FOR RF IS %f "  % mae)
	print("R-SQUARED VALUE FOR RF IS %f "  % r2)
	rms = np.sqrt(mean_squared_error(y_test, y_pred))
	print("RMSE VALUE FOR RF IS %f "  % rms)
	ac=accuracy_score(y_test,y_pred)
	print ("ACCURACY VALUE RF IS %f" % ac)
	print("---------------------------------------------------------")

	
	acc = [mse,mae,r2,rms,ac]
	alc = ["MSE","MAE","R-SQUARED","RMSE","ACCURACY"]
	colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#8c564b"]
	explode = (0.1, 0, 0, 0, 0)  
		
	fig = plt.figure()
	plt.bar(alc, acc,color=colors)
	plt.xlabel('Parameter')
	plt.ylabel('Value')
	plt.title('Random Forest Metrics Value')
	plt.savefig('static/results/RFMetricsValue.png') 
	#plt.show()


