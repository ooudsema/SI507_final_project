import requests
import json
import plotly
from bs4 import BeautifulSoup
from secrets import *
import sqlite3
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.graph_objs import *
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

CACHE_FNAME = 'final_project_cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

DBNAME = 'books.db'

#create class
class Book:
	def __init__(self,title, author, publisher, date, isbn, description, page_count, language):
		self.title = title
		self.author = author
		self.publisher = publisher
		self.date = date
		self.isbn = isbn
		self.description = description
		self.page_count = page_count
		self.language = language

	def __str__(self):
		return str(self.title) + " by " + str(self.author) + " (" + str(self.date) + ")"

class Review:
		def __init__(self,url, review_title, reviewer, sentiment, date, abstract):
			self.url = url
			self.review_title = review_title
			self.reviewer = reviewer
			self.sentiment = sentiment
			self.date = date
			self.abstract = abstract

		def __str__(self):
			return str(self.review_title) + " reviewed by " + str(self.reviewer) + " in " + str(self.date) 


def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)



def get_googlebooks_titles(query):
	url = 'https://www.googleapis.com/books/v1/volumes'
	params = {}
	params['q'] = query
	params['maxResults'] = 40
	unique_ident = params_unique_combination(url,params)
	books = []  #list of dictionaries
	if unique_ident in CACHE_DICTION:
		data = CACHE_DICTION[unique_ident]['items']
		for each in data:
			books.append(each['volumeInfo'])  
	else:
		resp = requests.get(url, params).json()
		CACHE_DICTION[unique_ident] = resp
		dumped_json_cache = json.dumps(CACHE_DICTION)
		fw = open(CACHE_FNAME,"w")
		fw.write(dumped_json_cache)
		fw.close() 
		data = CACHE_DICTION[unique_ident]['items']
		for each in data:
			books.append(each['volumeInfo'])  
	return books

def create_class_book(booklst):
	gbooks = [] #list of class instances
	for dict in booklst:
		try:
			isbn1 = dict['industryIdentifiers'][-1]['identifier']
			if ":" in isbn1:
				isbnsplit = isbn.split(':')
				isbn = isbnsplit[-1]
			else:
				isbn = dict['industryIdentifiers'][-1]['identifier']
		except:
			isbn = "" 
		try:
			title = dict['title']
		except:
			title = ""
		try:
			author = dict['authors'][0]
		except:
			author = "" 
		try:
			publisher = dict['publisher']
		except:
			publisher = "" 
		try:
			date = dict['publishedDate']
		except:
			date = "" 
		try:
			description = dict['description']
		except:
			description = "" 
		try: 
			page_count = dict['pageCount']
		except:
			page_count = "" 
		try:
			language = dict['language']
		except:
			language = ""
		gbooks.append(Book(title, author, publisher, date, isbn, description, page_count, language))
	return gbooks


def get_goodreads_reviews(isbn):
	url = 'https://www.goodreads.com/book/isbn/' + str(isbn)
	unique_ident = url
	if unique_ident in CACHE_DICTION:
		page_text = CACHE_DICTION[unique_ident]
		page_soup = BeautifulSoup(page_text, 'html.parser')
		try:
			review = page_soup.find(class_ = "readable stacked").text
		except:
			review = page_soup.find(class_ = "readable stacked")

	else: 
		page_text = requests.get(url).text
		CACHE_DICTION[unique_ident] = page_text
		json_cache = json.dumps(CACHE_DICTION)
		fw = open(CACHE_FNAME,"w")
		fw.write(json_cache)
		fw.close()
		page_soup = BeautifulSoup(page_text, 'html.parser')
		try: 
			review = page_soup.find(class_ = "readable stacked").text
		except:
			review = page_soup.find(class_ = "readable stacked")
	return review


