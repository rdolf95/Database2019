import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from pypg import helper
import csv

#selenium의 webdriver로 크롬 브라우저를 실행한다
driver_path = "/Users/Rdolf/desktop/selenium/chromedriver"
driver = webdriver.Chrome(driver_path)
 
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
    for j in range(1,11):
        for i in range(1,11):
            if k == 31 and j == 6 and i == 9:
                break

            print(100*k + 10*(j-1) + (i-1))
            data = driver.find_element_by_xpath("/html/body/div[1]/div/div[" + str(i) + "]").get_attribute('innerHTML')
            data = data.split('<div>')

            data.append({'name' :data[1].strip()[:-6], 'addr' : data[2].strip()[:-6]})
            helper.insert('store', [('kind', 2,), ('addr', '\'' + data[2].strip()[:-6] + '\''), \
                                                 ('name', '\'' + data[1].strip()[:-6] + '\'')])

        if k == 31 and j == 6:
            break

        if j != 10:
            button = driver.find_element_by_xpath("/html/body/div[2]/div[1]/a[" + str(j) + "]")
            button.click()
            time.sleep(1.5)

    if k == 0:
        button = driver.find_element_by_xpath("/html/body/div[2]/div[2]/a[3]/img")
        button.click()
        time.sleep(1.5)
    elif k != 31:
        button = driver.find_element_by_xpath("/html/body/div[2]/div[2]/a[4]/img")
        button.click()
        time.sleep(1.5)


csv_file = "nikon.csv"
csv_columns = ['name', 'addr']

try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
except IOError:
    print("I/O error")

print('done!')
