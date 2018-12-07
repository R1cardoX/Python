import time
import re
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from lxml import etree
options = Options()
options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument('start-maximized')
options.add_argument('window-size=1920x1080')
options.add_argument("--mute-audio")
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")
browser = webdriver.Chrome(executable_path = r'/usr/local/bin/chromedriver',options=options)
name = input('输入要查找的歌曲名字：')
base_search_url = 'https://y.qq.com/portal/search.html#remoteplace=txt.yqq.top&t=song&w='+name
browser.get(base_search_url)
browser.find_element_by_xpath('//*[@class="search_input__input"]').clear()
browser.find_element_by_xpath('//*[@class="search_input__input"]').send_keys(name)
time.sleep(1)
browser.get("https://y.qq.com/portal/search.html#page=1&searchid=1&remoteplace=txt.yqq.top&t=song&w="+name)
browser.find_element_by_xpath("//i").click()
time.sleep(1)
html = etree.HTML(browser.page_source)
for i in range(1,21):
    result = html.xpath('//li['+str(i)+']//a[@class="js_song" or @class="singer_name" or @class="album_name"]/@title')
    print('序号',i,' 歌曲名：',result[0],' 歌手：',result[1],' 专辑：',result[2])
_id = input('输入要下载的歌曲：')
if _id < '21' and _id > '0':
    song_url = html.xpath('//li['+ _id +']//a[@class="js_song"]/@href')
else:
    song_url = html.xpath('//li//a[@title="'+ _id +'"]/@href')
browser.get(song_url[0])
browser.find_element_by_link_text(u"播放").click()
browser.close()
try:
    browser.switch_to_window(browser.window_handles[0])
    time.sleep(2)
    browser.find_element_by_id("btnplay").click() 
    browser.find_element_by_id("simp_btn")
    wait.until
    html = browser.page_source
    soup = BeautifulSoup(html,'lxml')
    print(soup)
    source = soup.find("audio",{"src":re.compile(r'http://.+?')})['src']
except:
    print("Error")
r = requests.get(source)
source_name = source.split('?')[0].split('/')[-1]
with open('./music/'+name+'.m4a', 'wb') as f:
    f.write(r.content)
print('已下载')
print('歌词：')
for soup in soup.find_all(attrs={"class":"song_info__lyric_inner qrc_ctn"}):
    lyrics = soup.find_all("p",{"data-id":re.compile('line_\w+')})
    for lyric in lyrics:
        print(lyric.get_text())
browser.quit()
