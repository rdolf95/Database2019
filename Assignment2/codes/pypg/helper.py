import psycopg2 as pg
import psycopg2.extras


db_connector = {
    'host': "localhost",
    'user': "postgres",
    'dbname': "postgres",
}

connect_string = "host={host} user={user} dbname={dbname}".format(
    **db_connector)

#table_name이라는 이름의 table 만든다.
def create_table(table_name):


    check_sql = f'''SELECT EXISTS(
                    SELECT relname 
                    FROM pg_class 
                    WHERE relname = \'{table_name}\')
                ;
         '''

    sql = f'''CREATE TABLE {table_name} (
                name varchar(20),
                phone char(20)
            );
     '''
    try:
        conn = pg.connect(connect_string) #connect
        cur = conn.cursor() # cursor 가져옴
        cur.execute(check_sql)
        check = cur.fetchone()[0]
        if check is False:
            cur.execute(sql) #sql 실행
        conn.commit() #commit 해줌
        conn.close() #닫아줌
    except pg.OperationalError as e:
        print(e)

    return  check

def copy_csv(file_name, table_name):
    try:
        conn = pg.connect(connect_string)  # DB 연결
        cur = conn.cursor()
        with open(file_name, 'r') as f:
            next(f)  # Skip the header row.
            cur.copy_from(f, table_name, sep=',')
        conn.commit()
        conn.close()

    except pg.OperationalError as e:
        print(e)


def make_id (table_name):
    sql = f'''ALTER TABLE {table_name}
              ADD COLUMN id SERIAL PRIMARY KEY
             '''
    try:
        conn = pg.connect(connect_string)  # DB 연결
        cur = conn.cursor()  # cursor 정하기
        cur.execute(sql)  # sql문 실행
        conn.commit()
        conn.close()
    except pg.OperationalError as e:
        print(e)

def search_contact(name):
    name = name + "%"
    sql = f'''SELECT C.name, C.phone
              FROM contact C
              WHERE C.name LIKE \'{name}\'
              ORDER BY name;
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

def insert_address(name, pnum):

    sql = f'''INSERT INTO contact
              VALUES (\'{name}\', \'{pnum}\');
            '''
    try:
        conn = pg.connect(connect_string)  # DB 연결
        cur = conn.cursor()  # cursor 정하기
        cur.execute(sql)  # sql문 실행
        conn.commit()
        conn.close()
    except pg.OperationalError as e:
        print(e)

def delete_address(name):
    sql = f'''DELETE
              FROM contact C
              WHERE C.id IN (SELECT C1.id
                             FROM contact C1
                             WHERE C1.name = \'{name}\'
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


def modify_address(name, pnum, newName, newPnum):
    sql = f'''UPDATE contact
              SET name = \'{newName}\', phone = \'{newPnum}\'
              FROM (SELECT * 
                    FROM contact C 
                    WHERE C.name = \'{name}\' AND C.phone = \'{pnum}\'
                    LIMIT 1) AS target
              WHERE contact.id = target.id;
          '''
    try:
        conn = pg.connect(connect_string)  # DB 연결
        cur = conn.cursor()  # cursor 정하기
        cur.execute(sql)  # sql문 실행
        conn.commit()
        conn.close()
    except pg.OperationalError as e:
        print(e)

