import os
from dotenv import load_dotenv
load_dotenv()

SERVER_PORT = int(os.getenv('SERVER_PORT', "8080"))
GPT_API_KEY = os.getenv('GPT_API_KEY')
MONGO_DB_URL = os.getenv('MONGO_DB_URL', 'mongodb://extreme00.itec.aau.at:27017')
MONGO_DB_DATABASE = os.getenv('MONGO_DB_DATABASE', 'lsc')