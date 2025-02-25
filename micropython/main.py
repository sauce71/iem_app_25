from time import sleep
import json
from wlan import connect
import uasyncio
from nanoweb import Nanoweb
import urequests

import sensors
from html_functions import naw_write_http_header, render_template
from leds import blink
import buttons
from thingspeak import thingspeak_publish_data
from machine import WDT
import gc


PUBLISH_INTERVAL_MS = 60000 # Endre denne til passende intervall



sta_if = connect() # Kobler til trådløst nettverk

naw = Nanoweb() # Lager en instans av Nanoweb

data = dict(
    bme = dict(temperature=0, humidity=0, pressure=0),
    ags = dict(tvoc=0),
    aht = dict(temperature=0, humidity=0),
    )

inputs = dict(button_1=False)

wdt = WDT(timeout=8000)
    
@naw.route("/")
def index(request):
    naw_write_http_header(request)
    html = render_template(
        'index.html',
        temperature_bme=str(data['bme']['temperature']),
        humidity_bme=str(data['bme']['humidity']),
        pressure=str(data['bme']['pressure']),        
        tVOC=str(data['ags']['tvoc']),
        temperature_aht=str(data['aht']['temperature']),
        humidity_aht=str(data['aht']['humidity']),
        )
    await request.write(html)


@naw.route("/api/data")
def api_data(request):
    naw_write_http_header(request, content_type='application/json')
    await request.write(json.dumps(data))

async def control_loop():
    while True:
        thingspeak_publish_data(data)
        wdt.feed()
        gc.collect()
        for i in range(PUBLISH_INTERVAL_MS // 6000):
            wdt.feed()
            await uasyncio.sleep_ms(6000) 
        
async def wdt_loop():
    wdt = WDT(timeout=8000)
    while True:
        wdt.feed()
        await uasyncio.sleep_ms(6000)

loop = uasyncio.get_event_loop()
loop.create_task(sensors.collect_sensors_data(data, False))
loop.create_task(buttons.wait_for_buttons(inputs))
loop.create_task(naw.run())
loop.create_task(control_loop())
loop.create_task(blink())
#loop.create_task(wdt_loop())

loop.run_forever()
    

