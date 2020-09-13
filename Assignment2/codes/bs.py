import requests
from bs4 import BeautifulSoup

req = requests.get('https://map.naver.com/v5/search/안경원?c=14140783.3503578,4517457.0355395,13,0,0,0,dh')
html = req.text
soup = BeautifulSoup(html, 'html.parser')
print(html)
my_titles = soup.select(
    'body > app > layout > div > div.container > div.router-output > shrinkable-layout > search-layout > search-list > search-list-contents > perfect-scrollbar > div > div.ps-content > div > div > div > search-item-place:nth-child(3) > div > div.search_box > div.title_box > strong > span.search_title_text'
    )
print(my_titles)
# my_titles는 list 객체
for title in my_titles:
    # Tag안의 텍스트
    print(title.text)
