from googlesearch import search

# 予約サイトのキーワードリスト
reservation_sites_keywords = [
    'tabelog', 'hotpepper', 'gurunavi', 'retty', 'yelp', 'ikyu', 
    'jalan', 'ozmall', 'rakuten', 'gnavi', 'foodpia', 'hitomebo'
]

def is_reservation_site(url):
    """予約サイトのURLかどうかを判定"""
    return any(keyword in url for keyword in reservation_sites_keywords)

def google_search_without_reservation_sites(query, num_results=10):
    """Google検索を実行し、予約サイトを除外した結果を取得"""
    search_results = search(query, num_results=num_results)
    filtered_results = [url for url in search_results if not is_reservation_site(url)]
    return filtered_results

# 検索クエリ（例：店舗名）
query = "kitchen"

# 検索実行
results = google_search_without_reservation_sites(query)

# 結果を表示
for idx, url in enumerate(results):
    print(f"{idx + 1}. {url}")
