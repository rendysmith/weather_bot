import requests
from bs4 import BeautifulSoup
import time
import configparser
import os
import openai

config = configparser.ConfigParser()
path_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "config.ini"))
config.read(path_db)

def send_telegram(text: str):
    token = config.get('bot', 'token_tg')
    url = "https://api.telegram.org/bot"
    channel_id = config.get('bot', 'channel_id')
    url += token
    method = url + "/sendMessage"

    r = requests.post(method, data={
        "chat_id": channel_id,
        "text": text,
        "parse_mode": "Markdown"
          })

    if r.status_code != 200:
        raise Exception("post_text error")

def get_txt(prompt: str):
    try:
        token = config.get('bot', 'token')
        openai.api_key = token
        model = config.get('bot', 'model')
        max_tokens = int(config.get('bot', 'max_tokens'))
        temperature = float(config.get('bot', 'temperature'))

        prompt = f'''
    Snow, Снег, 🌨
    Rain, Дождь, 🌧
    Sunny, Солнечно, ☀
    {prompt},'''

        completion = openai.Completion.create(
            engine=model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        txt = completion.choices[0].text
        txt = txt.split(',')
        return txt[1].strip(), txt[0].strip()

    except:
        return None, None

def get_weather(today_text):
    tt = '??'
    t_text = today_text

    if today_text == 'Snow':
        tt = '🌨'
        t_text = 'Снег'
    elif today_text == 'Cloudy':
        tt = '☁'
        t_text = 'Облачно'
    elif today_text == 'Sleet':
        tt = '🌧'
        t_text = 'Мокрый снег'
    elif today_text == 'Foggy':
        tt = '🌫'
        t_text = 'Туман'
    elif today_text == 'Clear':
        tt = '☀'
        t_text = 'Ясно'
    elif today_text == 'Showers':
        tt = '🌧'
        t_text = 'Ливень'
    elif today_text == 'Sunny':
        tt = '☀'
        t_text = 'Солнечно'

    elif today_text == 'Mostly Sunny':
        tt = '☀'
        t_text = 'Ясно-Солнечно'

    elif today_text == 'Partly Cloudy':
        tt = '⛅️'
        t_text = 'Переменная облачность'

    elif today_text == 'Mostly Cloudy':
        tt = '🌥'
        t_text = 'Преимущественно облачно'

    elif today_text == 'Mostly Clear':
        tt = '🌤' 
        t_text = 'Преимущественно ясно'

    elif today_text == 'Fair':
        tt = '🌥'
        t_text = 'Без осадков, небольшая обласность'

    elif today_text == 'Mixed Rain and Snow':
        tt = '🌧'
        t_text = 'Дождь со снегом'

    elif today_text == 'Flurries':
        tt = '🌧'
        t_text = 'Легкий снег'

    elif today_text == 'Scattered Thunderstorms':
        tt = '⛈️'
        t_text = 'Разбросанные грозы'

    elif today_text == 'Scattered Showers':
        tt = '⛈️'
        t_text = 'Разрозненные дожди'

    elif today_text == 'Thunderstorms':
        tt = '⚡'
        t_text = 'Гроза'


    return tt, t_text

def temperature():
    #https://www.yahoo.com/news/weather/kazakhstan/batys-qazaqstan/oral-2264983
    url = "https://yahoo-weather5.p.rapidapi.com/weather"
    querystring = {"lat": "51.223419", "long": "51.356411", "format": "json", "u": "c"}
    headers = {
        "X-RapidAPI-Key": "8419074986mshfb2da144f8b1085p17a241jsn5d5602969ac8",
        "X-RapidAPI-Host": "yahoo-weather5.p.rapidapi.com"
    }

    r = requests.request("GET", url, headers=headers, params=querystring).json()
    #print(r)
    now_time = r['current_observation']['pubDate']
    today = r['current_observation']['condition']
    today_tem = today['temperature']
    today_text = today['text']
    print(today_text)

    wind = r['current_observation']['wind']
    wind_s = wind['speed'] * 1.609

    pressure = r['current_observation']['atmosphere']['pressure']

    #tt, t_text = get_txt(today_text)
    tt, t_text = get_weather(today_text)

    tomorrow = r["forecasts"]
    #print(tomorrow)
    tom_tem_min = tomorrow[0]['low']
    tom_tem_max = tomorrow[0]['high']
    tom_text = tomorrow[0]['text']
    print(tom_tem_min, tom_tem_max, tom_text)

    tmt, tm_text = get_weather(tom_text)
    #tmt, tm_text = get_txt(tom_text)

    txt = f'''Сегодня: t= {today_tem}°C
{tt} {t_text}
Давление:🔻{pressure}
Ветер:💨 {wind_s/3.6:.0f} м/с
Завтра: max t= {tom_tem_max}°C, min t= {tom_tem_min}°C
{tmt} {tm_text}'''
    print(txt)
    return txt

def get_data():
    headers ={
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 OPR/40.0.2308.81',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'DNT': '1',
        'Accept-Encoding': 'gzip, deflate, lzma, sdch',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'
    }

    url = 'https://www.gismeteo.ru/weather-naberezhnye-chelny-4534/gm/'
    url = 'https://www.gismeteo.kz/weather-oral-5156/gm/'
    r = requests.get(url, headers=headers).text
    soup = BeautifulSoup(r, "html.parser")
    #print(soup)

    gmcurrent = soup.find('div', class_='gmcurrent').text
    num_act = int(gmcurrent[0])
    #print(num_act)

    if 0 <= num_act <= 1:
        col = '🟢'
    elif 2 <= num_act <= 3:
        col = '🔵'
    elif 4 <= num_act <= 5:
        col = '🟡'
    elif 6 <= num_act <= 7:
        col = '🟠'
    elif 8 <= num_act <= 9:
        col = '🔴'

    city = soup.find('div', class_='transparent-city js-transparent-city').text

    now_act = gmcurrent[1:]

    txt = f'''
{time.ctime()}
Город: {city}
{temperature()}
ГМ Активность: {num_act}
{col} {now_act}'''

    send_telegram(txt)

get_data()
