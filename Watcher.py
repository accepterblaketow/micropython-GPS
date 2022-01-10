from machine import UART, Pin, I2C
import time, ssd1306, ujson
import urequests as requests
import machine,dht,utime,time,network,urequests
import gc

def go_wifi():#裝置連WIFI
    try:
        wifi.active(False)
        wifi.active(True)
        wifi.connect('blake','12345678')
        print('start to connect wifi')
        for i in range(20):
            print('try to connect wifi in {}s'.format(i))
            utime.sleep(1)
            if wifi.isconnected():
                break
        if wifi.isconnected():
            print('WiFi connection OK!')
            print('Network Config=',wifi.ifconfig())
        else:
            print('WiFi connection Error')
    except Exception as e: print(e)
wifi=network.WLAN(network.STA_IF)
go_wifi()
i=0
class GPS:
    def __init__(self, bondRate=9600):
        self.com = UART(0, bondRate)
        self.com.init(bondRate)

    def utcDateTime(self, dateStr, timeStr, timeZone=8):#時間
        if dateStr == '' or timeStr == '':
            return None

        day = dateStr[0:2]
        month = dateStr[2:4]
        year = dateStr[4:6]
        hr = timeStr[0:2]
        min = timeStr[2:4]
        sec = timeStr[4:6]
        timeZone *= 3600

        t = time.mktime((int('20' + year), int(month), int(day),int(hr), int(min), int(sec), 0, 0))

        return time.localtime(t+timeZone)

    def latitude(self, d, h):#經度
        if d == '':
            return '0'

        hemi = '' if h == 'N' else '-'
        deg = int(d[0:2])
        min = str(float(d[2:]) / 60)[1:]

        return hemi + str(deg) + min

    def longitude(self, d, h):#緯度
        if d == '':
            return '0'

        hemi = '' if h == 'E' else '-'
        deg = int(d[0:3])
        min = str(float(d[3:]) / 60)[1:]

        return hemi + str(deg) + min

    def convertGPS(self, gpsStr):
        gps = gpsStr.split(b'\r\n')[0].decode('ascii').split(',')

        lat = self.latitude(gps[3], gps[4])  # N or S
        long = self.longitude(gps[5], gps[6]) # E or W
        today = ''
        now = ''
        tim = self.utcDateTime(gps[9], gps[1], 8)

        if tim != None:
            today = str(tim[0]) + '/' + str(tim[1]) + '/' + str(tim[2])
            now = str(tim[3]) + ':' + str(tim[4]) + ':' + str(tim[5])

        return (lat, long, today, now)

    def getGPSInfo(self):
        data = self.com.readline()
        return data

class OLED:
    def __init__(self, scl=13, sda=12):#初始化
        self.oled = ssd1306.SSD1306_I2C(
            128, 64,
            I2C(scl=Pin(scl), sda=Pin(sda), freq=100000)
        )
        self.oled.text("GPS RUNNING...", 0, 30)
        self.oled.show()

    def displayGPS(self, lat, long, today, now):#在OLED顯示and發送請求
        d11=dht.DHT11(machine.Pin(0))
        d11.measure()
        tmp="temperature: " + str(d11.temperature())
        hid="humidity: " + str(d11.humidity())
        lat = "Lat: " + lat
        long = "Long: " + long
        today="date: "+today
        now="now: " + now
        api_key='bVfPHgoiyLpqT1kFW89cGD'#發送http請求
        gc.collect()
        line_url='https://maker.ifttt.com/trigger/room_status/with/key/{}?value1={}'.format(api_key,lat+"<br>"+long+"<br>"+today+"<br>"+now+"<br>"+tmp+"<br>"+hid)
        line_res=urequests.get(line_url)
        gc.collect()
        line_res.close()
        time.sleep(4)
        self.oled.fill(0)
        self.oled.text(today, 0, 0)
        self.oled.text(now, 0, 10)
        self.oled.text(lat, 0, 20)
        self.oled.text(long, 0, 30)
        self.oled.text(tmp, 0, 40)
        self.oled.text(hid, 0, 50)
        self.oled.show()
        



