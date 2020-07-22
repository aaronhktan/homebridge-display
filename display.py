from RPLCD.gpio import CharLCD # Driver for LCD
from RPi import GPIO # To suppress warnings
import paho.mqtt.client as mqtt # For MQTT

import threading

temperature = ''
humidity = ''
eCO2 = ''
pressure = ''
lux = ''

lock = threading.Lock()

GPIO.setwarnings(False)
lcd = CharLCD(pin_rs=36, pin_e=32, pins_data=[37, 33, 31, 29],
numbering_mode=GPIO.BOARD, cols=16, rows=2, charmap='A02')

def on_connect(client, userdata, flags, rc):
  print('Connected with result code {}'.format(rc))
  client.subscribe('dht22/temperature')
  client.subscribe('dht22/humidity')
  client.subscribe('bmp280/pressure')
  client.subscribe('sgp30/eCO2')

def on_message(client, userdata, msg):
  print(msg.payload.decode('utf-8'))
  if msg.topic == 'dht22/temperature':
    global temperature
    temperature = msg.payload.decode('utf-8')[:4]
  elif msg.topic == 'dht22/humidity':
    global humidity
    humidity = msg.payload.decode('utf-8')[:4]
  elif msg.topic == 'bmp280/pressure':
    global pressure
    pressure = msg.payload.decode('utf-8')[:4]
  elif msg.topic == 'sgp30/eCO2':
    global eCO2
    eCO2 = msg.payload.decode('utf-8')[:4]
  else:
    print('Unknown topic: ', msg.topic, msg.payload)

def printValues():
  print('Values: {}C {}% {}ppm {}hPa'.format(temperature, humidity, pressure, eCO2))

  with lock:
    lcd.cursor_pos = (0, 0)
    lcd.write_string('{}C, {}%'.format(temperature, humidity).ljust(16))
    lcd.cursor_pos = (1, 0)
    lcd.write_string('{}ppm, {}hPa'.format(eCO2, pressure).ljust(16))

  threading.Timer(10, printValues).start()

lcd.write_string('...C ...%')
lcd.cursor_pos = (1, 0)
lcd.write_string('...ppm ...hPa')

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect('192.168.0.38', 1883, 60)

try:
  client.loop_start()
except KeyboardInterrupt:
  pass

printValues()

