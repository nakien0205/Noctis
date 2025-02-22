from ollama import chat
import assist_mes
import requests
import trafilatura
from bs4 import BeautifulSoup
from ollama import ChatResponse

def query_generator():
    # Use the latest user prompt from the conversation.
    last_user_prompt = 'who is the president of the US in 2025'


    assist_mes.query['content'] += last_user_prompt
    response: ChatResponse = chat(
        model="llama3.2:3b",
        messages=[{
            'role': 'user',
            'content': assist_mes.query['content']
        }]
    )
    query_result = response.message.content
    assist_mes.query['content'] = assist_mes.query['content'].replace(last_user_prompt, "")
    print(f"Generated query: {query_result}")
    return query_result

def search_or_not(user_input):
    assist_mes.search_or_not['content'] += user_input
    response: ChatResponse = chat(model='llama3.2:3b', messages=[
        {
            'role': 'user',
            'content': assist_mes.search_or_not['content'],
        },
    ])
    content = response.message.content
    assist_mes.search_or_not['content'] = assist_mes.search_or_not['content'].replace(user_input, "")

    print(f"Search or not: {content}")


m = [1]
print(m[-1])
# who is the president of the US in 2024
# will there be an olympic in 2025
# who is the best League of Legends player in 2025
# search for the price of the monitor Philips 24M2N3200S 24-inch on Google