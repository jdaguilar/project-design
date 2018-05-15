# sniffer.py
# Diseno electronico 2018-01
#
# Grupo 5
# Jorge Aguilar Orozco
# Karim Dasuki Garcia
# Juan De La Hoz Fonseca
# Jorge Lambrano Arroyo
#

import socket
import struct
import textwrap
import time
import pymysql
import datetime
#import sniffer

TAB_1 = '\t - '
TAB_2 = '\t\t - '
TAB_3 = '\t\t\t - '
TAB_4 = '\t\t\t\t - '

DATA_TAB_1 = '\t '
DATA_TAB_2 = '\t\t '
DATA_TAB_3 = '\t\t\t '
DATA_TAB_4 = '\t\t\t\t '

#................................................................
# this depends of our amazon instance
connection = pymysql.connect(host='designdatabase2.cg6tv9ndrugo.us-west-2.rds.amazonaws.com',
                             user='admin',
                             password='admin123456',
                             db='designdatabase',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

#.................................................................

def main():
    conn = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
    while True:
        #read all posible value from ports
        raw_dat, add = conn.recvfrom(65536)

        #unpacked ethernet frame
        eth_proto, data = ethernet_frame(raw_dat)

        # 8 for IPv4
        if eth_proto == 8:
            # print("prtocol IPv4")
            (proto, target, data) = ipv4_packet(data)
            # print(proto)
            # 17 for UDP
            if proto == 17:
                # print("protocol UDP")
                dest_port, lenght, data = upd_segment(data)

                # port 3388
                if dest_port == 3389:
                    #Se convierten los datos de hexa a string
                    info = str(data)
                    index_E = info.find('E')

                    if data:

                        try:
                            itIs, EventDef, datetime, lat, lon, vel, id_syrus = get_message(info[index_E:len(other_str)- 1])
                            rpm = get_rpm(info)
                        except ValueError:
                            continue
                            #print(DATA_TAB_3 + "Invalid Format...\n")

                        if itIs == 1:
                            #print(DATA_TAB_3 + "Latitud es "+str(lat)+"  Longitud "+str(lon) )
                            #print(DATA_TAB_3 + "la hora es "+ str(Hour)+":"+str(Minutes)+":"+str(Seconds))
                            #print(DATA_TAB_3 + "La fecha es "+str(Day)+"/"+str(Month)+"/"+str(Year))
                            #print(DATA_TAB_3 + "la velocidad es "+str(vel))
                            db(lat, lon, id_syrus, datetime, vel, rpm)

#.................................................................

#unpacked ethernet frame
def ethernet_frame(data):
    dest_mac, src_mac, proto = struct.unpack('! 6s 6s H', data[:14])
    return socket.htons(proto), data[14:]

#.................................................................

#def print_frame():


#.................................................................

#unpacks IPV4 packets
def ipv4_packet(data):
    version_header_lenght = data[0]
    version = version_header_lenght >> 4
    header_length = (version_header_lenght & 15) * 4
    ttl, proto, src, target = struct.unpack('! 8x B B 2x 4s 4s', data[:20])
    #return ipv4_fmt(src), ipv4_fmt(target), data[header_length:]
    return proto, target, data[header_length:]

#.................................................................

def upd_segment(data):
    src_port, dest_port, size = struct.unpack('! H H 2x H', data[:8])
    return dest_port, size, data[8:]

#.................................................................

def get_message(m):
    if m[0:2] == "EV":
        #print("Mensaje recibido: " + m )
        #print("Procesando...")
        # Confirmation
        itIs = 1
        # Event
        EventDef = int(m[4:6])
        vel=float(m[34:37])

        #id_syrus
        id_syrus = m[45:60]
        #print (id_syrus)

        # Time
        #secn, Year, Month, Day, Hour, Minutes, Seconds = getTime(int(m[6:10]), int(m[10]), int(m[11:16]))
        ts_epoch = get_seconds(int(m[6:10]), int(m[10]), int(m[11:16]))
        my_datetime = datetime.datetime.fromtimestamp(ts_epoch).strftime('%Y-%m-%d %H:%M:%S')

        #print(my_datetime)

        # Coordinates
        lat = float(m[17:19]) + (float(m[19:24]) / 100000.0)
        if m[16] == "-":
            lat = -lat
        lon = float(m[25:28]) + (float(m[28:33]) / 100000.0)
        if m[24] == "-":
            lon = -lon

    else:
        vel = 0
        EventDef = 0
        lat = 0
        lon = 0
        itIs = 0
        my_datetime = '0000-00-00 00:00:00'
        id_syrus = 0
    return itIs, EventDef, my_datetime, lat, lon, vel, id_syrus

#..................................................................

def get_seconds(wks, days, scnd):
     seco = wks * 7 * 24 * 60 * 60 + (days + 3657) * 24 * 60 * 60 + scnd - 5 * 60 * 60
     return seco

#-------------------------------------------------------------------------

#def getTime(wks, days, scnd):
#    seco = wks * 7 * 24 * 60 * 60 + (days + 3657) * 24 * 60 * 60 + scnd
#    # + 5 * 60 * 60
#    t = time.localtime(seco)
#    posmonths = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
#    Year = t.tm_year
#    Month = posmonths[t.tm_mon - 1]
#    Day = t.tm_mday
#    Hour = t.tm_hour
#    Minutes = t.tm_min
#    Seconds = t.tm_sec
#    return seco, Year, Month, Day, Hour, Minutes, Seconds
#.................................................................

#def db(datetime,latitude,longitud,Velocidad,id_syrus):
def db(latitude, longitude, id_syrus, datetime, velocity, rpm):
    try:

        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `position_data` (`latitude`, `longitude`, `id_syrus`, `datetime`, `velocity`, `rpm`) VALUES ( %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (str(latitude), str(longitude), id_syrus, datetime, str(velocity), , str(rpm)))

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()

    finally:
        #connection.close()
        print("ok Db")
        
    pass


# this is the main function

def get_rpm(info):
    try:
        rpm = int(info[4:8])
    except ValueError:
        rpm = -1
    return rpm 

#.....................................................................
if __name__ == '__main__':
    main()
