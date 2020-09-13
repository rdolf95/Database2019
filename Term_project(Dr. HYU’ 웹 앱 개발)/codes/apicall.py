import json
import requests
from pypg import helper
from threading import Thread

ONE_PAGE_NUM_COUNT = 100

def hosp_list(lat, lng, pageNum, rowNum, radius):    
    
    url = "http://apis.data.go.kr/B551182/hospInfoService/getHospBasisList"
    default_key = "cvebA7Nf1iP0/+f7J/K9wKEB4AufEEbr4ZYQ1++e6NdF2OjrnuaDOHvxdlLTF+4ujWJ+dUJ8Jt1o5yzjGDqltQ=="
    params = {
      'pageNo': pageNum,
      'numOfRows': rowNum,
      'ServiceKey': default_key,
      'xPos': lng,
      'yPos': lat,
      #sogang 1493 solve
      'radius': radius,
      '_type': 'json'
    }
    r = requests.get(url, params=params)
    return r.json()


def hosp_date(ykiho):
    url = "http://apis.data.go.kr/B551182/medicInsttDetailInfoService/getDetailInfo"
    default_key = "cvebA7Nf1iP0/+f7J/K9wKEB4AufEEbr4ZYQ1++e6NdF2OjrnuaDOHvxdlLTF+4ujWJ+dUJ8Jt1o5yzjGDqltQ=="
    params = {
      'ServiceKey': default_key,
      'ykiho': ykiho,
      '_type': 'json'
    }
    r = requests.get(url, params=params)
    try:
      result =  r.json()
    except ValueError:
      print('detail error')
      result = None
    return result
      

def hosp_subject(ykiho):
    url = "http://apis.data.go.kr/B551182/medicInsttDetailInfoService/getMdlrtSbjectInfoList"
    default_key = "cvebA7Nf1iP0/+f7J/K9wKEB4AufEEbr4ZYQ1++e6NdF2OjrnuaDOHvxdlLTF+4ujWJ+dUJ8Jt1o5yzjGDqltQ=="
    params = {
      'numOfRows': 100,
      'ServiceKey': default_key,
      'ykiho': ykiho,
      '_type': 'json'
    }
    r = requests.get(url, params=params)
    try:
      result =  r.json()
    except ValueError:
      print('subject errors')
      result = None
    return result


def pharm_list(lat, lng, pageNum, rowNum, radius):    
    url = "http://apis.data.go.kr/B551182/pharmacyInfoService/getParmacyBasisList"
    default_key = "cvebA7Nf1iP0/+f7J/K9wKEB4AufEEbr4ZYQ1++e6NdF2OjrnuaDOHvxdlLTF+4ujWJ+dUJ8Jt1o5yzjGDqltQ=="
    params = {
      'pageNo': pageNum,
      'numOfRows': rowNum,
      'ServiceKey': default_key,
      'xPos': lng,
      'yPos': lat,      
      'radius': radius,
      '_type': 'json'
    }
    r = requests.get(url, params=params)
    try:
      result =  r.json()
    except ValueError:
      print('subject errors')
      result = None
    return result

''' 주어진 위치, 반경에 대해 총 병원의 개수를 return 한다.
'''
def get_hos_total(lat,lng,radius):
     # 총 data 의 개수를 얻기 위해 하나의 데이터만 받아온다.
    hospital = hosp_list(lat, lng, 1, 1, radius)
    total_count = hospital['response']['body']['totalCount']
    return total_count


def get_pharm_total(lat,lng,radius):
     # 총 data 의 개수를 얻기 위해 하나의 데이터만 받아온다.
    pharmacy = pharm_list(lat, lng, 1, 1, radius)
    total_count = pharmacy['response']['body']['totalCount']
    print(total_count)
    return total_count


'''병원정보 데이터베이스에서 병원 데이터를 받아 local DB 에 저장한다.
   row_num 개수의 row 가 있는 page number 의 page 를 가져온다.
'''
def get_hospital_data(lat, lng, radius, page, row_num, isFirst):

    print("page" + str(page))
    # page number 에 해당하는 page 를 읽어온다.
    hospital = hosp_list(lat, lng, page, row_num, radius)
    th = []
    for j in range(row_num):
      print(j)
      input = []
      # i 번째 page 에서 j 번째 병원의 data
      jth_hos = hospital['response']['body']['items']['item'][j]
      # 병원 정보 api 에서 받아 올 수 있는 데이터를 먼저 받아온다.
      input.append(('lng', jth_hos['XPos']))
      input.append(('lat', jth_hos['YPos']))
      name = '\'' + jth_hos['yadmNm']  + '\''
      input.append(('name', name))
      input.append(('dnum', jth_hos['drTotCnt']))
      input.append(('addr', '\'' + jth_hos['addr'] + '\''))
      input.append(('ykiho', '\'' + jth_hos['ykiho'] + '\''))
      
      # When getting data is not first, check the data exist.
      if isFirst is True:
        helper.insert('hospital', input)
      else:
        hos = helper.search('hospital', ['hid'], input, 1)
        if hos != []:
          continue
        else:
          helper.insert('hospital', input)
          

      '''
      th.append(Thread(target=h_insert_subject_thread, args=(input, ykiho, name)))
      th[j].start()
    for j in range(row_num):
      th[j].join()
      '''


