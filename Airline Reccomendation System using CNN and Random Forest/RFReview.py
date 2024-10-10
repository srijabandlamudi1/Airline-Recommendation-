import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
from sklearn.ensemble import RandomForestClassifier

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

# Other
import re
import string

def clean_text(text):
    t=text.split("|")
    if len(t)>1:
    	text=t[1]
    else:
    	text=t[0]
    ## Remove puncuation
    text = text.translate(string.punctuation)
    ## Convert words to lower case and split them
    text = text.lower().split()
    ## Remove stop words
    stops = set(stopwords.words("english"))
    text = [w for w in text if not w in stops and len(w) >= 3]
    text = " ".join(text)
    text = text.split()
    stemmer = SnowballStemmer('english')
    stemmed_words = [stemmer.stem(word) for word in text]
    text = " ".join(stemmed_words)
    return text


def process():
	# ensure the dates are parsed correctly with parse_dates argument
	reviews = pd.read_csv("scraped_reviews.csv", parse_dates = ["date_of_review", "date_flown"])
	print(reviews.head(5))
	reviews=reviews.fillna(0)

	print("Percentage of missing values for each column: \n")
	print((reviews.isna().sum()/reviews.shape[0])*100)

	reviews=reviews.drop(columns=['title', 'reviewer_name','aircraft','date_of_review'])
	reviews['recommendation'] = pd.Categorical(reviews.recommendation)
	reviews['recommendation'] = reviews['recommendation'].replace(['no','yes'],[0,1])
	labelencoder = LabelEncoder()
	reviews['seat_type'] = labelencoder.fit_transform(reviews['seat_type'])
	print(reviews)

	reviews['review_text'] = reviews['review_text'].map(lambda x: clean_text(x))
	print(reviews['review_text'])
	
	vectorizer = TfidfVectorizer(use_idf=True)
	x_dataset = vectorizer.fit_transform(reviews['review_text'].values.astype('U')).toarray()
	y = reviews['recommendation'] 
	
	
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
	plt.savefig('static/results/RFReviewMetricsValue.png') 
	#plt.show()

	