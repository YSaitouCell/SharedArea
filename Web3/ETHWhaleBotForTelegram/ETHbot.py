import os, time, requests
import tweepy
from web3 import Web3
from telegram import Bot
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
import sys

# モジュールのパスを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 設定ファイルから値を取得
from common import const_ethWhaleNews as const
from common import modules

# INFURA
INFURA_URL = const.CONFIG["Infura"]["INFURA_URL"]

# TELEGRAM
TELEGRAM_BOT_TOKEN = const.CONFIG["Telegram"]["TELEGRAM_BOT_TOKEN"]
TELEGRAM_ETHBOT_CHAT_ID = const.CONFIG["Telegram"]["TELEGRAM_ETHBOT_CHAT_ID"]
TELEGRAM_BOT_TOKEN_EN = const.CONFIG["Telegram"]["TELEGRAM_BOT_TOKEN_EN"]
TELEGRAM_ETHBOT_EN_CHAT_ID = const.CONFIG["Telegram"]["TELEGRAM_ETHBOT_EN_CHAT_ID"]

# ETHERSCAN
ETHERSCAN_API_KEY = const.CONFIG["Etherscan"]["ETHERSCAN_API_KEY"]

# X
X_API_KEY = const.CONFIG["X"]["X_API_KEY"]
X_API_SECRET = const.CONFIG["X"]["X_API_SECRET"]
X_ACCESS_TOKEN = const.CONFIG["X"]["X_ACCESS_TOKEN"]
X_ACCESS_TOKEN_SECRET = const.CONFIG["X"]["X_ACCESS_TOKEN_SECRET"]
X_BEARER_TOKEN = const.CONFIG["X"]["X_BEARER_TOKEN"]

