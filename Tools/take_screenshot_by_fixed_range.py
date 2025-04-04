from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from PIL import Image

# ChromeDriverのパスを指定
#driver = webdriver.Chrome(executable_path='C:\Program Files\chrome-win64')
service = Service(executable_path="C:\Program Files\chromedriver_win32\chromedriver.exe")
driver = webdriver.Chrome(service=service)

# 指定したURLを開く
driver.get('https://jp.taiwantoday.tw/index.php')

# ページ全体のスクリーンショットを取得
driver.save_screenshot('full_screenshot.png')

# 固定の範囲を切り抜き
left = 0
top = 0
right = 500
bottom = 300

im = Image.open('full_screenshot.png')
im_cropped = im.crop((left, top, right, bottom))
im_cropped.save('cropped_screenshot.png')

driver.quit()
