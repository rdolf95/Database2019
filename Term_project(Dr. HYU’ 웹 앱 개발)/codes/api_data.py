import math
import apicall as apicall
from pypg import helper
from threading import Thread
from time import sleep

hanyang_standard_point = (37.5585146, 127.0331892)
ONE_PAGE_NUM_COUNT = 100

def distance(lat1, lng1, lat2, lng2):
    theta = lng1 - lng2
    dist = math.sin(deg2rad(lat1)) * math.sin(deg2rad(lat2)) + math.cos(deg2rad(lat1))* math.cos(deg2rad(lat2)) * math.cos(deg2rad(theta))
    
    dist = math.acos(dist)
    dist = rad2deg(dist)
    dist = dist * 60 * 1.1515
    dist = dist * 1609.344
    return dist
     
def deg2rad(deg):
    return (deg * math.pi / 180.0)
    
def rad2deg(rad):
    return (rad * 180 / math.pi)

def get_pharmacy_data(lat, lng):
    dist = distance(hanyang_standard_point[0], hanyang_standard_point[1], lat, lng)
    print('distnace' + str(dist))
    # Data is in initial data.
    if dist <= 4000:
        return
    else:
        total_count = apicall.get_pharm_total(lat,lng, 1000)
        # Search hospitals closer than input distance.
        sql = f'''
            SELECT count(*)
            FROM store h
            WHERE 0.621371 >= (SELECT (POINT({lat},{lng}) <@> POINT(h.lat,h.lng)) AS distance) AND kind = 1;
           '''
        close_pharmacy_num = helper.special_sql(sql)[0]['count']

        if close_pharmacy_num >= total_count:
            return
        else: 
            get_new_pharm(lat,lng, total_count)
            return

def get_hospital_data(lat, lng):
    dist = distance(hanyang_standard_point[0], hanyang_standard_point[1], lat, lng)
    print('distnace' + str(dist))
    # Data is in initial data.
    if dist <= 4000:
        return
    else:
        total_count = apicall.get_hos_total(lat,lng, 1000)
        # Search hospitals closer than input distance.
        sql = f'''
            SELECT count(*)
            FROM hospital h
            WHERE 0.621371 >= (SELECT (POINT({lat},{lng}) <@> POINT(h.lat,h.lng)) AS distance);
           '''
        close_hospitals_num = helper.special_sql(sql)[0]['count']
        print('close hospital' + str(close_hospitals_num))
        print('total hospital' + str(total_count))

        if close_hospitals_num >= total_count:
            return
        else: 
            get_new_data(lat,lng, total_count)
            return
        
def get_new_data(lat, lng, total_count):
    # 한번에 100개씩 data 를 받아온다. 
    pageNum = total_count//ONE_PAGE_NUM_COUNT
    remainder = total_count%ONE_PAGE_NUM_COUNT
    th = []
    for i in range(1,pageNum+2):
        if i == (pageNum + 1):
            k = remainder
        else:
            k = ONE_PAGE_NUM_COUNT
        
        # 각 thread 는 1 페이지의 data 를 받아온다.
        thread = Thread(target=apicall.get_hospital_data, args=(lat, lng, 1000, i, k, False))
        th.append(thread)
        thread.start()
        sleep(0.05)
    for thread in th:
        thread.join()

    sql = f'''
            SELECT MAX(hid)
            FROM hospital
           '''
    last_hid = helper.special_sql(sql)[0]['max']
    thread = Thread(target=get_new_detail, args=(last_hid, total_count))
    thread.start()

def get_new_pharm(lat, lng, total_count):
    # 한번에 100개씩 data 를 받아온다. 
    pageNum = total_count//ONE_PAGE_NUM_COUNT
    remainder = total_count%ONE_PAGE_NUM_COUNT
    th = []
    for i in range(1,pageNum+2):
        if i == (pageNum + 1):
            k = remainder
        else:
            k = ONE_PAGE_NUM_COUNT
        
        # 각 thread 는 1 페이지의 data 를 받아온다.
        thread = Thread(target=apicall.get_pharmacy_data, args=(lat, lng, 1000, i, k, False))
        th.append(thread)
        thread.start()
        sleep(0.05)
    for thread in th:
        thread.join()

def get_new_detail(last_hid, total_count):
    print('get_new_detail')
    for hid in range(last_hid - total_count+1, last_hid + 1):
        subject = helper.search('h_subject', ['hid'], [('hid', hid)], 1)
        if subject == []:
            print(hid)
            ykiho = helper.search('hospital', ['ykiho'], [('hid', hid)], 1)[0]['ykiho']
            apicall.get_hos_detail(ykiho, hid)
            apicall.get_subject(ykiho, hid, False)
