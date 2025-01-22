import gc
from time import sleep
from machine import Pin, I2C
import uasyncio
from BME280 import BME280
import aht
from ags10 import AGS10



i2c = I2C(0, scl=Pin(17), sda=Pin(16))
bme = BME280(i2c=i2c, address=0x77)
aht_sensor = aht.AHT2x(i2c, crc=False)
ags_sensor = AGS10(i2c)


readings_bme_temperature = []
readings_bme_humidity = []
readings_bme_pressure = []
readings_ags_tvoc = []
readings_aht_temperature = []
readings_aht_humidity = []

async def read_bme():
    temperature = bme.read_temperature() / 100
    humidity = bme.read_humidity() / 1024
    pressure = bme.read_pressure() / 25600
    return temperature, humidity, pressure


async def read_ags():
    return ags_sensor.total_volatile_organic_compounds_ppb
    
    
async def read_aht():
    if aht_sensor.is_ready:
        temperature = aht_sensor.temperature
        humidity = aht_sensor.humidity  
    return temperature, humidity

def _pop0(l):
    if len(l) >= 60:
        l.pop(0)

def _mid(l):
    return sorted(l)[len(l)//2]
    

async def update_sensors_data(data):
    global readings_bme_temperature
    global readings_bme_humidity
    global readings_bme_pressure
    global readings_ags_tvoc
    global readings_aht_temperature
    global readings_aht_humidity

    temperature, humidity, pressure = await read_bme()
    readings_bme_temperature.append(temperature)
    readings_bme_humidity.append(humidity)
    readings_bme_pressure.append(pressure)
  
    tvoc = await read_ags()
    readings_ags_tvoc.append(tvoc)
   
    temperature, humidity = await read_aht()
    readings_aht_temperature.append(temperature)
    readings_aht_humidity.append(humidity)
 
    _pop0(readings_bme_temperature)
    _pop0(readings_bme_humidity)
    _pop0(readings_bme_pressure)

    _pop0(readings_ags_tvoc)

    _pop0(readings_aht_temperature)
    _pop0(readings_aht_humidity)
     
    data['bme']['temperature'] = _mid(readings_bme_temperature)
    data['bme']['humidity'] = _mid(readings_bme_humidity)
    data['bme']['pressure'] = _mid(readings_bme_pressure)
    data['ags']['tvoc'] = _mid(readings_ags_tvoc)
    data['aht']['humidity'] = _mid(readings_aht_humidity)
    data['aht']['temperature'] = _mid(readings_aht_temperature)


async def collect_sensors_data(data, test=False):    
    while True:
        await update_sensors_data(data)
        if test:
            print(data)
    
        await uasyncio.sleep_ms(5000)

def test():
    data = dict(
        bme = dict(temperature=0, humidity=0, pressure=0),
        ags = dict(tvoc=0),
        aht = dict(temperature=0, humidity=0),
    )
    loop = uasyncio.get_event_loop()
    loop.create_task(collect_sensors_data(data, True))
    loop.run_forever()

if __name__ == '__main__':
    test()
    