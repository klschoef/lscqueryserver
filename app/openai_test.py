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

# Initial system message
#messages = [{"role": "system", "content": "You are Elliot Alderson from Mr. Robot. You are exactly that role. Don't break out of your role. You are no AI Assistent, you are this role."}]
#messages = [{"role": "system", "content": "Please return 5 variants of the given sentences in a json string array. "
#                                          "Keep the same style of language, and don't use too complex language. "
#                                          "Make also the sentences shorter, to get only the relevant information."}]
messages = [{"role": "system", "content": "Please return 5 variants of the given json object (5 json objects in total). The anwers needs to be the same, just change the hints."
                                          "Just append -Variant{number} to the query name."
                                          "return 5 new json objects with the changed hints. Each with 6 hints like the given one."
                                          "Each following hint, needs to be started with the last hint."
                                          "Keep the same style of language, and don't use too complex language."
                                          "Make also the sentences in the hints shorter, to get only the relevant information."
                                          "Don't forget to rewrite the hints to get the same context, but with other structure and words."
                                            "Don't forget to create 5 new objects."}]

with open('example.json', 'r') as file:
    messages.append({"role": "user", "content": file.read()})
    chat = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",  # Check OpenAI documentation for the latest model
        messages=messages
    )
    reply = chat.choices[0].message.content
    print(f"Answer: {reply}")
    messages.append({"role": "assistant", "content": reply})

while True:
    message = input("You: ")
    if message:
        messages.append({"role": "user", "content": message})
        chat = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",  # Check OpenAI documentation for the latest model
            messages=messages
        )
        reply = chat.choices[0].message.content
        print(f"Answer: {reply}")
        messages.append({"role": "assistant", "content": reply})