def get_nyt_articles(query):
	url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'
	params = {}
	params['query'] = query  #author or title or isbn
	params['api-key'] = nyt_key
	unique_ident = params_unique_combination(url,params)
	if unique_ident in CACHE_DICTION:
		data = CACHE_DICTION[unique_ident]
	else:
		resp = requests.get(url, params).json()
		CACHE_DICTION[unique_ident] = resp
		dumped_json_cache = json.dumps(CACHE_DICTION)
		fw = open(CACHE_FNAME,"w")
		fw.write(dumped_json_cache)
		fw.close() 
		data = CACHE_DICTION[unique_ident]
	return data

def create_class_article(dictionary_list):
	nytreviews = []
	for each in dictionary_list['response']['docs']:
		try:
			url = each['web_url']
		except:
			url = ""
		try:
			review_title = each['headline']['main']
		except:
			review_title= ""
		try:
			reviewer = each['byline']['person'][0]['firstname'] + " " + each['byline']['person'][0]['lastname']
		except:
			reviewer = "Reviewer Unknown"
		try:
			date = each['pub_date']
		except:
			date = "Date Unknown"
		try: 
			abstract = each['abstract']
		except:
			try: 
				abstract = each['snippet']
			except:
				abstract = ""
		sid = SentimentIntensityAnalyzer()
		try:
			scores = sid.polarity_scores(text = abstract)
			neg = scores['neg']
			pos = scores['pos']
			neu = scores['neu']
			sentiment = scores['compound']
		except: 
			scores = ""
			neg = ""
			pos = ""
			neu = ""
			sentiment = ""
		nytreviews.append(Review(url, review_title, reviewer, sentiment, date, abstract))
	return nytreviews

def create_database(query):
	conn = sqlite3.connect(DBNAME)   
	cur = conn.cursor()
	statement = "DROP TABLE IF EXISTS 'Books'" 
	cur.execute(statement)
	statement1 = "CREATE TABLE Books('Id' INTEGER PRIMARY KEY AUTOINCREMENT, 'ISBN' INTEGER, 'Title' TEXT, 'Author' TEXT, 'Publisher' TEXT, 'PublicationDate' TEXT, 'Description' TEXT, 'Page Count' TEXT, 'Language' TEXT)"
	cur.execute(statement1)
	conn.commit()
	bookdata = get_googlebooks_titles(query)
	gbooks = create_class_book(bookdata)
	for each in gbooks:
		statement2 = "INSERT INTO 'Books' "
		statement2 += "VALUES(?,?,?,?,?,?,?,?,?)"
		insertion = (None, each.isbn, each.title, each.author, each.publisher, each.date, each.description, each.page_count, each.language)
		cur.execute(statement2, insertion)
		conn.commit()
	
	statement = "DROP TABLE IF EXISTS 'Goodread_Reviews'"
	cur.execute(statement)
	statement = "CREATE TABLE Goodread_Reviews('Id' INTEGER PRIMARY KEY AUTOINCREMENT, 'ISBN' INTEGER, 'Review' TEXT, 'Negative' REAL, 'Neutral' REAL, 'Positive' REAL, 'Compound' REAL)"
	cur.execute(statement)
	conn.commit()
	
	for each in gbooks:
		isbn = each.isbn
		reviews = get_goodreads_reviews(isbn)
		sid = SentimentIntensityAnalyzer()
		try:
			scores = sid.polarity_scores(text = reviews)
			neg = scores['neg']
			pos = scores['pos']
			neu = scores['neu']
			total = scores['compound']
		except: 
			scores = None
			neg = None
			pos = None
			neu = None
			total = None
		statement2 = "INSERT INTO 'Goodread_Reviews' "
		statement2 += "VALUES(?,?,?,?,?,?,?)"
		insertion = (None, isbn, reviews, neg, neu, pos, total)
		cur.execute(statement2, insertion)
		conn.commit()

	statement = "DROP TABLE IF EXISTS 'NYT_Reviews'"
	cur.execute(statement)
	statement = "CREATE TABLE NYT_Reviews('Id' INTEGER PRIMARY KEY AUTOINCREMENT, 'Url' TEXT, 'Review_Title' TEXT, 'Reviewer' TEXT, 'SentimentScore' REAL, 'Date' TEXT, 'Abstract' TEXT)"
	cur.execute(statement)
	conn.commit()
	
	nytdata = get_nyt_articles(query)
	nytreviews = create_class_article(nytdata)
	for each in nytreviews:
		statement2 = "INSERT INTO 'NYT_Reviews' "
		statement2 += "VALUES(?,?,?,?,?,?,?)"
		insertion = (None, each.url, each.review_title, each.reviewer, each.sentiment, each.date, each.abstract)
		cur.execute(statement2, insertion)
		conn.commit()

