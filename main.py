from machine import Pin
import network
import socket
import utime
import secrets
def ultra():
 trigger.low()
 utime.sleep_us(2)
 trigger.high()
 utime.sleep_us(5)
 trigger.low()
 while echo.value() == 0:
 signaloff = utime.ticks_us()
 while echo.value() == 1:
 signalon = utime.ticks_us()
 timepassed = signalon - signaloff
 distance = (timepassed * 0.0343) / 2
 distance = round(distance,2)
 return distance
trigger = Pin(3, Pin.OUT)
echo = Pin(2, Pin.IN)
led = Pin("LED", Pin.OUT)
SensorState = 'Sensor State Unknown'
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)
print("Wifi connection = {}".format(wlan.isconnected()))
html = """<!DOCTYPE html><html>
<head><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; textalign: center;}
.buttonGreen { background-color: #4CAF50; border: 2px solid #000000;; color: white;
padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block;
font-size: 16px; margin: 4px 2px; cursor: pointer; }
.buttonRed { background-color: #D11D53; border: 2px solid #000000;; color: white;
padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block;
font-size: 16px; margin: 4px 2px; cursor: pointer; }
text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
</style></head>
<body>
<center><h2>Distance Control Panel</h2></center><br>
<form><center>
<center> <button class="buttonGreen" name="ULTRA" value="on" type="submit">Read
Distance</button>
<br><br>
<center> <button class="buttonRed" name="ULTRA" value="off"
type="submit">STOP</button>
</form>
<br><br>
<p>%s<p>
</body></html>
"""
max_wait = 10
while max_wait > 0:
 if wlan.status() < 0 or wlan.status() >= 3:
 break
 max_wait -= 1
 print('waiting for connection...')
 utime.sleep(1)
print("Wifi connection = {}".format(wlan.isconnected()))
# Handle connection error
if wlan.status() != 3:
 raise RuntimeError('network connection failed')
else:
 print('Connected')
 status = wlan.ifconfig()
 print( 'ip = ' + status[0] )

# Open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
print('listening on', addr)
distance_cm = "unknown"
# Listen for connections, serve client
while True:
 try:
 cl, addr = s.accept()
 print('client connected from', addr)
 request = cl.recv(1024)
 print("request:")
 print(request)
 request = str(request)
 Sensor_on = request.find('ULTRA=on')
 Sensor_off = request.find('ULTRA=off')

 print( 'sensor on = ' + str(Sensor_on))
 print( 'sensor off = ' + str(Sensor_off))

 if Sensor_on == 8:
 print("sensor on")
 led.value(1)
 distance_cm = str(ultra())
 print("the distance = " + distance_cm + " cm")
 if Sensor_off == 8:
 print("sensor off")
 led.value(0)
 distance_cm = str("unknown")
 print("the distance = " + distance_cm + " cm")

 SensorState = "sensor is OFF" if led.value() == 0 else "sensor is ON"

 # Create and send response
 stateis = SensorState + " and " + "the distance = " + distance_cm + " cm"
 response = html % stateis
 cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
 cl.send(response)
 cl.close()

 except OSError as e:
 cl.close()
 print('connection closed')
