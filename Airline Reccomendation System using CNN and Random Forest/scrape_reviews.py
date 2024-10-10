import pandas as pd
import time
import argparse
import sys

# scraping
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import os
import pandas as pd

def process(airlinesname):
    reviews_url = sneaky_request("https://www.airlinequality.com/airline-reviews/"+airlinesname+"/")
    if reviews_url.reason != "OK":
        sys.exit()
    sys.stdout.write("Accessed URL: {} \nStatus: {}\n".format(reviews_url.geturl(), reviews_url.reason))
    sys.stdout.flush()
    gw_reviews = BeautifulSoup(reviews_url.read(), features = "lxml")

    reviews = []
    keep_going = True
    while keep_going:
        if len(reviews) == 0:
            reviews = gw_reviews.find_all("article", {"itemprop" : "review"})
        else:
            for review in gw_reviews.find_all("article", {"itemprop" : "review"}):
                reviews.append(review)
        try:
            next_page = gw_reviews.find("a", string = ">>")["href"]
            next_page_url = "https://www.airlinequality.com" + next_page
        except:
            keep_going = False
        time.sleep(float(5))
        reviews_url = sneaky_request(next_page_url)
        gw_reviews = BeautifulSoup(reviews_url.read(), features = "lxml")
    parsed_reviews = {
        "title" : [],
        "review_value" : [],
        #"n_user_reviews" : [],
        "reviewer_name" : [],
        #"reviewer_country" : [],
        "date_of_review" : [],
        "review_text" : [],
        "aircraft" :[],
        "traveller_type" : [],
        "seat_type" : [],
        "route" : [],
        "date_flown" : [],
        "seat_comfort_rating" : [],
        "cabin_staff_service_rating" : [],
        "food_and_beverages_rating" : [],
        "inflight_entertainment_rating" : [],
        "ground_service_rating" : [],
        "value_for_money_rating" : [],
        "recommendation" : []
    }
    for review in reviews:
        # extract review title
        review_title = review.find("h2", {"class" : "text_header"})
        parsed_reviews["title"].append(safe_extract(review_title))

        # extract review value out of 10
        review_value = review.find("span", {"itemprop" : "ratingValue"})

        # if there is no value out of 10, enter None instead using `safe_extract`
        parsed_reviews["review_value"].append(safe_extract(review_value))

        # extract number of reviews by the reviewer
        #n_reviews = review.find("span", {"class" : "userStatusReviewCount"})
        #parsed_reviews["n_user_reviews"].append(safe_extract(n_reviews))

        # extract the reviewer
        reviewer_name = review.find("span", {"itemprop" : "name"})
        parsed_reviews["reviewer_name"].append(safe_extract(reviewer_name))

        # extract the country of the reviewer
        #reviewer_country = review.find("h3", {"class" : "text_sub_header userStatusWrapper"})
        #parsed_reviews["reviewer_country"].append(safe_extract(reviewer_country))

        # extract the date of the review
        date_of_review = review.find("time", {"itemprop" : "datePublished"})
        parsed_reviews["date_of_review"].append(safe_extract(date_of_review))

        # extract the review text
        review_text = review.find("div", {"class" : "text_content"})
        parsed_reviews["review_text"].append(safe_extract(review_text))

        # extract the aircraft
        # there are multiple td with class = "review-value"
        # so we need to find the sibling header for aircraft then find it's sibling
        # in order to find the aircraft type.  Use sibling_extract for this
        aircraft = review.find("td", {"class" : "review-rating-header aircraft"})
        aircraft_value = sibling_extract(aircraft)
        parsed_reviews["aircraft"].append(aircraft_value)

        # extract the type of traveller
        traveller_type = review.find("td", {"class" : "review-rating-header type_of_traveller"})
        traveller_type_value = sibling_extract(traveller_type)
        parsed_reviews["traveller_type"].append(traveller_type_value)

        # extract seat type
        seat_type = review.find("td", {"class" : "review-rating-header cabin_flown"})
        seat_type_value = sibling_extract(seat_type)
        parsed_reviews["seat_type"].append(seat_type_value)

        # extract the route
        route = review.find("td", {"class" : "review-rating-header route"})
        route_value = sibling_extract(route)
        parsed_reviews["route"].append(route_value)

        # extract the date flown
        date_flown = review.find("td", {"class" : "review-rating-header date_flown"})
        date_flown_value = sibling_extract(date_flown)
        parsed_reviews["date_flown"].append(date_flown_value)

        # extract the seat comfort rating out of 5
        # need to find the sibling in order to narrow down the number of stars for
        # seat comfort or other ratings.  use star_extract to do this for us
        seat_comfort_rating = review.find("td", {"class" : "review-rating-header seat_comfort"})
        parsed_reviews["seat_comfort_rating"].append(star_extract(seat_comfort_rating))

        # extract the cabin staff service rating out of 5
        cabin_staff_service_rating = review.find("td", {"class" : "review-rating-header cabin_staff_service"})
        parsed_reviews["cabin_staff_service_rating"].append(star_extract(cabin_staff_service_rating))

        # extract the food and beverages rating out of 5
        food_and_beverages_rating = review.find("td", {"class" : "review-rating-header food_and_beverages"})
        parsed_reviews["food_and_beverages_rating"].append(star_extract(food_and_beverages_rating))

        # extract the inflight entertainment rating out of 5
        inflight_entertainment_rating = review.find("td", {"class" : "review-rating-header inflight_entertainment"})
        parsed_reviews["inflight_entertainment_rating"].append(star_extract(inflight_entertainment_rating))

        # extract the ground service rating out of 5
        ground_service_rating = review.find("td", {"class" : "review-rating-header ground_service"})
        parsed_reviews["ground_service_rating"].append(star_extract(ground_service_rating))

        # extract the value for money rating out of 5
        value_for_money_rating = review.find("td", {"class" : "review-rating-header value_for_money"})
        parsed_reviews["value_for_money_rating"].append(star_extract(value_for_money_rating))

        # extract if the review recommended Germanwings or not
        recommendation = review.find("td", {"class" : "review-rating-header recommended"}).find_next("td")
        parsed_reviews["recommendation"].append(recommendation.text)

        # Now that all information is parsed, convert to a pandas dataframe
        # and save as a csv.

    print(parsed_reviews)

    parsed_reviews_df = pd.DataFrame(parsed_reviews)
    #print(parsed_reviews_df)
    return parsed_reviews_df
    #parsed_reviews_df.to_csv("data/scraped_reviews.csv", index = False)

