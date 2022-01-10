from Watcher import GPS, OLED
from machine import Pin
import machine,dht,utime,time,network,urequests
gps = GPS()
oled = OLED()
d4 = Pin(2, Pin.OUT, value=0)


def loop():
    global gps, oled, api, d4
    gpsStr = b''
    gpsReading = False
    if d4.value() == 0:
        d4.value(1)
    else:
        d4.value(0)
    while True:
        data = gps.getGPSInfo()
        if data and (gpsReading or ('$GPRMC' in data)) :
            gpsStr += data
            if '\n' in data:
                gpsReading = False            
                lat, long, today, now = gps.convertGPS(gpsStr)                
                oled.displayGPS(lat, long, today, now)
                gpsStr = b''                
                break
            else:
                gpsReading = True
def main():
    while True:
        loop()
main()