import psycopg2 as pg
import psycopg2.extras
from threading import Thread


db_connector = {
    'host': "localhost",
    'user': "Rdolf",
    'dbname': "postgres",
}

connect_string = "host={host} user={user} dbname={dbname}".format(
    **db_connector)


# TODO: 처방전 : 약 data 테이블 만들어야됨
# application 에서 사용되는 모든 table 을 create
def create_table(total_tname):

    check_sql = []

    for table_name in total_tname:
        check_sql.append(f'''SELECT EXISTS(
                             SELECT relname 
                             FROM pg_class 
                             WHERE relname = \'{table_name}\');
                            ''')

    sql_arr = []
    # 병원 table
    sql_arr.append(f''' CREATE TABLE hospital(
                        hid SERIAL PRIMARY KEY,
                        name VARCHAR(200),
                        dnum Integer,
                        monStart time, monEnd time,
                        tueStart time, tueEnd time,
                        wedStart time, wedEnd time,
                        thuStart time, thuEnd time,
                        friStart time, friEnd time,
                        satStart time, satEnd time,
                        sunStart time, sunEnd time,
                        lng double precision,
                        lat double precision,
                        addr VARCHAR(100),
                        ykiho VARCHAR(100)
                        );
                    ''')

    # 환자 테이블
    sql_arr.append(f''' CREATE TABLE patient(
                        pid SERIAL PRIMARY KEY,
                        name VARCHAR(20),
                        phone VARCHAR(20)
                        );
                    ''')

    # 사용자 테이블
    # TODO primary key 만들어줘야된다, kind INTEGER 만들어야 한다.
    sql_arr.append(f''' CREATE TABLE client(
                        name VARCHAR(20),
                        phone VARCHAR(15),
                        local VARCHAR(20),
                        domain VARCHAR(20),
                        passwd VARCHAR(40),
                        payments VARCHAR(1000),
                        lat DOUBLE PRECISION,
                        lng DOUBLE PRECISION,
                        kind INTEGER
                        );
                    ''')

    # 사용자 테이블 primary key 만들기
    sql_arr.append(f''' ALTER TABLE client
                        ADD COLUMN uid SERIAL PRIMARY KEY
                    ''')

    # 예약 table
    # TODO: 요일은 어떻게?
    sql_arr.append(f''' CREATE TABLE appointment(
                        aid SERIAL PRIMARY KEY,
                        pid INTEGER REFERENCES patient(pid),
                        hid INTEGER REFERENCES hospital(hid),
                        time TIME,
                        date DATE,
                        subject VARCHAR(20),
                        confirm INTEGER,
                        uid INTEGER REFERENCES client(uid)
                        );
                    ''')

    # 자주가는 병원 table
    sql_arr.append(f''' CREATE TABLE f_hospital(
                        fid SERIAL PRIMARY KEY,
                        hid INTEGER REFERENCES hospital(hid),
                        uid INTEGER REFERENCES client(uid)
                        );
                    ''')

    # 상점 테이블
    sql_arr.append(f''' CREATE TABLE store(
                        sid SERIAL PRIMARY KEY,
                        kind INTEGER,
                        lng double precision,
                        lat double precision,
                        addr VARCHAR(100),
                        name VARCHAR(200)
                        );
                    ''')

    # 약국 기록 테이블 -> 처방전 테이블로 바꿈
    sql_arr.append(f''' CREATE TABLE prescription(
                        prid SERIAL PRIMARY KEY,
                        hid INTEGER REFERENCES hospital(hid),
                        sid INTEGER REFERENCES store(sid),
                        pid INTEGER REFERENCES patient(pid),
                        presc_time time,
                        presc_date date,
                        prepare_time time,
                        prepare_date date,
                        presc_done INTEGER,
                        uid INTEGER REFERENCES client(uid),
                        etc VARCHAR(1000)
                        );
                    ''')
              
 
    
    # 사용자 - 병원 테이블
    sql_arr.append(f''' CREATE TABLE h_client(
                        hurid SERIAL PRIMARY KEY,
                        uid INTEGER REFERENCES client(uid),
                        hid INTEGER REFERENCES hospital(hid)
                        );
                    ''')
     
    # 사용자 - 상점 테이블
    sql_arr.append(f''' CREATE TABLE s_client(
                        surid SERIAL PRIMARY KEY,
                        uid INTEGER REFERENCES client(uid),
                        sid INTEGER REFERENCES store(sid)
                        );
                    ''')
    
    # 병원 진료과목 테이블
    sql_arr.append(f''' CREATE TABLE h_subject(
                        hsid SERIAL PRIMARY KEY,
                        hid INTEGER REFERENCES hospital(hid),
                        subject VARCHAR(30)
                        );
                    ''')
    
    # 처방전_약 테이블
    sql_arr.append(f''' CREATE TABLE p_medicine(
                        pmid SERIAL PRIMARY KEY,
                        prid INTEGER REFERENCES prescription(prid),
                        name VARCHAR(30),
                        total INTEGER,
                        day INTEGER,
                        amount VARCHAR(30)
                        );
                    ''')

    # 처방전 _ 안경 처방 테이블
    sql_arr.append(f''' CREATE TABLE p_eye(
                        peid SERIAL PRIMARY KEY,
                        prid INTEGER REFERENCES prescription(prid),
                        l_eye VARCHAR(30),
                        r_eye VARCHAR(30)
                        );
                    ''')

    sql = f'''CREATE TABLE {table_name} (
                name varchar(20),
                phone char(20)
            );
     '''

    check = True

    for i in range(len(total_tname)):
        try:
            conn = pg.connect(connect_string) #connect
            cur = conn.cursor() # cursor 가져옴
            cur.execute(check_sql[i])
            check = check and cur.fetchone()[0]
            conn.commit() #commit 해줌
            conn.close() #닫아줌
        except pg.OperationalError as e:
            print(e)

    for i in range(len(sql_arr)):
        try:
            conn = pg.connect(connect_string) #connect
            cur = conn.cursor() # cursor 가져옴
            if check is False:
                cur.execute(sql_arr[i]) #sql 실행
            conn.commit() #commit 해줌
            conn.close() #닫아줌
        except pg.OperationalError as e:
            print(e)

    return  "ok"


