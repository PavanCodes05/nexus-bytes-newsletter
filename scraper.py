import requests
from bs4 import BeautifulSoup

def get_content(url):
    response = requests.get(url)

    if response.status_code == 200:
        title = response.text
        print("Title scraped succesfully!")
    else:
        print('Title not found', response.status_code)
        title = None

    if title:
        soup = BeautifulSoup(title, 'html.parser')

    if 'soup' in locals():
        articles = []
        for article in soup.find_all(class_ = "loop-card__title-link"):
            articles.append(article)

    title = articles[0].text
    content_link = articles[0].attrs['data-destinationlink']

    # Scrape the content.

    content_response = requests.get(content_link)
    if content_response.status_code == 200:
        response_content = content_response.text
        print("Content Scraped Succesfully!")
    else:
        print("Content Scraping Failed")
        response_content = None

    if content_response:
        content_soup = BeautifulSoup(response_content, 'html.parser')

    if 'soup' in locals():
        paragraph = []
        for para in content_soup.find_all('p', class_='wp-block-paragraph'):
            paragraph.append(para.text)

    content = paragraph[1:-2]
    
    return (title, content, content_link)
