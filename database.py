import sqlite3

DB_NAME = 'myDatabase.db'



def get_Connection():
    conn=sqlite3.connect(DB_NAME)
    return conn

def create_table():
    conn=get_Connection()
    cursor=conn.cursor()
    cursor.execute('''
                   create table  if not exists devices(
                       device_id TEXT,
                       intensity INTEGER,
                       device_status INTEGER,
                       temperature REAL,
                       auto_brightness_status INTEGER,
                       auto_motion_status INTEGER,
                       power INTEGER,
                       lux INTEGER,
                       timestamp DATETIME DEFAULT (datetime('now','localtime'))
                    )
                   ''')
     
    conn.commit()
    conn.close()
    
    
def insert_Data(device_id,intensity,device_status,temperature,auto_brightness_status,auto_motion_status,power,lux):
    conn = get_Connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO devices (device_id, intensity, device_status, temperature,auto_brightness_status,auto_motion_status,power,lux)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (device_id, intensity, device_status, temperature,auto_brightness_status,auto_motion_status,power,lux))
    conn.commit()
    conn.close()
    
def get_all_data():
        conn = get_Connection()
        cursor=conn.cursor()
        cursor.execute('select * from devices')
        data=cursor.fetchall()
        conn.close
        return data 
    
    
    
def get_calculate_power():
    conn=get_Connection()
    cursor = conn.cursor()
    query = """
                 WITH RECURSIVE hours(h) AS (
                 SELECT 0
                 UNION ALL
                 SELECT h+1 FROM hours WHERE h < 23
                 )
                 SELECT 
                 printf('%02d:00', hours.h) AS hours_slot,
                 IFNULL(ROUND(AVG(d.power), 2), 0) AS power_consumption
                 FROM hours
                 LEFT JOIN devices d
                 ON strftime('%H', d.timestamp) = printf('%02d', hours.h)
                 AND date(d.timestamp) = date('now')
                 GROUP BY hours.h
                 ORDER BY hours.h;
              """
              
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return[
        {"hour":row[0],"power":row[1]} for row in data
    ]