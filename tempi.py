# このpyを実行するにはsudo権限が必要です。
# 権限がたりないとscanner.scan()でエラーになります。
# 20221123
# このコードは@geboさんのQiita記事を元に目指せ北海道@habingofitがWanaPi用に変更を加えたものです。
# https://qiita.com/gebo/items/67aca91d07e3d7fccc85
# Lineに通知する部分を、Symbol系ブロックチェーンに記録するように改造しました。

from bluepy import btle
import sys
import time
import datetime
import to_float_from_11073_32bit_float as tofl
import to_date_time as todt
import sqlite3

# define
SERVICE_UUID="00001809-0000-1000-8000-00805f9b34fb"
MYADDRESS="NCQRNQBQOIRWJM6MUK2D4SFD55EV46YYNBNYM2A"
MYPLACE="bodytemp"
WANAPI_MOSAIC="75706ADB11C869EE"

# global
BLE_ADDRESS="64:33:db:89:30:e0"
rawfromaddress = MYADDRESS
rawtoaddress = MYADDRESS
myplace = 'bodytemp'
device = "A&D;6433db8930e0;"
WmosaicID = WANAPI_MOSAIC

def scan():
    try:
        scanner = btle.Scanner(0)
        devices = scanner.scan(3.0)

        for device in devices:
            #print(f'SCAN BLE_ADDR：{device.addr}')

            if(device.addr.lower()==BLE_ADDRESS.lower()):
                print("Find!")
                return True
    except:
        print("scan Error!")
        return False
    print("---")
    return False

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print("Indicate Handle = " + hex(cHandle))
        print("Flags = " + hex(data[0]))
        print("C1:Temperature Measurement Value(Celsius) = " + hex(data[1])+":"+hex(data[2])+":"+hex(data[3])+":"+hex(data[4]))
        print("C3:Time Stamp = " + hex(data[5])+":"+hex(data[6])+":"+hex(data[7])+":"+hex(data[8])+":"+hex(data[9])+":"+hex(data[10])+":"+hex(data[11]))

        temp = tofl.to_float_from_11073_32bit_float(data[1:5])
        print("temp = " + str(temp))
        #timestamp = todt.to_date_time(data[5:12])
        timestamp = datetime.datetime.now()
        timestampstr = timestamp.strftime('%Y/%m/%d %H:%M:%S')
        print("timestamp = " + timestampstr)

        parent=myplace
        child=device+str(temp)
        created_at=timestampstr
        con = sqlite3.connect('/home/pi/wanapi2/db/shizuinet.db')
        cur = con.cursor()
        sql = 'SELECT max(id), id FROM transactions'
        cur = con.cursor()
        cur.execute(sql)
        for row in cur:
            print(str(row[0]))
            id = row[0]+1

        sql = 'INSERT INTO transactions (id, sender, receiver, mosaic, parent, child, created_at)  VALUES (?,?,?,?,?,?,?)'
        data = [id, rawfromaddress, rawtoaddress, WmosaicID, parent, child, created_at]
        cur.execute(sql, data)
        #print(data)
        con.commit()
        con.close()

def main():
    #
    # Scan
    #
    print("<Scan Start>")
    while True:
        scanresult = scan()
        if( scanresult==True):
            break
        time.sleep(3)
    print("Scan End")


    #
    # Connect
    #
    print("Connect Start")
    try:
        peripheral = btle.Peripheral()
        peripheral.connect(BLE_ADDRESS)
    except:
        print("connect Error!")
        sys.exit(0)

    print("Connected!")
    service = peripheral.getServiceByUUID(SERVICE_UUID)
    peripheral.withDelegate(MyDelegate())

    # Enable Indicate
    peripheral.writeCharacteristic(0x0013, b'\x02\x00', True)

    # 通知を待機する
    print("Indicate Wait...")
    try:
        TIMEOUT = 3.0
        while True:
            if peripheral.waitForNotifications(TIMEOUT):
                # handleNotification()が呼び出された
                continue

            # handleNotification()がTIMEOUT秒だけ待っても呼び出されなかった
            print("wait...")
    except:
        print("except!")

    print("<end>")

if __name__ == '__main__':
    print(sys.argv[0])
    #gloval BLE_ADDRESS
    #BLE_ADDRESS = sys.argv[2]
    print("BLE device = " + BLE_ADDRESS)

    while True:
        main()
        time.sleep(3)
