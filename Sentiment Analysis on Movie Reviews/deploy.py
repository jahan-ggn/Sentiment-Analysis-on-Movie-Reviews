from flask import Flask
from googlesearch import search 
import requests
from urllib.request import urlopen
import bs4
import re
import nltk
from textblob import TextBlob
from flask import jsonify
import json

app = Flask(__name__)

@app.route('/get-verdict/<movie_name>')
def get_verdict(movie_name):
    url = movie_name + " imdb review"
    counter = 0
    frequency = []
    for link in search(url, tld="co.in", num=1, start=0, stop=1, pause=2.0): 
        review_page_url = link + "reviews?ref_=tt_urv"
        try:
            user_review = urlopen(review_page_url)
        except:
            print(url + " not worked")
        soup = bs4.BeautifulSoup(user_review, 'lxml')
        for i in soup.find_all('a', class_ = 'title'): 
            if(counter < 25):
                result = cleaning(i.text)
                result = result.lower()
                obj = TextBlob(result)
                sentiment = round(obj.sentiment.polarity, 3)
                frequency.append(assign_sentiment(sentiment))
            else:
                break
        ++counter
        frequency = calculate_outlier_points(frequency)
        rating = int(calculate_average(frequency));
        verdict = give_verdict(rating)
        director = get_director(url)
        release_date = get_release_date(url)
        genres = get_genres(url)
        image_url = get_image_url(url)
        json_data =  { "image_url": image_url, "genre": genres, "director": director, "release_date": release_date, "rating": rating, "verdict": verdict }
    return jsonify(json_data)

def get_genres(url):
    for link in search(url, tld="co.in", num=1, start=0, stop=1, pause=2.0): 
        review_page_url = link + "?ref_=ttrel_rel_tt"
        try:
            user_review = urlopen(review_page_url)
        except:
            print(url + " not worked")
        soup = bs4.BeautifulSoup(user_review, 'lxml')
        for genre in soup.find_all('div', class_ = 'subtext'):
            for i in genre('a', class_ = None):
                genres = i.text
                return genres

def assign_sentiment(sentiment):
    if(sentiment >= -1 and sentiment < -0.8):
        return 1
    elif(sentiment >= -0.8 and sentiment < -0.6):
        return 2
    elif(sentiment >= -0.6 and sentiment < -0.4):
        return 3
    elif(sentiment >= -0.4 and sentiment < -0.2):
        return 4
    elif(sentiment >= -0.2 and sentiment < 0):
        return 5
    elif(sentiment >= 0.0 and sentiment < 0.2):
        return 6
    elif(sentiment >= 0.2 and sentiment < 0.4):
        return 7
    elif(sentiment >= 0.4 and sentiment < 0.6):
        return 8
    elif(sentiment >= 0.6 and sentiment < 0.8):
        return 9
    elif(sentiment >=0.8 and sentiment <= 1):
        return 10

def calculate_outlier_points(frequency):
    frequency_copy = frequency.copy()
    frequency.sort()
    if(len(frequency) % 2 == 1):
        Q1 = frequency[int(((len(frequency) + 1) / 4))]
        Q3 = frequency[int(((len(frequency) + 1) * 0.75)) - 1]
        difference = Q3 - Q1
        maxV = int(Q3 + 1.5 * difference)
        minV = int(Q1 - 1.5 * difference)
    else:
        Q1 = int((frequency[int(((len(frequency) - 1) / 4))] + frequency[int(((len(frequency) - 1) / 4)) + 1]) / 2)
        Q3 = int((frequency[int(((len(frequency) - 1) * 0.75))] + frequency[int(((len(frequency) - 1) * 0.75)) + 1]) / 2)
        difference = Q3 - Q1
        maxV = int(Q3 + 1.5 * difference)
        minV = int(Q1 - 1.5 * difference)
    average = int(calculate_average(frequency))
    for q in range(1, len(frequency)):
        if(frequency_copy[q] < minV or frequency_copy[q] > maxV):
            frequency_copy[q] = average
    return frequency_copy

def calculate_average(frequency):
    average = round((sum(frequency) / len(frequency)), 3)
    return average

def give_verdict(verdict):
    if(verdict == 10):
        return "Blockbuster"
    elif (verdict == 9):
        return "Super Duper Hit"
    elif (verdict == 8):
        return "Super Hit"
    elif (verdict == 7):
        return "Semi Hit"
    elif (verdict == 6):
        return "Hit"
    elif (verdict == 5):
        return "Above Average"
    elif (verdict == 4):
        return "Average"
    elif (verdict == 3):
        return "Below Average"
    elif (verdict == 2):
        return "Flop"
    elif (verdict == 1):
        return "Disaster"

def get_director(url):
    for link in search(url, tld="co.in", num=1, start=0, stop=1, pause=2.0): 
        cast_page_url = link + "fullcredits?ref_=tt_cl_sm#cast"
        try:
            cast = urlopen(cast_page_url)
        except:
            print(url + " not worked")
        soup = bs4.BeautifulSoup(cast, 'lxml')
        cast = soup.findAll('td', class_ = "name")
        cast = cast[0].find('a')
        director = cleaning(cast.text)
        return director

def get_release_date(url):
    cCounter = 0
    dCounter = 0
    release_date = None
    for link in search(url, tld="co.in", num=1, start=0, stop=1, pause=2.0): 
        review_page_url = link + "releaseinfo?ref_=tt_ov_inf"
        try:
          user_review = urlopen(review_page_url)
        except:
          print(url + " not worked")
        soup = bs4.BeautifulSoup(user_review, 'lxml')
        for date in soup.find_all('tr', class_ = "ipl-zebra-list__item release-date-item"):
            for i in date('td', class_ = "release-date-item__country-name"):
                country = str(i.text)
                country = country.replace('\n', '')
                if(country == "India"):
                    break
                cCounter += 1
            for i in date('td', class_ = "release-date-item__date"):
                if(dCounter != cCounter):
                    dCounter += 1
                else:
                    release_date = i.text
                    break
    if(release_date == None):
      release_date = "-"
    return release_date

def cleaning(result):
    result = re.sub("'", '', result)
    result = re.sub(r'[^\w]', ' ', result)
    result = re.sub(r'\d', ' ', result)
    result = re.sub(r'^\s+','', result)
    result = re.sub(r'\s+$', '', result)
    return result
def get_image_url(url):
    for link in search(url, tld="co.in", num=1, start=0, stop=1, pause=2.0): 
        review_page_url = link + "?ref_=fn_tt_tt_1"
        user_review = urlopen(review_page_url)
        soup = bs4.BeautifulSoup(user_review, 'lxml')
        for banner in soup.find_all('div', class_ = 'poster'):
            for b in banner('img', class_ = None):
                return (b["src"])

if __name__ == '__main__':
    app.run(host='0.0.0.0')
