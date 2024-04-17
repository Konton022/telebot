import telebot
import requests
import json
import os
import re
from g4f.client import Client
from g4f.Provider import RetryProvider,ChatForAi, Chatgpt4Online, ChatgptNext, ChatgptX, GptTalkRu, Koala, FlowGpt
from telebot import types





API_TOKEN = os.getenv('API_TOKEN')
API_WEATHER_TOKEN = os.getenv('API_WEATHER_TOKEN')


bot = telebot.TeleBot(API_TOKEN)

def get_weather_by_api(message):
    # Define the base URL for the OpenWeatherAPI and your API key
    base_url = "https://api.openweathermap.org/data/2.5/weather"

    # Set the city you want to get the weather data for
    city = message.text

    # Construct the full URL with parameters
    params = {
        "q": city,
        "appid": API_WEATHER_TOKEN,
        "units": "metric",
        "lang": "ru"
    }


    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        bot.send_location(message.chat.id, latitude=data['coord']['lat'], longitude=data['coord']['lon'])
        bot.send_message(message.chat.id, json.dumps(data['main']))
        bot.send_message(message.chat.id, json.dumps(data['weather']))
        bot.send_message(message.chat.id, data['weather'][0]['description'])
        bot.send_message(message.chat.id, data['weather'][0]['icon'])

        print(data)

    else:
        print()
        bot.reply_to(message, f"Failed to retrieve data: {response.status_code}" )

# Handle '/start' and '/help'
@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, готовый отвечать на ваши запросы.")


# handle /weather
@bot.message_handler(commands=['weather'])
def send_current_weather(message):
    # bot.reply_to(message, f"hello {message.chat.first_name}! you send me {message.text}")
    sent = bot.reply_to(message, 'send city')
    bot.register_next_step_handler(sent, get_weather_by_api)

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
# @bot.message_handler(func=lambda message: True)
# def echo_message(message):
#     bot.reply_to(message, message.text)


@bot.message_handler(commands=['img'])
def handle_gpt(message):
    send = bot.reply_to(message, 'send your image description')
    bot.register_next_step_handler(send, get_gpt_img)


@bot.message_handler(content_types=['text'])
def handle_gpt(message):
    send = bot.reply_to(message, 'обрабатываю запрос...')
    # bot.register_next_step_handler(send, get_gpt_message)
    get_gpt_message(message)

def get_gpt_message(message):
    # client = Client(
    #     provider=RetryProvider([ChatForAi, Chatgpt4Online, ChatgptFree, ChatgptX, FlowGpt], shuffle=False)
    # )
    client = Client(
        provider=RetryProvider([ChatForAi, Chatgpt4Online, ChatgptNext, ChatgptX, GptTalkRu, Koala, FlowGpt], shuffle=False)
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message.text}],
    )
    print(response.choices[0].message.content)
    bot.send_message(message.chat.id, response.choices[0].message.content)

def get_gpt_img(message):
    client = Client()
    response = client.images.generate(
        model="dall-e-3",
        prompt=message.text,
    )
    image_url = response.data[0].url
    print(image_url)
    bot.send_photo(message.chat.id, image_url)


bot.infinity_polling()