''' application 에서 사용되는 모든 table 을 drop
    모든 table 의 이름은 total_tname 으로 주어진다.
    total_tname 의 이름 순서는 create 할 때 dependency 가 없는 순이므로
    반대로 drop 을 해야 한다.
'''
def drop_table(total_tname):
    check_sql = []
    for table_name in reversed(total_tname):
            check_sql.append(f'''SELECT EXISTS(
                                SELECT relname 
                                FROM pg_class 
                                WHERE relname = \'{table_name}\');
                                ''')
    drop_sql = []
    for table_name in reversed(total_tname):
            drop_sql.append(f'''DROP TABLE {table_name};
                             ''')


    for i in range(len(total_tname)):
        try:
            conn = pg.connect(connect_string) #connect
            cur = conn.cursor() # cursor 가져옴
            #print(check_sql[i])
            cur.execute(check_sql[i])
            check = cur.fetchone()[0]
            if check is True:
                #print(sql_arr[i])
                cur.execute(drop_sql[i]) #sql 실행
            conn.commit() #commit 해줌
            conn.close() #닫아줌
        except pg.OperationalError as e:
            print(e)

    return  "ok"


# 이미 만들어진 table 에 primary key 를 추가한다
def make_id (table_name, id_name):
    sql = f'''ALTER TABLE {table_name}
              ADD COLUMN {id_name} SERIAL PRIMARY KEY
             '''
    try:
        conn = pg.connect(connect_string)  # DB 연결
        cur = conn.cursor()  # cursor 정하기
        cur.execute(sql)  # sql문 실행
        conn.commit()
        conn.close()
    except pg.OperationalError as e:
        print(e)


# TODO: 구현 안됨
''' table_name 에서 target 으로 주어진 조건으로 검색하여
    selection 으로 주어진 column 을 반환한다.
    selection 은 column name 의 list 이다.
    target 은 tuple list 로 이루어져 있다.
    각 tuple 의 첫번째 element 는 column name, 두번째 elemnet 는 value 이다.
    Value 의 모든 string 은 ' ' 처리 되어 있어야 한다.
'''
def search(table_name, selection, target, limit):

    select = ''
    where = ''

    for column in selection:
        select += 'T.' + column + ','
    select = select[:-1]

    for (column, value) in target:
        where += "T." + column + "=" + str(value) + " AND "
    where = where[:-5]
    
    sql = f'''SELECT {select}
              FROM {table_name} T
              WHERE {where}
              LIMIT {str(limit)}
        '''
    try:
        conn = pg.connect(connect_string)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        result = cur.fetchall()
        conn.close()
        return result
    except Exception as e:
        print(e)
        return []

