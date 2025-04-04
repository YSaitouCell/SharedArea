import requests
from bs4 import BeautifulSoup
import re

# URLリストを定義
urls = [
    'https://www.icyokohama-grand.com/',
    'https://www.tokyuhotels.co.jp/en/yokohama-r/index.html',
    # 他のURLを追加
]

# 電話番号を取得する関数
def get_phone_numbers(url):
    #phone_numbers = []
    phone_numbers = set()
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 'tel:'リンクを含む<a>タグを検索
        phone_links = soup.find_all('a', href=re.compile(r'tel:'))
        
        # 電話番号をリストに追加
        for link in phone_links:
            phone_number = link.get_text()
            #phone_numbers.append(phone_number)
            #phone_numbers.add(phone_number)

            clean_phone_number = re.sub(r'[^\d-]+', '', phone_number)
            if clean_phone_number:
                phone_numbers.add(clean_phone_number)            
    
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")

    #return phone_numbers
    return list(phone_numbers)

# 各URLに対して電話番号を取得
for url in urls:
    phone_numbers = get_phone_numbers(url)
    print(f"Phone numbers found on {url}: {phone_numbers}")
