import requests

# https://how2electronics.com/send-sensor-data-to-thingspeak-with-raspberry-pi-pico-w/

HTTP_HEADERS = {'Content-Type': 'application/json'}


THINGSPEAK_WRITE_API_KEY = '95N5X02QHYLKI573' # HER MÅ DERE BRUKE EGEN!!!
THINGSPEAK_WRITE_URL = f'http://api.thingspeak.com/update?api_key={THINGSPEAK_WRITE_API_KEY}'

def thingspeak_publish_data(data):
    """
    data = dict(
        bme = dict(temperature=0, pressure=0),
        ags = dict(tvoc=0),
        aht = dict(temperature=0, humidity=0),
        )

    """
    payload = {
        'field1' : data["bme"]["temperature"],
        'field2' : data["bme"]["pressure"],
        'field3' : data["ags"]["tvoc"],
        'field4' : data["aht"]["temperature"],
        'field5' : data["aht"]["humidity"],
        }
    #print(payload)
    r = requests.post(THINGSPEAK_WRITE_URL, json = payload, headers = HTTP_HEADERS)
    return r
    
   
    

if __name__ == '__main__':
    from wlan import connect
    sta_if = connect()
    data = dict(
        bme = dict(temperature=0, humidity=0, pressure=0),
        ags = dict(tvoc=0),
        aht = dict(temperature=0, humidity=0),
        )

    r = thingspeak_publish_data(data)
    print(r.status_code)
    print(r.text)
    