''' table_name 에 해당하는 table 에 fields value 를 갖는 row 를 추가한다.
    input tuple list 이어야 하고, 
    각 tuple 의 첫번째 element 는 datatype,
    tuple 의 두번째 element 는 data 의 value 가 들어온다.
    value가 string 이면 ' ' 가 추가 되어 있어야 한다.
'''
def insert(table_name, input):

    fields = ""
    values = ""

    for data in input:
        fields += data[0] + ','
        values += str(data[1]) + ','
    fields = fields[:-1]
    values = values[:-1]

    sql = f'''INSERT INTO {table_name} ({fields})
              VALUES ({values});
            '''
    try:
        conn = pg.connect(connect_string)  # DB 연결
        cur = conn.cursor()  # cursor 정하기
        cur.execute(sql)  # sql문 실행
        conn.commit()
        conn.close()
    except pg.OperationalError as e:
        print(e)


''' table_name 에 해당하는 table 에서 target 의 값들로 select 된 entity 를 삭제한다.
    target 은 tuple list 이어야 하고, 
    각 tuple 의 첫번째 element 는 datatype 의 string, 두번째 element 는 value 이다.
    value의 모든 string 은 ' ' 가 추가 되어 있어야 한다.
    id_name 은 해당 table 의 id column 의 이름이다 ('id_name'으로 주어져야 함).
'''
def delete(table_name, target, id_name):

    where = ""
    for (data_type, value) in target:
        where += "T1." + data_type + "=" + str(value) + " AND "

    where = where[:-5]

    sql = f'''DELETE
              FROM {table_name} T
              WHERE T.{id_name} IN (SELECT T1.{id_name}
                             FROM {table_name} T1
                             WHERE {where}
                             LIMIT 1);
          '''
    try:
        conn = pg.connect(connect_string)  # DB 연결
        cur = conn.cursor()  # cursor 정하기
        cur.execute(sql)  # sql문 실행
        conn.commit()
        conn.close()
    except pg.OperationalError as e:
        print(e)


''' table_name 에 해당하는 table 에서
    target 의 값들로 select 된 entity 를 newData 의 값들로 수정한다.
    target, newData 는 tuple list 이어야 하고, 
    각 tuple 의 첫번째 element 는 datatype 의 string, 두번째 element 는 value 이다.
    value의 모든 string 은 ' ' 가 추가 되어 있어야 한다.
'''
def modify(table_name, target, newData, id_name):

    set_data = ""
    for (nData_type, nValue) in newData:
        set_data += nData_type + "=" + str(nValue) + ","
    set_data = set_data[:-1]

    where = ""
    for (tData_type, tValue) in target:
        where += "T." + tData_type + "=" + str(tValue) + " AND "
    where = where[:-5]
    

    sql = f'''UPDATE {table_name}
              SET {set_data}
              FROM (SELECT * 
                    FROM {table_name} T 
                    WHERE {where}
                    LIMIT 1) AS target
              WHERE {table_name}.{id_name} = target.{id_name};
          '''
    try:
        conn = pg.connect(connect_string)  # DB 연결
        cur = conn.cursor()  # cursor 정하기
        cur.execute(sql)  # sql문 실행
        conn.commit()
        conn.close()
    except pg.OperationalError as e:
        print(e)


def add_column(table_name, col_name, col_type):

    sql = f'''ALTER TABLE {table_name}
              ADD COLUMN {col_name} {col_type}
           '''
    try:
        conn = pg.connect(connect_string)  # DB 연결
        cur = conn.cursor()  # cursor 정하기
        cur.execute(sql)  # sql문 실행
        conn.commit()
        conn.close()
    except pg.OperationalError as e:
        print(e)


'''Execute parameter's sql
'''
def special_sql(sql):
    try:
        conn = pg.connect(connect_string)  # DB 연결
        cur = conn.cursor()  # cursor 정하기
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)  # sql문 실행
        conn.commit()
        if cur.description is not None:
            result = cur.fetchall()
        else:
            result = []
        conn.close()
        return result
    
    except pg.OperationalError as e:
        print(e)


if __name__ == ("__main__"):
    total_tname = ["hospital", "patient", "client", "appointment",  "f_hospital", "store",
                  "prescription", "h_client", "s_client", "h_subject", "p_medicine", "p_eye"]
    drop_table(total_tname)
    create_table(total_tname)