conn = sqlite3.connect('books.db')
cur = conn.cursor()
statement = "SELECT Books.Title, Compound, Goodread_Reviews.ISBN, Books.PublicationDate FROM Books JOIN Goodread_Reviews ON Books.ISBN=Goodread_Reviews.ISBN ORDER BY PublicationDate"
cur.execute(statement)
titles = []
sentiment = []
nytsentiment = []
nyt = []
isbn = []
dates = []
for each in cur:
	titles.append(each[0]) 
	sentiment.append(each[1])
	isbn.append(each[2])
	dates.append(each[3][0:4])
statement2 = "SELECT Date, Review_Title, SentimentScore FROM NYT_Reviews"
cur.execute(statement2)
for each in cur:
	nytsentiment.append(each[2])
	nyt.append(each[1])

def scatter_plot():
	global sentiment, nytsentiment, titles, isbn, nyt
	x = sentiment
	x1 = nytsentiment
	y0 = titles
	y1 = isbn
	y2 = nyt

	# Create traces
	trace0 = go.Scatter(x = y0, y = x, mode = 'markers', name = 'Google Books')
	trace1 = go.Scatter(x = y1, y = x, mode = 'markers', name = 'Goodread Sentiments')
	trace2 = go.Scatter(x = y2, y = x1, mode = 'markers', name = 'NYT Reviews')

	data = [trace0, trace1, trace2]
	py.plot(data, filename='scatter-mode')

def dot_plot():
	global sentiment, nytsentiment, titles, isbn, nyt
	trace1 = {"x": sentiment, "y": titles, "marker": {"color": "pink", "size": 12}, "mode": "markers", "name": "Goodreads Reviews","type": "scatter"}
	trace2 = {"x": nytsentiment, "y": nyt, "marker": {"color": "blue", "size": 12}, "mode": "markers", "name": "NYT Reviews", "type": "scatter"}
	data = Data([trace1, trace2])
	layout = {"title": "Book Reviews", "xaxis": {"title": "Sentiment" }, "yaxis": {"title": "Titles"}}
	fig = Figure(data=data, layout=layout)
	py.plot(fig, filename='basic_dot-plot')


def bar_graph():
	global sentiment, nytsentiment, titles, isbn, nyt
	trace0 = go.Bar(x=titles,y=sentiment,name='Google Books',marker=dict(color='rgb(49,130,189)'))
	trace1 = go.Bar(x=nyt,y=nytsentiment,name='NYT Reviews',marker=dict(color='rgb(204,204,204)'))

	data = [trace0, trace1]
	layout = go.Layout(xaxis=dict(tickangle=-45),barmode='group')

	fig = go.Figure(data=data, layout=layout)
	py.plot(fig, filename='Book Reviews')

def bubble_chart():
	global sentiment, titles, dates
	sents = []
	for each in sentiment:
		if each != None:
			if each < 0:
				each = each*(-1)
			sents.append(each*100)
		else:
			sents.append(0)
	trace0 = go.Scatter(x=dates,y=titles,mode='markers',marker=dict(size=sents))
	data = [trace0]
	py.plot(data, filename='Book Reviews')

inp = ""
while inp != "exit":
	inp = input("bubble chart, bar graph, dot plot, scatter plot\nSelect a graph for displaying book reviews or enter exit to quit: ") 
	if "bubble" in inp:
		bubble_chart()
	elif "bar" in inp:
		bar_graph()
	elif "dot" in inp:
		dot_plot()
	elif "scatter" in inp:
		scatter_plot()
	else:
		print("Not a valid input") 