''' 사용자가 병원의 이름을 선택 했고, database 에 저장이 되어있지 않을 때 사용한다.
    data base 에서 저장이 되어있지 않은 것을 확인 할 때 ykiho 와 hid 를 함께 받아온다. (TODO 테스트 안됨)
'''
def get_hos_detail(ykiho, hid):
    input = []
    jth_hos_detail = hosp_date(ykiho)
    while jth_hos_detail is None:
      jth_hos_detail = hosp_date(ykiho)
    jth_hos_detail = jth_hos_detail['response']['body']['items']
    # 상세 정보가 있을 시
    if jth_hos_detail != '':
      jth_hos_detail = jth_hos_detail['item']
      # 월~일 의 시간 데이터가 있을 때만 받아온다.
      startTimes = ['monstart', 'tuestart', 'wedstart', 'thustart', 'fristart', 'satstart', 'sunstart']
      endTimes = ['monend', 'tueend', 'wedend', 'thuend', 'friend', 'satend', 'sunend']

      '''
      for i in range(7):
        if startTimes[i] in jth_hos_detail:
          if check_is_time(jth_hos_detail[startTimes[i]]):
            input.append((startTimes[i], '\'' + str(jth_hos_detail[startTimes[i]]) + '\''))
        if endTimes[i] in jth_hos_detail:
          if check_is_time(jth_hos_detail[endTimes[i]]):
            input.append((endTimes[i], '\'' + str(jth_hos_detail[endTimes[i]]) + '\''))
      '''
      if 'trmtMonStart' in jth_hos_detail:
        if check_is_time(str(jth_hos_detail['trmtMonStart'])):
          input.append(('monStart', '\'' + str(jth_hos_detail['trmtMonStart']) + '\''))
      if 'trmtMonEnd' in jth_hos_detail:
        if check_is_time(str(jth_hos_detail['trmtMonEnd'])):
          input.append(('monEnd', '\'' + str(jth_hos_detail['trmtMonEnd']) + '\''))
      if 'trmtTueStart' in jth_hos_detail:
        if check_is_time(str(jth_hos_detail['trmtTueStart'])):
          input.append(('tueStart', '\'' + str(jth_hos_detail['trmtTueStart']) + '\''))
      if 'trmtTueEnd' in jth_hos_detail:
        if check_is_time(str(jth_hos_detail['trmtTueEnd'])):
          input.append(('tueEnd', '\'' + str(jth_hos_detail['trmtTueEnd']) + '\''))
      if 'trmtWedStart' in jth_hos_detail:
        if check_is_time(str(jth_hos_detail['trmtWedStart'])):
          input.append(('wedStart', '\'' + str(jth_hos_detail['trmtWedStart']) + '\''))
      if 'trmtWedEnd' in jth_hos_detail:
        if check_is_time(str(jth_hos_detail['trmtWedEnd'])):
          input.append(('wedEnd', '\'' + str(jth_hos_detail['trmtWedEnd']) + '\''))
      if 'trmtThuStart' in jth_hos_detail:
        if check_is_time(str(jth_hos_detail['trmtThuStart'])):
          input.append(('thuStart', '\'' + str(jth_hos_detail['trmtThuStart']) + '\''))
      if 'trmtThuEnd' in jth_hos_detail:
        if check_is_time(str(jth_hos_detail['trmtThuEnd'])):
          input.append(('thuEnd', '\'' + str(jth_hos_detail['trmtThuEnd']) + '\''))
      if 'trmtFriStart' in jth_hos_detail:
        if check_is_time(str(jth_hos_detail['trmtFriStart'])):
          input.append(('friStart', '\'' + str(jth_hos_detail['trmtFriStart']) + '\''))
      if 'trmtFriEnd' in jth_hos_detail:
        if check_is_time(str(jth_hos_detail['trmtFriEnd'])):
          input.append(('friEnd', '\'' + str(jth_hos_detail['trmtFriEnd']) + '\''))
      if 'trmtSatStart' in jth_hos_detail:
        if check_is_time(str(jth_hos_detail['trmtSatStart'])):
          input.append(('satStart', '\'' + str(jth_hos_detail['trmtSatStart']) + '\''))
      if 'trmtSatEnd' in jth_hos_detail:
        if check_is_time(str(jth_hos_detail['trmtSatEnd'])):
          input.append(('satEnd', '\'' + str(jth_hos_detail['trmtSatEnd']) + '\''))
      if 'trmtSunStart' in jth_hos_detail:
        if check_is_time(str(jth_hos_detail['trmtSunStart'])):
          input.append(('sunStart', '\'' + str(jth_hos_detail['trmtSunStart']) + '\''))
      if 'trmtSunEnd' in jth_hos_detail:
        if check_is_time(str(jth_hos_detail['trmtSunEnd'])):
          input.append(('sunEnd', '\'' + str(jth_hos_detail['trmtSunEnd']) + '\''))

    if input != []:
      helper.modify('hospital',[('hid', hid)], input, 'hid')

