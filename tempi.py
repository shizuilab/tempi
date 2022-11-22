# このpyを実行するにはsudo権限が必要です。
# 権限がたりないとscanner.scan()でエラーになります。
from bluepy import btle
import sys
import time
import to_float_from_11073_32bit_float as tofl
import to_date_time as todt

# define
SERVICE_UUID="00001809-0000-1000-8000-00805f9b34fb"

# global
BLE_ADDRESS="64:33:db:89:30:e0"

def scan():
    try:
        scanner = btle.Scanner(0)
        devices = scanner.scan(3.0)

        for device in devices:
            print(f'SCAN BLE_ADDR：{device.addr}')

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
        timestamp = todt.to_date_time(data[5:12])
        print("timestamp = " + timestamp)

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
