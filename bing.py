import telebot
import asyncio
import re
import json
import os

from telebot.async_telebot import AsyncTeleBot

from EdgeGPT import Chatbot, ConversationStyle
from telebot.util import quick_markup

BOT_TOKEN = os.getenv('BOT_TOKEN')
ALLOWED_USER_IDS = os.getenv('ALLOWED_USER_IDS').split(',')
COOKIE_PATH = os.getenv('COOKIE_PATH', './cookie.json')

bot = telebot.TeleBot(BOT_TOKEN)
EDGES = {}
for user in ALLOWED_USER_IDS:
    EDGES[int(user)] = Chatbot(cookiePath=COOKIE_PATH)
# gbot = Chatbot(cookiePath=COOKIE_PATH)
not_allow_info = '⚠️You are not authorized to use this bot⚠️'

markup = quick_markup({
    'Github': {'url': 'https://github.com/pininkara/BingChatBot'},
}, row_width=1)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if is_allowed(message):
        bot.reply_to(
            message, "Bing Chat Bot By Kakanya~\n", reply_markup=markup)
    else:
        bot.reply_to(message, not_allow_info)


@bot.message_handler(commands=['reset'])
def send_reset(message):
    if is_allowed(message):
        asyncio.run(EDGES[message.from_user.id].reset())
        bot.reply_to(message, "Reset successful🎉")
    else:
        bot.reply_to(message, not_allow_info)


@bot.message_handler(func=lambda msg: True)
def response_all(message):
    print("Receive: " + message.text)
    if is_allowed(message):
        responseList = asyncio.run(bingChat(message.text, message))

        if len(callbackQuery.message) > 4095:
            for x in range(0, len(callbackQuery.message), 4095):
                bot.reply_to(
                    callbackQuery.message, responseList[0][x:x+4095], parse_mode='Markdown', reply_markup=responseList[1])
        else:
            bot.reply_to(
                    callbackQuery.message, responseList[0], parse_mode='Markdown', reply_markup=responseList[1])
    else:
        bot.reply_to(message, not_allow_info)

@bot.callback_query_handler(func=lambda msg: True)
def callback_all(callbackQuery):
    print("callbackQuery: " + callbackQuery.data)
    responseList = asyncio.run(bingChat(callbackQuery.data, callbackQuery))
    bot.reply_to(
        callbackQuery.message, responseList[0], parse_mode='Markdown', reply_markup=responseList[1])
    
    if len(callbackQuery.message) > 4095:
        for x in range(0, len(callbackQuery.message), 4095):
            bot.reply_to(
                callbackQuery.message, responseList[0][x:x+4095], parse_mode='Markdown', reply_markup=responseList[1])

    else:
        bot.reply_to(
                callbackQuery.message, responseList[0], parse_mode='Markdown', reply_markup=responseList[1])

async def bingChat(messageText, message):
    response_dict = await EDGES[message.from_user.id].ask(prompt=messageText,
                                                          conversation_style=ConversationStyle.creative)

    json_str = json.dumps(response_dict)
    print("JSON: \n" + json_str)

    if 'text' in response_dict['item']['messages'][1]:
        response = re.sub(r'\[\^\d\^\]', '',
                          response_dict['item']['messages'][1]['text'])
    else:
        response = "Something wrong. Please reset chat"

    if 'suggestedResponses' in response_dict['item']['messages'][1]:
        suggestedResponses0 = re.sub(
            r'\[\^\d\^\]', '', response_dict['item']['messages'][1]['suggestedResponses'][0]['text'])
        suggestedResponses1 = re.sub(
            r'\[\^\d\^\]', '', response_dict['item']['messages'][1]['suggestedResponses'][1]['text'])
        suggestedResponses2 = re.sub(
            r'\[\^\d\^\]', '', response_dict['item']['messages'][1]['suggestedResponses'][2]['text'])
        markup = quick_markup({
            suggestedResponses0: {'callback_data': suggestedResponses0[0:21]},
            suggestedResponses1: {'callback_data': suggestedResponses1[0:21]},
            suggestedResponses2: {'callback_data': suggestedResponses2[0:21]}
        }, row_width=1)
    else:
        markup = quick_markup({
            'No Suggested Responses': {'url': 'https://bing.com/chat'}
        }, row_width=1)

    if 'maxNumUserMessagesInConversation' in response_dict['item']['throttling'] and 'numUserMessagesInConversation' in \
            response_dict['item']['throttling']:
        maxNumUserMessagesInConversation = response_dict['item'][
            'throttling']['maxNumUserMessagesInConversation']
        numUserMessagesInConversation = response_dict['item']['throttling']['numUserMessagesInConversation']
        response = response + "\n----------\n"
        response = response + "Messages In Conversation : %d / %d" % (
            numUserMessagesInConversation, maxNumUserMessagesInConversation)

    if numUserMessagesInConversation >= maxNumUserMessagesInConversation:
        await EDGES[messageText.from_user.id].reset()
        response = response + "\nAutomatic reset succeeded🎉"

    if len(response_dict['item']['messages'][1]['sourceAttributions']) >= 3:
        providerDisplayName0 = re.sub(
            r'\[\^\d\^\]', '', response_dict['item']['messages'][1]['sourceAttributions'][0]['providerDisplayName'])
        seeMoreUrl0 = re.sub(
            r'\[\^\d\^\]', '', response_dict['item']['messages'][1]['sourceAttributions'][0]['seeMoreUrl'])
        providerDisplayName1 = re.sub(
            r'\[\^\d\^\]', '', response_dict['item']['messages'][1]['sourceAttributions'][1]['providerDisplayName'])
        seeMoreUrl1 = re.sub(
            r'\[\^\d\^\]', '', response_dict['item']['messages'][1]['sourceAttributions'][1]['seeMoreUrl'])
        providerDisplayName2 = re.sub(
            r'\[\^\d\^\]', '', response_dict['item']['messages'][1]['sourceAttributions'][2]['providerDisplayName'])
        seeMoreUrl2 = re.sub(
            r'\[\^\d\^\]', '', response_dict['item']['messages'][1]['sourceAttributions'][2]['seeMoreUrl'])
        response = response + "\n----------\nReference:\n"
        response = response + \
                   "1.[%s](%s)\n" % (providerDisplayName0, seeMoreUrl0)
        response = response + \
                   "2.[%s](%s)\n" % (providerDisplayName1, seeMoreUrl1)
        response = response + \
                   "3.[%s](%s)\n" % (providerDisplayName2, seeMoreUrl2)

    markup = quick_markup({
        suggestedResponses0: {'callback_data': suggestedResponses0[0:21]},
        suggestedResponses1: {'callback_data': suggestedResponses1[0:21]},
        suggestedResponses2: {'callback_data': suggestedResponses2[0:21]}
    }, row_width=1)
    responseList = [response, markup]
    return responseList


def is_allowed(message) -> bool:
    # Check if user is allowed
    if str(message.from_user.id) in ALLOWED_USER_IDS:
        return True

    return False


bot.infinity_polling()
