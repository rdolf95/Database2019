import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from pypg import helper
import csv

driver_path = "/Users/Rdolf/desktop/selenium/chromedriver"

driver = webdriver.Chrome(driver_path)
 
driver.get("https://map.kakao.com/?from=total&nil_suggest=btn&q=%EC%95%88%EA%B2%BD%EC%9B%90&tab=place")

#print(driver.page_source)
#//*[@id="info.search.place.list"]/li[1]/div[3]/strong/a[2]
time.sleep(2)

temp = driver.find_element_by_xpath('/html/body/div[10]/div/div/div/p')
temp.click()

req = driver.page_source
soup = BeautifulSoup(req,'html.parser')
name =soup.find_all("a",{'data-id': 'name'})
addr =soup.find_all("p",{'data-id': 'address'})
print(name)
print(name[0]['title'])
print(addr[0]['title'])

data = []
for k in range(7):
    for j in range(2,7):
        req = driver.page_source
        soup = BeautifulSoup(req,'html.parser')
        name =soup.find_all("a",{'data-id': 'name'})
        addr =soup.find_all("p",{'data-id': 'address'})
        for i in range(15):
            print(75*k + 15*(j-2) + i)
            if  (75*k + 15*(j-2) + i)>=500:
                break
            
            data.append({'name' : name[i]['title'], 'addr' : addr[i]['title']})

        if k == 6 and j == 5:
            break

        if j != 6:
            button = driver.find_element_by_xpath('//*[@id="info.search.page.no' + str(j) + '"]')
            button.click()
            time.sleep(1.5)

    if k != 6:
        button = driver.find_element_by_xpath('//*[@id="info.search.page.next"]')
        button.click()
        time.sleep(1.5)
   
       


csv_file = "kakao.csv"
csv_columns = ['name', 'addr']

try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
except IOError:
    print("I/O error")