# LINE
LINE_CHANNEL_ACCESS_TOKEN = const.CONFIG["Line"]["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_USER_ID = const.CONFIG["Line"]["LINE_USER_ID"]

# AFFILIATE LINK
AFFILIATE_LINK_BITFLYER = const.CONFIG["Affiliate_Link"]["AFFILIATE_LINK_BITFLYER"]
AFFILIATE_LINK_BYBIT = const.CONFIG["Affiliate_Link"]["AFFILIATE_LINK_BYBIT"]

# THRESHOLD & BLOCK_LOOKBACK
THRESHOLD_ETH = const.CONFIG["Settings"]["THRESHOLD_ETH"]
BLOCK_LOOKBACK = const.CONFIG["Settings"]["BLOCK_LOOKBACK"]


# 認証設定
auth = tweepy.OAuthHandler(X_API_KEY, X_API_SECRET)
auth.set_access_token(X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)

# APIクライアント作成（メディアアップロード用）
api = tweepy.API(auth)

# X Client作成（投稿用）
x_client = tweepy.Client(
    bearer_token=X_BEARER_TOKEN,
    consumer_key=X_API_KEY,
    consumer_secret=X_API_SECRET,
    access_token=X_ACCESS_TOKEN,
    access_token_secret=X_ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=True
)
# LINEメッセンジャーのクラス
class LineMessenger:
    def __init__(self, channel_access_token):
        """
        LINE Messaging APIの初期化
        Args:
            channel_access_token (str): LINEチャネルアクセストークン
        """
        self.line_bot_api = LineBotApi(channel_access_token)

    def send_message(self, user_id, message):
        """
        指定したユーザーにメッセージを送信
        Args:
            user_id (str): 送信先のLINEユーザーID
            message (str): 送信するメッセージ
        Returns:
            bool: 送信成功時はTrue、失敗時はFalse
        """
        try:
            self.line_bot_api.push_message(
                user_id,
                TextSendMessage(text=message)
            )
            return True
        except LineBotApiError as e:
            print(f"エラーが発生しました: {e}")
            return False
        
# Web3 インスタンスを作成
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Telegram ボットのインスタンスを作成
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# 送信済みのメッセージを保存するためのセット
sent_block_numbers = set()

# LINEメッセンジャーのインスタンスを作成
line_messenger = LineMessenger(LINE_CHANNEL_ACCESS_TOKEN)

def get_eth_jpy_price():
    # ETH日本円換算額を取得
    print('get_eth_jpy_price')
    url = "https://api.bitflyer.com/v1/ticker?product_code=ETH_JPY"
    try:
        response = requests.get(url)
        data = response.json()
        return float(data['ltp'])  # last traded price
    except Exception as e:
        print(f"ETH価格取得エラー: {e}")
        return None    

def get_eth_usd_price():
    # ETHUSD価格を取得
    print('get_eth_usd_price')
    url = "https://api.bitflyer.com/v1/ticker?product_code=ETH_USD"
    try:
        response = requests.get(url)
        data = response.json()
        return float(data['ltp'])  # last traded price
    except Exception as e:
        print(f"ETH価格取得エラー: {e}")
        return None    
        
def get_latest_block():
    # 最新のブロック番号を取得
    print('get_latest_block')
    try:
        return web3.eth.block_number
    except Exception as e:
        print(f"[ERROR] ブロック取得失敗: {e}")
        return None

def get_transactions_from_block(block_number):
    # 特定のブロックから通常の ETH トランザクションを取得
    print('get_transactions_from_block')

    try:
        block = web3.eth.get_block(block_number, full_transactions=True)
        transactions = []

        for tx in block.transactions:
            if tx.value > Web3.to_wei(THRESHOLD_ETH, 'ether'):
                transactions.append({
                    "hash": tx.hash.hex(),
                    #"from": tx["from"],
                    #"to": tx["to"],
                    "value": Web3.from_wei(tx.value, 'ether'),
                    "block": block_number                    
                })

        return transactions
    except Exception as e:
        print(f"[ERROR] ブロック {block_number} のトランザクション取得失敗: {e}")
        return []        

def get_internal_transactions(block_number):
    # Etherscan API を利用して内部トランザクションを取得
    print('get_internal_transactions')

    try:
        url = f"https://api.etherscan.io/api?module=account&action=txlistinternal&startblock={block_number}&endblock={block_number}&sort=asc&apikey={ETHERSCAN_API_KEY}"
        response = requests.get(url, timeout=10)  # タイムアウト設定
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "1" and "result" in data:
                transactions = []
                for tx in data["result"]:
                    value_eth = int(tx["value"]) / 10**18  # Wei → ETH に変換
                    if value_eth > THRESHOLD_ETH:  # 1000 ETH 以上かチェック
                        transactions.append({
                            "hash": tx["hash"],
                            #"from": tx["from"],
                            #"to": tx["to"],
                            "value": value_eth,
                            "block": block_number
                        })
                return transactions
        print(f"[WARNING] Etherscan からデータ取得失敗 (ブロック {block_number})")
    except Exception as e:
        print(f"[ERROR] Etherscan API 取得失敗: {e}")
    return []

def generate_whale_alert_message(
    tx: dict,
    eth_jpy_price: float | None,
    eth_usd_price: float | None,
    language: str,
    affiliate_link: str
) -> str:
    """
    Generate whale alert message in specified language with optional price information.
    
    Args:
        tx (dict): Transaction data
        eth_jpy_price (float | None): ETH/JPY exchange rate, None if unavailable
        eth_usd_price (float | None): ETH/USD exchange rate, None if unavailable
        language (str): Message language ("ja" or "en")
        affiliate_link (str): Affiliate link to include
    
    Returns:
        str: Formatted message
    """
    print('generate_whale_alert_message')

    # Ensure tx hash has 0x prefix
    tx_hash = tx['hash'] if tx['hash'].startswith("0x") else "0x" + tx['hash']
    eth_amount = round(tx['value'], 3)
    
    # Calculate conversion values if rates are available
    jpy_value = round(float(tx['value']) * eth_jpy_price) if eth_jpy_price is not None else None
    usd_value = round(float(tx['value']) * eth_usd_price) if eth_usd_price is not None else None
    
    # Etherscan URLを生成
    etherscan_url = f"https://etherscan.io/tx/{tx_hash}"                    

    templates = {
        "ja": {
            "alert": "🚨 ETH クジラアラート！🚨",
            "block": f"ブロック: {tx['block']}",
            "amount": f"送金額: {eth_amount} ETH",
            "jpy_value": f"💰 日本円換算: {jpy_value:,} JPY" if jpy_value is not None else None,
            "eth_jpy_price": f"📈 1 ETH = {eth_jpy_price:,} JPY" if eth_jpy_price is not None else None,
            # "cta": "👀 クジラの動きに乗り遅れるな！",
            # "affiliate": "👉 今すぐ1500円分のBTCを獲得しETH取引を始める:",
            # "etherscan": "🔍 [Etherscan:]"
        },
        "en": {
            "alert": "🚨 ETH Whale Alert! 🚨",
            "block": f"Block: {tx['block']}",
            "amount": f"Amount: {eth_amount} ETH",
            "usd_value": f"💰 Value in USD: ${usd_value:,}" if usd_value is not None else None,
            "eth_usd_price": f"📈 1 ETH = ${eth_usd_price:,}" if eth_usd_price is not None else None
            # "cta": "👀 Don't miss the whale movements!",
            # "affiliate": "👉 Get max 6045 USDT bonus and start trading ETH now:",
            # "etherscan": "🔍 [View on Etherscan]"
        }
    }
    
    t = templates[language]
    
    # Build message parts, excluding None values
    message_parts = [
        t['alert'],
        t['block'],
        t['amount']
    ]
    
    # Add price information if available
    if language == "ja" and eth_jpy_price is not None:
        message_parts.extend([t['jpy_value'], t['eth_jpy_price']])
    elif language == "en" and eth_usd_price is not None:
        message_parts.extend([t['usd_value'], t['eth_usd_price']])
    
    # Add CTA and affiliate information
    # message_parts.extend([
    #     "",  # Empty line
    #     t['cta'],
    #     t['affiliate'],
    #     affiliate_link,
    #     "",  # Empty line
    #     f"{t['etherscan']}({etherscan_url})"
    # ])
    
    return "\n".join(message_parts)

def send_telegram_message_for_jp(message):
    # Telegramに送信
    print('send_telegram_message_for_jp')

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_ETHBOT_CHAT_ID, "text": message}
    requests.post(url, data=payload)

