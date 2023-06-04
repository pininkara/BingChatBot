import asyncio
import os
import re

import telebot
from EdgeGPT import Chatbot, ConversationStyle
from telebot.util import quick_markup

BOT_TOKEN = os.getenv('BOT_TOKEN')
ALLOWED_USER_IDS = os.getenv('ALLOWED_USER_IDS').split(',')
BOT_ID = os.getenv('BOT_ID', '')
COOKIE_PATH = os.getenv('COOKIE_PATH', './cookie.json')
GROUP_MODE = os.getenv('GROUP_MODE', 'False')
PUBLIC_MODE = os.getenv('PUBLIC_MODE', 'False')

print("\033[1;33mThe startup is successful, the configuration is as follows : ")
print("BOT_TOKEN: " + BOT_TOKEN)
print("BOT_ID: " + BOT_ID)
print("ALLOWED_USER_IDS: ")
print(ALLOWED_USER_IDS)
print("COOKIE_PATH: " + COOKIE_PATH)
print("GROUP_MODE: " + GROUP_MODE)
print("PUBLIC_MODE: " + PUBLIC_MODE + '\033[1;33m')

bot = telebot.TeleBot(BOT_TOKEN)
EDGES = {}

not_allow_info = '⚠️You are not authorized to use this bot⚠️'

markup = quick_markup({
    'Github': {'url': 'https://github.com/pininkara/BingChatBot'},
}, row_width=1)

my_conversation_style = ConversationStyle.balanced


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if is_allowed(message) or PUBLIC_MODE == "True" or message.chat.type == "group":
        bot.reply_to(
            message, "Bing Chat Bot By pininkara~\n/help - Show help message\n/reset - Reset conversation\n/switch - "
                     "Switch conversation style (creative,balanced,precise)\n", reply_markup=markup)
    else:
        bot.reply_to(message, not_allow_info)


@bot.message_handler(commands=['reset'])
def send_reset(message):
    if is_allowed(message) or PUBLIC_MODE == "True" or message.chat.type == "group":
        try:
            if message.from_user.id not in EDGES:
                EDGES[message.from_user.id] = Chatbot(cookie_path=COOKIE_PATH)
            asyncio.run(EDGES[message.from_user.id].reset())
        except Exception as e:
            print("\033[31mError: ", e)
            bot.reply_to(message, "Error : " + str(e), parse_mode='Markdown')
        else:
            bot.reply_to(message, "Reset successful🎉")
    else:
        bot.reply_to(message, not_allow_info)


@bot.message_handler(commands=['switch'])
def switch_style(message):
    if is_allowed(message):
        message_list = message.text.split(" ")
        if len(message_list) > 1:
            if message_list[1] == "creative":
                bot.reply_to(
                    message,
                    "Switch successful , current style is creative")
            elif message_list[1] == "balanced":
                conversation_style = ConversationStyle.balanced
                bot.reply_to(
                    message,
                    "Switch successful , current style is balanced")
            elif message_list[1] == "precise":
                conversation_style = ConversationStyle.precise
                bot.reply_to(
                    message,
                    "Switch successful , current style is precise")
            else:
                bot.reply_to(
                    message,
                    "Parameter error , please choose one of (creative,balanced,precise)\n(e.g./switch balanced")
        else:
            bot.reply_to(
                message, "Parameter error , please choose one of (creative,balanced,precise)\n(e.g./switch balanced")
    else:
        bot.reply_to(
            message, '⚠️You are not authorized to switch the conversation style⚠')


@bot.message_handler(func=lambda msg: True)
def response_all(message):
    print('\033[0;32mMessage: ' + message.text)
    print(
        'From: ', message.from_user.first_name, message.from_user.last_name, ' @', message.from_user.username)

    message_text = ''
    is_reply = message.reply_to_message is not None and '@' + \
        message.reply_to_message.from_user.username == BOT_ID
    if message.chat.type == "private" or GROUP_MODE == "True" or message.text.startswith(BOT_ID) or is_reply:
        if is_allowed(message) or PUBLIC_MODE == "True" or message.chat.type == "group":
            if message.text.startswith(BOT_ID) and BOT_ID != '':
                message_text = message.text[len(BOT_ID):]
            else:
                message_text = message.text
                response_list = asyncio.run(bing_chat(message_text, message))
                print("\033[1;34mResponse: " + response_list[0])
                if len(response_list[0]) > 4095:
                    for x in range(0, len(response_list[0]), 4095):
                        bot.reply_to(
                            message, response_list[0][x:x + 4095], parse_mode='Markdown', reply_markup=response_list[1])
                else:
                    bot.reply_to(
                        message, response_list[0], parse_mode='Markdown', reply_markup=response_list[1])
        else:
            bot.reply_to(message, not_allow_info)
    else:
        print('\033[0;36mUntargeted message, ignored\033[0;36m')


