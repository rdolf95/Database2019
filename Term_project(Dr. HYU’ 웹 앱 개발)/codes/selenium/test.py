import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time

#selenium의 webdriver로 크롬 브라우저를 실행한다
driver = webdriver.Chrome("/Users/Rdolf/desktop/selenium/chromedriver")
 
driver.get("http://www.nikon-lenswear.co.kr/store-finder")


driver.switch_to_frame('daum_road_frame')

elem = driver.find_element_by_xpath("//*[@id='location']")

elem.clear()
elem.send_keys("Selenium")
elem.submit()

time.sleep(1)
driver.switch_to_default_content()
driver.switch_to_frame('com_list_frame')

datas = []
for k in range(32):
    for j in range(1,10):
        for i in range(1,11):
            data = driver.find_element_by_xpath("/html/body/div[1]/div/div[" + str(i) + "]").get_attribute('innerHTML')
            data = data.split('<div>')
            print(data[1].strip()[:-6])
            print(data[2].strip()[:-6])

        button = driver.find_element_by_xpath("/html/body/div[2]/div[1]/a[" + str(j) + "]")
        button.click()
        time.sleep(1)
    if k == 0:
        button = driver.find_element_by_xpath("/html/body/div[2]/div[2]/a[3]/img")
        button.click()
        time.sleep(1.5)
    elif k != 31:
        button = driver.find_element_by_xpath("/html/body/div[2]/div[2]/a[4]/img")
        button.click()
        time.sleep(1.5)


print(datas)
