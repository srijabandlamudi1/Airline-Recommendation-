import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
from sklearn.ensemble import RandomForestClassifier



def process(source,destination,r1,r2,r3,r4,r5,r6):
	# ensure the dates are parsed correctly with parse_dates argument
	reviews = pd.read_csv("scraped_reviews.csv", parse_dates = ["date_of_review", "date_flown"])
	#print(reviews.head(5))
	reviews=reviews.fillna(0)

	#print("Percentage of missing values for each column: \n")
	#print((reviews.isna().sum()/reviews.shape[0])*100)

	#print(reviews)
	
	#index = pd.Index(reviews["source"])
	#print(index)
	#print(index.value_counts())

	#index = pd.Index(reviews["destination"])
	#print(index)
	#print(index.value_counts())
	
	#rslt_df = reviews[reviews['source'] == "Singapore"]
	#print(rslt_df)


	#index = pd.Index(rslt_df["destination"])
	#print(index)
	#print(index.value_counts())

	#rslt_df1 = rslt_df[rslt_df['destination'] == "Bangkok"]
	#print(rslt_df1)

	#rslt_df2 = rslt_df1[rslt_df1['recommendation'] == "yes"]
	#print(rslt_df2)
	#source="Singapore"
	#destination="Bangkok"
	rslt=reviews[(reviews['source'] == source) & (reviews['destination'] == destination) & (reviews['recommendation'] == "yes")]
	
	x_dataset=rslt.drop(columns=['title','review_value','reviewer_name','date_of_review','review_text','aircraft','traveller_type','seat_type','route','date_flown','recommendation','source','destination','airlines'])
	y=rslt['airlines']

	#print(x_dataset)
	#print(y)

	x_train, x_test, y_train, y_test = train_test_split(x_dataset, y, test_size=0.2, random_state=42)

	model = RandomForestClassifier(max_depth=50, random_state=0,n_estimators=25)
	model.fit(x_train,y_train)

	y_pred=model.predict(x_test)
	print(y_pred)
	print(y_test)
	
	new_x=[float(r1),float(r2),float(r3),float(r4),float(r5),float(r6)]
	new_x=np.asarray(new_x).reshape(1, -1)
	y_pred=model.predict(new_x)
	print(y_pred)
	rec=y_pred[0]
	#print(y)
	y_value=[]
	for i in y:
		#print(i)
		if i != rec:
			if i not in y_value:
				y_value.append(i)
	print(y_value)			
	return rec,y_value

#r=process("Melbourne","Tokyo",4,4,4,4,4,4)