import unittest
import final_project
import json
import requests
import sqlite3

class TestBooks(unittest.TestCase):
	def testGooglebooks(self):
		books = final_project.get_googlebooks_titles("Grimm")
		
		self.assertEqual(len(books), 40)
		self.assertEqual(type(books), list)
		self.assertEqual(type(books[0]), dict)
		self.assertIsNot(books,[])
		self.assertNotEqual(type(books), None)

class TestReviews(unittest.TestCase):
	def testreviews(self):
		books = final_project.get_googlebooks_titles("Grimm")
		reviews = final_project.get_goodreads_reviews(books[0])
		arts = final_project.get_nyt_articles("Grimm")

		self.assertGreater(len(str(reviews)),0)
		self.assertNotEqual(type(reviews), dict)
		self.assertNotEqual(type(reviews), list)
		self.assertNotEqual(len(arts),0)
		self.assertEqual(type(arts), dict)

class TestDatabase(unittest.TestCase):
	def testdatabase(self):
		conn = sqlite3.connect('books.db')   
		cur = conn.cursor() 
		statement = "SELECT count(Books.Title), ISBN, Title FROM Books"
		data = []
		cur.execute(statement)
		for each in cur:
			data.append(each)

		statement2 = 'SELECT count(*), ISBN FROM Goodread_Reviews'
		cur.execute(statement2)
		for each in cur:
			data.append(each)


		self.assertEqual(data[0][0], 40)
		self.assertEqual(type(data[0][1]), int)
		self.assertEqual(type(data[0][2]), str)
		self.assertEqual(data[1][0], 40)
		self.assertEqual(type(data[1][1]),int)

unittest.main()