def send_telegram_message_for_en(message):
    # Telegramに送信
    print('send_telegram_message_for_en')

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN_EN}/sendMessage"
    payload = {"chat_id": TELEGRAM_ETHBOT_EN_CHAT_ID, "text": message}
    requests.post(url, data=payload)

def monitor_transactions():
    # ETH クジラアラートボットのメイン関数
    print('monitor_transactions')
    
    # 初期ブロック取得
    last_checked_block = get_latest_block()
    
    if last_checked_block is None:
        print("[ERROR] 初期ブロック取得に失敗。終了します。")
        return        

    # 最初に過去10ブロック分を見る
    last_checked_block -= BLOCK_LOOKBACK

    # メインループの外側でフラグを定義
    should_exit = False

    while True:
        if should_exit:
            break  # 外側のループを抜ける

        latest_block = get_latest_block()
        if latest_block is None:
            time.sleep(10)
            continue
        
        if latest_block > last_checked_block:
            print(f"Checking blocks {last_checked_block + 1} to {latest_block}...")
            
            for block_number in range(last_checked_block + 1, latest_block + 1):
                # 通常のトランザクションを取得
                normal_txs = get_transactions_from_block(block_number)
                
                # 内部トランザクションを取得
                internal_txs = get_internal_transactions(block_number)
                
                # 日本円換算値を取得
                eth_jpy_price = get_eth_jpy_price()

                # 日本円換算値を取得
                eth_usd_price = get_eth_usd_price()

                # 送信メッセージ作成
                for tx in normal_txs + internal_txs:
                    # ハッシュ値の先頭に0xがない場合は付与
                    tx_hash = tx['hash']
                    if not tx_hash.startswith("0x"):
                        tx_hash = "0x" + tx_hash
                    
                    # 日本語メッセージ作成
                    ja_message = generate_whale_alert_message(
                        tx=tx,
                        eth_jpy_price=eth_jpy_price,
                        eth_usd_price=eth_usd_price,
                        language="ja",
                        affiliate_link=AFFILIATE_LINK_BITFLYER
                    )

                    # 英語メッセージ作成
                    en_message = generate_whale_alert_message(
                        tx=tx,
                        eth_jpy_price=eth_jpy_price,
                        eth_usd_price=eth_usd_price,
                        language="en",
                        affiliate_link=AFFILIATE_LINK_BYBIT
                    )

                    print(ja_message)  # コンソールに表示
                    print(en_message)  # コンソールに表示
                    
                    # ブロック番号の重複をチェックして送信
                    if tx["block"] not in sent_block_numbers:
                        send_telegram_message_for_jp(ja_message)  # Telegram 日本語Botに送信
                        send_telegram_message_for_en(en_message)  # Telegram 英語Botに送信
                        line_messenger.send_message(LINE_USER_ID, ja_message)
              
                        first_post_result = modules.post_to_x(api, x_client, ja_message, None, None)
                        first_post_post_id = first_post_result["post_id"] 
                        time.sleep(10)
                        #input("Enter")
                        # メッセージの後半部分を作成
                        second_message_parts_jp = [
                            "#PR",
                            "👀 クジラの動きに乗り遅れるな！",
                            "👉 今すぐ1500円分のBTCを獲得しETH取引を始める:",
                            AFFILIATE_LINK_BYBIT
                        ]

                        second_message_parts_en = [
                            "#PR",
                            "👀 Don't miss the whale movements!",
                            "👉 Get USDT bonus and start trading ETH now:",
                            AFFILIATE_LINK_BYBIT
                        ]
                        second_message = "\n".join(second_message_parts_jp)
                        
                        # 返信として投稿
                        second_post_result = modules.post_to_x(api, x_client, second_message, None, first_post_post_id)                                                
                        second_post_post_id = second_post_result["post_id"]
                        
                        time.sleep(10)
                        #input("Enter")
                        third_message_parts_jp = [
                            f"🔍 [Etherscanで取引詳細を見る](https://etherscan.io/tx/{tx_hash})"
                        ]
                        third_message_parts_en = [
                            f"🔍 [View on Etherscan](https://etherscan.io/tx/{tx_hash})"
                        ]
                        third_message = "\n".join(third_message_parts_jp)
                        
                        # 返信として投稿
                        modules.post_to_x(api, x_client, third_message, None, second_post_post_id)

                        # ループを抜ける
                        should_exit = True
                        break  # txのループを抜ける
                        
                        # 注意：以下のコードには到達しない
                        # sent_block_numbers.add(tx["block"])  # 送信済みブロック番号を保存
                
                if should_exit:
                    break  # block_numberのループを抜ける
            
        if not should_exit:    
            last_checked_block = latest_block  # 最新ブロックを更新

        time.sleep(10)  # 10秒ごとにチェック

if __name__ == "__main__":
    monitor_transactions()
    print("Finished monitoring transactions.")