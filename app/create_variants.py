import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Load environment variables from .env file
load_dotenv()

# Fetch the API key from the environment variable
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv('API_KEY')
)

messages = [{"role": "system", "content": "Please return the given json object with different variants of the hints"
                                          "Append number 'Variant1' to the query name."
                                          "Each following hint, needs to be started with the last hint."
                                          "Keep the same style of language, and don't use too complex language."
                                          "Make also the sentences in the hints shorter, to get only the relevant information."
             }]

with open('example.json', 'r') as file:
    messages.append({"role": "user", "content": file.read()})
    chat = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",  # Check OpenAI documentation for the latest model
        messages=messages
    )
    reply = chat.choices[0].message.content
    print(f"{reply}")