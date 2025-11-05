# %%
print('Hello World')

from hashlib import sha1
import requests
import urllib.parse
import hmac
import hashlib
import binascii
import numpy as np
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo  # built-in from Python 3.9 onwards

devId = 3003758
key = 'cb5321b0-e83e-45ab-a98e-f5d154599d59'
keyBytes = key.encode('utf-8')

def getUrl(request):
    request = request + ('&' if ('?' in request) else '?')
    raw = request+'devid={0}'.format(devId)
    rawBytes = raw.encode('utf-8')
    hashed = hmac.new(keyBytes, rawBytes, sha1)
    signature = hashed.hexdigest()
    return 'https://timetableapi.ptv.vic.gov.au'+raw+'&signature={1}'.format(devId, signature)
print(getUrl('/v3/routes'))

print(getUrl('/v3/departures/route_type/0/stop/1165?max_results=20&look_backwards=false'))
print(getUrl('/v3/stops/location/-37.87613416084298,144.99491888592993'))

# === TRAM - ROUTE  67 + STOP 41 ===
# Disruptions - Route 67 Trams
print(getUrl('/v3/disruptions/route/913'))

# Should check stopping pattern for each run that is displayed
# Not using pattern atm - print(getUrl('/v3/pattern/run/62649/route_type/1'))
print(getUrl('/v3/runs/62649/route_type/1'))

# === TRAIN - SANDRINGHAM LINE + RIPPONLEA ===
# Disruptions - Sandringham Trains
print(getUrl('/v3/disruptions/route/12'))

# 3175 - stop ID for trams towards city
# 3176 - stop ID for trams from city
# 1165 - ripponlea station
# Route 67 route ID - 913 - melb university to carnegie 
# Sandringham route ID 12

def urlToDataframe(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error {response.status_code}: Failed to fetch data from {url}")
        return None

    data = response.json()
    departures = data.get('departures', [])
    if not departures:
        print("No departures found in the response.")
        return pd.DataFrame()
    
    df = pd.DataFrame(data['departures'])
    df['scheduled_departure_utc'] = pd.to_datetime(df['scheduled_departure_utc'])
    df['estimated_departure_utc'] = pd.to_datetime(df['estimated_departure_utc'])
    df['delay_min'] = (df['estimated_departure_utc'] - df['scheduled_departure_utc']).dt.total_seconds() / 60
    
    # --- Add local time (Australia/Melbourne) ---
    melb_tz = ZoneInfo("Australia/Melbourne")
    df['scheduled_departure_local'] = df['scheduled_departure_utc'].dt.tz_convert(melb_tz)
    df['estimated_departure_local'] = df['estimated_departure_utc'].dt.tz_convert(melb_tz)
    
    return df

df_67_toCity = urlToDataframe(getUrl('/v3/departures/route_type/1/stop/3175?max_results=10&look_backwards=false'))
df_67_fromCity = urlToDataframe(getUrl('/v3/departures/route_type/1/stop/3176?max_results=10&look_backwards=false'))
df_Ripponlea = urlToDataframe(getUrl('/v3/departures/route_type/0/stop/1165?max_results=10&look_backwards=false'))

df_Ripp_toCity = df_Ripponlea[df_Ripponlea['direction_id']==1]
df_Ripp_fromCity = df_Ripponlea[df_Ripponlea['direction_id']==12]
