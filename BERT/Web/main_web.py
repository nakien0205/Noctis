import sys

from ollama import chat
import assist_mes
import requests
import trafilatura
from bs4 import BeautifulSoup
from ollama import ChatResponse
from urllib.parse import urlparse, parse_qs, unquote

user_prompt = []
model_answer = []

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
    return "true" in content.lower()

def query_generator():
    # Use the latest user prompt from the conversation.
    last_user_prompt = user_prompt[-1]
    if not last_user_prompt:
        last_user_prompt = "No user prompt provided."

    query_mes = f"Generate a concise search query for this user prompt:\n{last_user_prompt}"

    assist_mes.query['content'] += query_mes
    response: ChatResponse = chat(
        model="llama3.2:3b",
        messages=[{
            'role': 'user',
            'content': assist_mes.query['content']
        }]
    )

    query_result = response.message.content
    query_result = query_result[1:-1]
    assist_mes.query['content'] = assist_mes.query['content'].replace(query_mes, "")

    print(f"Generated query: {query_result}")
    return query_result

def OperaGX(query):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36 OPR/116.0.0.0"
        )
    }
    # url = f"https://www.google.com/search?client=opera-gx&q={query}"
    url = f"https://html.duckduckgo.com/html/?q={query}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    # Adjust the parser logic as needed depending on Google’s HTML structure.
    for idx, result in enumerate(soup.find_all("div", class_="result"), start=0):
        if idx >= 10:
            break
        title_tag = result.find("a", class_="result__a")
        if not title_tag:
            continue
        link = title_tag.get("href")
        snippet = title_tag.text.strip() if title_tag else "No description available"
        results.append({
            "id": idx,
            "link": link,
            "search_description": snippet
        })
        # print(f"id: {results[-1]['id']}")
        # print(f"Search description: {results[-1]['search_description']}")

    return results

def best_search(results, search_query):
    # Use the latest user prompt.
    last_user_prompt = user_prompt[-1]

    if not last_user_prompt:
        last_user_prompt = "No user prompt available."
    best_mes = f"Search results: {results[-1]['search_description']}\nUser prompt: {last_user_prompt}\nSearch query: {search_query}"
    for _ in range(2):
        try:
            assist_mes.best_search['content'] += best_mes
            response: ChatResponse = chat(
                model="llama3.2:3b",
                messages=[{
                    'role': 'user',
                    'content': assist_mes.best_search['content']
                }]
            )
            best_index = int(response.message.content)
            assist_mes.best_search['content'] = assist_mes.best_search['content'].replace(best_mes, "")
            # print(f"Best search result index: {best_index}")

            # print(response)
            return best_index
        except Exception as e:
            # print(f"Error in best_search attempt: {e}")
            continue
    return 0


def extract_target_url(url):
    # If the URL starts with '//', prepend 'https:'
    if url.startswith("//"):
        url = "https:" + url
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    if parsed.path.startswith("/l/") and "uddg" in qs:
        target_url = qs["uddg"][0]
        return unquote(target_url)
    return url


def scrape_webpage(url):
    url = extract_target_url(url)
    print(url)
    try:
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            text_bs = "\n".join([p.get_text(strip=True) for p in paragraphs])

            if text_bs and text_bs.strip():
                print("Method: BeautifulSoup")
                return text_bs, url
    except Exception as e:
        print('2-------------------------2')
        print(f"Error with BeautifulSoup: {e}")
        pass


def contains_needed_data(page_text, search_query):
    last_user_prompt = user_prompt[-1]
    if not last_user_prompt:
        last_user_prompt = "No user prompt available."
    needed_data_mes = f"Page Text: {page_text}\nUser prompt: {last_user_prompt}\nSearch query: {search_query}"

    assist_mes.contains_data['content'] += needed_data_mes
    response: ChatResponse = chat(
        model="llama3.2:3b",
        messages=[{
            'role': 'user',
            'content': assist_mes.contains_data['content']
        }]
    )
    content = response.message.content.strip()
    assist_mes.contains_data['content'] = assist_mes.contains_data['content'].replace(needed_data_mes, "")
    print(f"Contains needed data response: {content}")
    return "true" in content.lower()

def search():
    print("Generating query...")
    search_query = query_generator()
    search_results = OperaGX(search_query)
    context = None
    for i in range(1):
        best_index = best_search(search_results, search_query)

        try:
            page_link = search_results[-1]["link"]


            # print(f'Page link: {page_link}')

        except Exception as e:
            print(f"Error selecting best result: {e}")
            break
        url = extract_target_url(page_link)
        page_text, link = scrape_webpage(url)
        # Remove the used result from the list.
        if page_text and contains_needed_data(page_text, search_query):
            context = page_text
            break
    print(f'Content: {context}')
    return context

def stream_assistant_response(user_input):
    assist_mes.normal_conver['content'] += '"user": ' + user_input
    response: ChatResponse = chat(
        model="llama3.2:3b",
        messages=[{
            'role': 'user',
            'content': assist_mes.normal_conver['content']
        }],
        stream=True
    )


    complete_response = ""
    for chunk in response:
        chunk_text = chunk.message.content
        complete_response += chunk_text
    # Use the valid role "assistant" here.
    print(f"Assistant: {complete_response}\n")
    assist_mes.normal_conver['content'] += '"you": ' + complete_response
    if complete_response == 'Good day to you.':
        sys.exit()

def main():
    while True:
        user_input = input("User: ").strip()
        # search_or_not1 = input('Do you want to search? (y/n) ')
        if not user_input:
            continue
        # Append the new user prompt.
        user_prompt.append(user_input)

        # if search_or_not1 == 'y':
        #     context = search()
        #     if context:
        #         user_input = f"Search result: {context}\nUser prompt: {user_input}"
        #     else:
        #         user_input = (
        #             f"User prompt: {user_input}\nSearch failed: The search did not yield reliable data. "
        #             "Proceed without additional context."
        #         )
        #     # Replace the last user message with the updated version.
        #     user_prompt[-1] = user_input

        stream_assistant_response(user_input)

if __name__ == "__main__":
    main()