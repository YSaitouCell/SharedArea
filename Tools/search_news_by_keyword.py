import requests
from datetime import datetime, timedelta
from newsapi import NewsApiClient
import re
from urllib.parse import urlparse

NEWS_API_KEY = '313eea86dab94326a97150bf235e2fd0'
keywords = ['シャンパン', 'シャンパーニュ', 'champagne']
start_date = '2024-07-01'
end_date = '2024-07-15'

newsapi = NewsApiClient(api_key=NEWS_API_KEY)

def is_valid_article(article, seen_urls):
    title = article['title'].lower()
    content = article['description'].lower() if article['description'] else ''
    url = article['url']
    
    # 除外するドメイン
    excluded_domains = ['winereport.jp', 'forbes.com', 'thebest-1.com', 'my-best.com']
    
    # URLのドメインチェック
    parsed_url = urlparse(url)
    if any(domain in parsed_url.netloc for domain in excluded_domains):
        return False
    
    # AMPのURL除外
    if 'google.co.jp/amp' in url or '/amp/' in url:
        return False
    
    # 同じサイトの重複記事チェック
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    if base_url in seen_urls:
        return False
    seen_urls.add(base_url)
    
    # キーワードチェック
    if not any(kw.lower() in title or kw.lower() in content for kw in keywords):
        return False
    
    # 除外キーワード
    exclude_phrases = [
        'シャンパンのような', 
        'シャンパーニュ方式', 
        'シャンパーニュと同じ製法',
        'シャンパンとあう', 
        #'入荷情報', 
        #'商品情報'
    ]
    if any(phrase in title or phrase in content for phrase in exclude_phrases):
        return False
    
    # シャンパーニュに関する具体的な情報があるか確認
    #if not re.search(r'シャンパーニュ.*ワイン|シャンパーニュ.*生産|シャンパーニュ.*地域', content):
    #    return False
    
    return True

results = []
seen_urls = set()

for keyword in keywords:
    articles = newsapi.get_everything(q=keyword,
                                      from_param=start_date,
                                      to=end_date,
                                      language=None,
                                      #country='jp',
                                      sort_by='publishedAt')
    
    for article in articles['articles']:
        if is_valid_article(article, seen_urls):
            published_date = datetime.strptime(article['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
            formatted_date = published_date.strftime("%Y/%m/%d")
            results.append({
                'date': formatted_date,
                'url': article['url'],
                'title': article['title']
            })

results.sort(key=lambda x: datetime.strptime(x['date'], "%Y/%m/%d"))

for result in results:
    print(f"日付: {result['date']}")
    print(f"URL: {result['url']}")
    print(f"タイトル: {result['title']}")
    print('-' * 50)