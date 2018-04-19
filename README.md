
This project uses data from the Google Books API, scraping the Goodreads website, and the New York Times API. 
This program requires a NYT API Key, saved in a file called "secrets.py" and assignmed to a variable called "nyt-key".
The necessary modules for this program can be found in requirements.txt. 

When run, this program prompt the user to select a type of graph to dislapy precollected data from four provided options, or to create a new database.  

This program uses two classes, Book and Review, which can be found at the beginning of the code. 
It also uses the following functions(listed in the order that they appear in the program): 
get_googlebooks_titles
create_class_book
get_goodreads_reviews
get_nyt_articles
create_class_article
create_database 

The code begins by collecting data from Googlebooks, Goodreads, and the New York Times.  It organizes this data into a class, and then writes the data to a sqlite database (books.db). It also performs sentiment analysis on the reviews.    
An additional four function are included to create different types of plotly graphs. 
Test cases can be found in the file final_project_test.py. 



