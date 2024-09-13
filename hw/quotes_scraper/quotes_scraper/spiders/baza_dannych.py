import json
from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017/')
db = client['quotes_db']
quotes_collection = db['quotes']
authors_collection = db['authors']

with open('quotes.json', 'r', encoding='utf-8') as file:
    quotes_data = json.load(file)
    quotes_collection.insert_many(quotes_data)


with open('authors.json', 'r', encoding='utf-8') as file:
    authors_data = json.load(file)
    authors_collection.insert_many(authors_data)