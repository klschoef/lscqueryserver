import os
from dotenv import load_dotenv
load_dotenv()

SERVER_PORT = int(os.getenv('SERVER_PORT', "8080"))
GPT_API_KEY = os.getenv('GPT_API_KEY')
MONGO_DB_URL = os.getenv('MONGO_DB_URL', 'mongodb://extreme00.itec.aau.at:27017')
MONGO_DB_DATABASE = os.getenv('MONGO_DB_DATABASE', 'lsc')
SOLR_URL = os.getenv('SOLR_URL', 'http://host.docker.internal:8983/solr')
SOLR_DEFAULT_CORE = os.getenv('SOLR_DEFAULT_CORE', 'mycore')
CLIP_URL = os.getenv('CLIP_URL', 'ws://cloud6.itec.aau.at:8003')

# Optional explicit CLIP/SigLIP2 runtime configs for automatic faiss/model switching.
CLIP_FAISS_FOLDER = os.getenv('CLIP_FAISS_FOLDER')
CLIP_MODEL_NAME = os.getenv('CLIP_MODEL_NAME')
CLIP_WEIGHTS_NAME = os.getenv('CLIP_WEIGHTS_NAME')

SIGLIP2_FAISS_FOLDER = os.getenv('SIGLIP2_FAISS_FOLDER')
SIGLIP2_MODEL_NAME = os.getenv('SIGLIP2_MODEL_NAME')
SIGLIP2_WEIGHTS_NAME = os.getenv('SIGLIP2_WEIGHTS_NAME')

BYPASS_MONGO = os.getenv('BYPASS_MONGO', 'false').lower() in ['1', 'true', 'yes', 'y']