@bot.callback_query_handler(func=lambda msg: True)
def callback_all(callback_query):
    print("\033[0;32mCallbackQuery: " + callback_query.data)
    print(
        'From: ', callback_query.from_user.first_name, callback_query.from_user.last_name, '@',
        callback_query.from_user.username)
    try:
        response_list = asyncio.run(
            bing_chat(callback_query.data, callback_query))
    except Exception as e:
        print("\033[31mError: ", e)
        bot.reply_to(callback_query.message, "Error : " +
                     str(e), parse_mode='Markdown')
    else:
        print("\033[1;34mResponse: " + response_list[0] + '\033[1;34m')
        if len(response_list[0]) > 4095:
            for x in range(0, len(response_list[0]), 4095):
                bot.reply_to(
                    callback_query.message, response_list[0][x:x +
                                                             4095], parse_mode='Markdown',
                    reply_markup=response_list[1])
        else:
            bot.reply_to(
                callback_query.message, response_list[0], parse_mode='Markdown', reply_markup=response_list[1])


async def bing_chat(message_text, message):
    if message.from_user.id not in EDGES:
        EDGES[message.from_user.id] = Chatbot(cookie_path=COOKIE_PATH)
    response_dict = await EDGES[message.from_user.id].ask(prompt=message_text,
                                                          conversation_style=my_conversation_style)

    if 'text' in response_dict['item']['messages'][1]:
        response = re.sub(r'\[\^\d\^]', '',
                          response_dict['item']['messages'][1]['text'])
    else:
        response = "Something wrong. Please reset chat"

    if 'suggestedResponses' in response_dict['item']['messages'][1]:
        suggested_responses0 = re.sub(
            r'\[\^\d\^]', '', response_dict['item']['messages'][1]['suggestedResponses'][0]['text'])
        suggested_responses1 = re.sub(
            r'\[\^\d\^]', '', response_dict['item']['messages'][1]['suggestedResponses'][1]['text'])
        suggested_responses2 = re.sub(
            r'\[\^\d\^]', '', response_dict['item']['messages'][1]['suggestedResponses'][2]['text'])
        markup = quick_markup({
            suggested_responses0: {
                'callback_data': suggested_responses0.encode('utf-8')[:64].decode('utf-8', 'ignore')},
            suggested_responses1: {
                'callback_data': suggested_responses1.encode('utf-8')[:64].decode('utf-8', 'ignore')},
            suggested_responses2: {'callback_data': suggested_responses2.encode(
                'utf-8')[:64].decode('utf-8', 'ignore')}
        }, row_width=1)
    else:
        markup = quick_markup({
            'No Suggested Responses': {'url': 'https://bing.com/chat'}
        }, row_width=1)

    if 'maxNumUserMessagesInConversation' in response_dict['item']['throttling'] and 'numUserMessagesInConversation' in \
            response_dict['item']['throttling']:
        max_num_user_messages_in_conversation = response_dict['item'][
            'throttling']['maxNumUserMessagesInConversation']
        num_user_messages_in_conversation = response_dict[
            'item']['throttling']['numUserMessagesInConversation']
        response = response + "\n----------\n"
        response = response + "Messages In Conversation : %d / %d" % (
            num_user_messages_in_conversation, max_num_user_messages_in_conversation)

    if num_user_messages_in_conversation >= max_num_user_messages_in_conversation:
        await EDGES[message.from_user.id].reset()
        response = response + "\nAutomatic reset succeeded🎉"

    if len(response_dict['item']['messages'][1]['sourceAttributions']) >= 3:
        provider_display_name0 = re.sub(
            r'\[\^\d\^]', '', response_dict['item']['messages'][1]['sourceAttributions'][0]['providerDisplayName'])
        see_more_url0 = re.sub(
            r'\[\^\d\^]', '', response_dict['item']['messages'][1]['sourceAttributions'][0]['seeMoreUrl'])
        provider_display_name1 = re.sub(
            r'\[\^\d\^]', '', response_dict['item']['messages'][1]['sourceAttributions'][1]['providerDisplayName'])
        see_more_url1 = re.sub(
            r'\[\^\d\^]', '', response_dict['item']['messages'][1]['sourceAttributions'][1]['seeMoreUrl'])
        provider_display_name2 = re.sub(
            r'\[\^\d\^]', '', response_dict['item']['messages'][1]['sourceAttributions'][2]['providerDisplayName'])
        see_more_url2 = re.sub(
            r'\[\^\d\^]', '', response_dict['item']['messages'][1]['sourceAttributions'][2]['seeMoreUrl'])
        response = response + "\n----------\nReference:\n"
        response = response + \
            "1.[%s](%s)\n" % (provider_display_name0, see_more_url0)
        response = response + \
            "2.[%s](%s)\n" % (provider_display_name1, see_more_url1)
        response = response + \
            "3.[%s](%s)\n" % (provider_display_name2, see_more_url2)

    markup = quick_markup({
        suggested_responses0: {'callback_data': suggested_responses0.encode('utf-8')[:64].decode('utf-8', 'ignore')},
        suggested_responses1: {'callback_data': suggested_responses1.encode('utf-8')[:64].decode('utf-8', 'ignore')},
        suggested_responses2: {'callback_data': suggested_responses2.encode(
            'utf-8')[:64].decode('utf-8', 'ignore')}
    }, row_width=1)
    response_list = [response, markup]
    return response_list


def is_allowed(message) -> bool:
    # Check if user is allowed
    if str(message.from_user.id) in ALLOWED_USER_IDS:
        return True

    return False


bot.infinity_polling()