def sneaky_request(url):
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        open_url = urlopen(req)
    except HTTPError as error:
        sys.stdout.write("Error code: ", error.code)
        sys.stdout.write("The reason for the exception:", error.reason)
        sys.stdout.flush()

    return open_url

def safe_extract(extracted_tag, replacement_value = None):
    try:
        value = extracted_tag.text
    except:
        value = replacement_value
    return value

def sibling_extract(extracted_tag, next_tag = "td", replacement_value = None):
    try:
        value = extracted_tag.find_next(next_tag).text
    except:
        value = None
    return value

def star_extract(extracted_tag, next_tag = "td", replacement_value = None):
    try:
        filled_star_tags = extracted_tag.find_next(next_tag).find_all("span", {"class" : "star fill"})
        value = len(filled_star_tags)
    except:
        value = None
    return value


def getReview():
	#airlines=["ana-all-nippon-airways","asiana-airlines","cathay-pacific-airways","eva-air","garuda-indonesia","hainan-airlines","japan-airlines","lufthansa","qatar-airways","singapore-airlines"]
	airlines=["japan-airlines"]

	for i in airlines:	
		df=process(i)
		df.to_csv("data/scraped_"+i+"_reviews.csv", index = False)
	
	arr = os.listdir("data")
	dfnew = pd.DataFrame()
	for file in arr:
		df1 = pd.read_csv("data/"+file, parse_dates = ["date_of_review", "date_flown"])
		dfnew=pd.concat([dfnew, df1], axis=0)
    
	dfnew.to_csv("scraped_reviews.csv", index = False)
    
	arr = os.listdir("data")
	dfnew = pd.DataFrame()
	for file in arr:
		f=file.split("_")
		print(f[1])
		f1=f[1].replace("-"," ")
		airlines=[]
		source=[]
		dest=[]
		df1 = pd.read_csv("data/"+file, parse_dates = ["date_of_review", "date_flown"])
		for route in df1["route"]:
			try:
				s=route.split(" to ")
				if len(s)>1:
					#print(s)
					#print("Source",s[0])
					source.append(s[0])
					d=s[1].split("via")
					#print("Dest",d[0])
					dest.append(d[0])
					airlines.append(f1)
				else:
					source.append("-")
					dest.append("-")
					airlines.append(f1)
					
			except:
				#print(route)
				source.append("-")
				dest.append("-")
				airlines.append(f1)
		print(len(df1))
		print(len(source))
		print(len(dest))
		df1["source"]=source
		df1["destination"]=dest
		df1["airlines"]=airlines
		df1=df1.dropna()
		dfnew=pd.concat([dfnew, df1], axis=0)
	    
	dfnew.to_csv("scraped_reviews.csv", index = False)
    
