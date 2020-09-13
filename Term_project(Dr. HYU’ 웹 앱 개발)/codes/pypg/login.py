import psycopg2 as pg
import psycopg2.extras
import helper as helper


db_connector = {
    'host': "localhost",
    'user': "postgres",
    'dbname': "postgres",
}

connect_string = "host={host} user={user} dbname={dbname}".format(
    **db_connector)


#table_name 이라는 table 에 file_name 의 csv file 을 copy 한다
def copy_csv(file_name, table_name):
    try:
        conn = pg.connect(connect_string)  # DB 연결
        cur = conn.cursor()
        with open(file_name, 'r') as f:
            next(f)  # Skip the header row.
            cur.copy_from(f, table_name, sep=',', columns=['name', 'phone', 'local', 'domain', 'passwd', 'lat', 'lng'])
        conn.commit()
        conn.close()

    except pg.OperationalError as e:
        print(e)


def copy_csv2():

    sql = f'''  \COPY client(name, phone, local, domain, passwd, lat, lng) 
                FROM 'customers.csv' CSV HEADER DELIMITER ','
           '''
    try:
        conn = pg.connect(connect_string)  # DB 연결
        cur = conn.cursor()  # cursor 정하기
        cur.execute(sql)  # sql문 실행
        conn.commit()
        conn.close()
    except pg.OperationalError as e:
        print(e)

if __name__ == ("__main__"):
    copy_csv('customers.csv', 'client')
    #helper.add_column('hospital','kind','INTEGER')
    