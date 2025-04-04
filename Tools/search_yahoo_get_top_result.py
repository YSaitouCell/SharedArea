from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import csv
from datetime import datetime

def yahoo_search(driver, keyword):
    try:
        # Yahoo!のモバイルトップページにアクセス
        driver.get("https://m.yahoo.co.jp/")
        
        # 検索ボックスが表示されるまで待機
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "p"))
        )
        
        # 既存の入力をクリアし、新しいキーワードを入力して検索
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        
        # 検索結果が表示されるまで待機
        first_result = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.sw-Card__title a"))
        )
        
        # 1位のサイトのURLを取得（広告枠を除外）
        top_url = first_result.get_attribute('href')
        
        return top_url
    
    except (TimeoutException, NoSuchElementException) as e:
        print(f"エラーが発生しました: {e}")
        return None

def save_results_to_csv(results):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"search_results_{timestamp}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["検索キーワード", "検索順位1位のサイトのURL"])
        writer.writerows(results)
    print(f"結果を {filename} に保存しました。")

# メイン処理
if __name__ == "__main__":
    # Chromeドライバーのオプションを設定
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # ヘッドレスモードで実行（ブラウザを表示しない）
    chrome_options.add_argument("--window-size=375,812")  # モバイル表示用のウィンドウサイズ
    chrome_options.add_argument("--disable-gpu")  # GPUハードウェアアクセラレーションを無効化
    chrome_options.add_argument("--no-sandbox")  # サンドボックスモードを無効化
    
    # Chromeドライバーをセットアップ
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        
    keywords = [
        "看護師 求人 ナースキャストベスト",
        "看護師転職サイト おすすめライブラリー",
        "看護師求人 全国 キャストビズ",
        "看護師 求人 サイトプレミアム公式",
        "看護師転職サイトナースキャストビズ",
        "看護師 転職 navi比較最新版",
        "看護師 転職 ナースキャストビズ",
        "看護師転職 サイトプレミアム",
        "看護師 転活 ナースキャストビズ",
        "薬剤師 転職 サイトライブラリープラス",
        "看護師 仕事探し ナースキャストビズ",
        "看護師求人サイト プレミアムナース",
        "ナース求人 キャスト五社",
        "薬剤師求人サイト ラリーファネット",
        "看護サイト転職ナースキャストビズ",
        "退職代行 アットcom",
        "看護師 再就職 人気キャストベスト",
        "退職代行 最強ガイド ダイジョブ",
        "クレジットカード現金に 特選窓ナビ",
        "ファクタリング サイト",
        "ショッピング枠を現金にかえる 特選窓"
    ]

    
    results = []
    for keyword in keywords:
        result_url = yahoo_search(driver, keyword)
        
        print(f"検索キーワード: {keyword}")
        if result_url:
            print(f"検索順位1位のサイトのURL: \n{result_url}")
            results.append([keyword, result_url])
        else:
            print("URLの取得に失敗しました。")
            results.append([keyword, "取得失敗"])
        print('-' * 50)
    
    # 結果をCSVファイルに保存
    save_results_to_csv(results)
    
    # ブラウザを閉じる
    driver.quit()