def check_is_time(string):
  time = int(string)
  hour = time/100
  minute = time%100
  if hour < 0 or hour > 24:
    return False
  if minute < 0 or minute >60:
    return False
  
  return True
    


''' 사용자가 병원을 선택 하였을 때 name 을 받아와 검색, 
    ykiho 와 hid 를 받아와 parameter 로 사용한다. (TODO 테스트 안됨)
'''
def get_subject(ykiho, hid, isFirst):
    if isFirst is False:
      check = helper.search('h_subject', ['hid'], [('hid', hid)], 1)
      if check != []:
        return

    # 병원 진료과목 받아오기 (병원의 데이터가 데이터 베이스에 먼저 저장이 되어 있어야 함)
    jth_hos_subject = hosp_subject(ykiho)
    while jth_hos_subject is None:
        jth_hos_subject = hosp_subject(ykiho)
    sub_total = jth_hos_subject['response']['body']['totalCount']
    jth_hos_subject = jth_hos_subject['response']['body']['items']
    
    if jth_hos_subject != '':
      #hid = helper.search('hospital', ['hid'], [('name',name)], 1)[0]['hid']
      if(sub_total != 1):
        for p in range(sub_total):
          subject_input = []
          subject_input.append(('hid', hid))
          subject = '\'' + jth_hos_subject['item'][p]['dgsbjtCdNm'] + '\''
          #print(subject)
          subject_input.append(('subject', subject))
          helper.insert('h_subject', subject_input)
      else:
        subject_input = []
        subject_input.append(('hid', hid))
        subject = '\'' + jth_hos_subject['item']['dgsbjtCdNm'] + '\''
        #print(subject)
        subject_input.append(('subject', subject))
        helper.insert('h_subject', subject_input)
        
    
''' 약국 data 를 받아온다.
'''
def get_pharmacy_data(lat, lng, radius, page, row_num, isFirst):
    pharmacy = pharm_list(lat, lng, page, row_num, radius)

    for j in range(row_num):
      print(j)
      input = []
      # i 번째 page 에서 j 번째 병원의 data
      jth_pharm = pharmacy['response']['body']['items']['item'][j]
      # 병원 정보 api 에서 받아 올 수 있는 데이터를 먼저 받아온다.
      input.append(('lng', jth_pharm['XPos']))
      input.append(('lat', jth_pharm['YPos']))
      name = '\'' + jth_pharm['yadmNm']  + '\''
      input.append(('name', name))
      input.append(('addr', '\'' + jth_pharm['addr'] + '\''))
      input.append(('kind', 1))

      if isFirst is True:
        helper.insert('store', input)
      else:
        sto = helper.search('store', ['sid'], input[0:3], 1)
        print(sto)
        if sto != []:
          continue
        else:
          helper.insert('store', input)


def h_insert_subject_thread(input, ykiho, name):
    helper.insert('hospital', input)
    get_subject(ykiho,name)
      

def get_default():
    # 총 data 의 개수를 얻기 위해 하나의 데이터만 받아온다.
    radius = 5000
    lat = 37.5585146
    lng = 127.0331892

    total_count = get_hos_total(lat,lng, radius)
    print(total_count)
    # 한번에 100개씩 data 를 받아온다. 
    pageNum = total_count//ONE_PAGE_NUM_COUNT
    remainder = total_count%ONE_PAGE_NUM_COUNT

    for i in range(1,pageNum+2):
      if i == (pageNum + 1):
        k = remainder
      else:
        k = ONE_PAGE_NUM_COUNT
      get_hospital_data(lat, lng, radius, i, k, True)

    print('get_hospital done')
    
    # detail data 를 받아온다.
    for i in range(1, total_count+1):
      print(i)
      ykiho = helper.search('hospital', ['ykiho'], [('hid', i)], 1)[0]['ykiho']
      get_hos_detail(ykiho, i)
      get_subject(ykiho, i, True)


    # 약국 데이터 받아오기
    total_pharm = get_pharm_total(lat,lng, radius)
    pageNum = total_pharm//ONE_PAGE_NUM_COUNT
    remainder = total_pharm%ONE_PAGE_NUM_COUNT
    for i in range(1,pageNum+2):
      if i == (pageNum + 1):
        k = remainder
      else:
        k = ONE_PAGE_NUM_COUNT
      get_pharmacy_data(lat, lng, radius, i, k, True)


def repair():
    radius = 1000
    lat = 37.5585146
    lng = 127.0331892
    i = 2288
    ykiho = helper.search('hospital', ['ykiho'], [('hid', i)], 1)[0]['ykiho']
    get_hos_detail(ykiho, i)
    get_subject(ykiho, i, True)



if __name__ == ("__main__"):
    get_default()