import openai
from openai import OpenAI
import os

## 9/22/2025 - trying to scrape search results from Bing
# Scrape the data and 
## write it into superbase, part 1
## deploy streamlit app to read from supabase, part 2
## then part 3, deploy streamlit app to Modal
## Due before Friady (API) 9/27/2024

## *********SUMMARY********* 
## webscraping html
## LLM to process the html
## Try to parse and pretty print the JSon
## import JSON
## try: 
##    parsed_json = json.loads(response.choices[0].message.content)
##    print(json.dumps(parsed_json, indent=4))
## except json.JSONDecodeError as e:



## CODE BELOW ******


## UNCOMMENT TO SCRAPE
## scrape_url = "https://www.bing.com/search?q=javascript+semicolons+optional"
## headers = {
##    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
## }
## response=requests.get(scrape_url, headers=headers)
## soup = BeautifulSoup(response.text, 'html.parser')
## print(soup.prettify())

## COMMENTED OUT BELOW, NOT NEEDED
search_results = soup.find_all('li', class_='b_algo')   
endpoint = "https://cdong1--azure-proxy-web-app.modal.run"
api_key = "supersecretkey"
deployment_name = "gpt-4o"



client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

response = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {
            "role": "developer",
            "content": "Talk like a pirate."
        },
        {
            "role": "user",
            "content": "Are semicolons optional in JavaScript?"
        }
    ]
)

print(response.choices[0].message.content)
