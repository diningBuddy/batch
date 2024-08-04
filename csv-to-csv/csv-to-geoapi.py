import os

import pandas as pd
import requests

# 네이버 지오코딩 API 키 설정
client_id = os.getenv('NAVER_CLIENT_ID')
client_secret = os.getenv('NAVER_CLIENT_SECRET')

df = pd.read_csv('../csv/restaurants.csv')


def get_coordinates(address):
  url = f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={address}"
  headers = {
    "X-NCP-APIGW-API-KEY-ID": client_id,
    "X-NCP-APIGW-API-KEY": client_secret
  }
  response = requests.get(url, headers=headers)
  if response.status_code == 200:
    data = response.json()
    if data['addresses']:
      x = data['addresses'][0]['x']
      y = data['addresses'][0]['y']
      return x, y
  else:
    print("Error Code:", response.status_code)
    print(response.text)
  return None, None


df['longitude'] = ''
df['latitude'] = ''

for idx, row in df.iterrows():
  address = row['address']
  x, y = get_coordinates(address)
  df.at[idx, 'longitude'] = x
  df.at[idx, 'latitude'] = y

df.to_csv('restaurants.csv', index=False)
