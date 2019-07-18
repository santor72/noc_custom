# -*- coding: utf-8 -*-
import json
import os
import sys
import requests
import pyping
from pprint import pprint
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import apiai

# NOC modules
from noc.core.service.base import Service
from noc.sa.models.managedobject import ManagedObject
from noc.main.models.customfieldenumgroup import CustomFieldEnumGroup
from noc.main.models.customfieldenumvalue import CustomFieldEnumValue
from noc.fm.models.activealarm import ActiveAlarm
from noc.core.management.base import BaseCommand
from noc.sa.models.action import Action

olt = {"Vishnevay" : "10.8.0.11", "Melihovo" : "10.5.0.11"}

class Command(BaseCommand):
    def showalarm(self):
        alarms = ActiveAlarm.objects().order_by("-timestamp")
        res = []
        i = 0
#        for a in alarms:
#            res.append('{} - {}'.format(a.managed_object.name, a.subject))
#            i = 1+1
        pprint(alarms[0].subject)

    def startCommand(self,bot, update):
        chat_id = update.message.chat_id
        if str(chat_id) in validuser:
            bot.send_message(chat_id=update.message.chat_id, text='?????')
        else:
#            self.logger.info('Not valid user {}'.format(update.message.chat_id))
            print('Not valid user {}'.format(update.message.chat_id))
            bot.sendMessage(chat_id=chat_id, text='Sorry, private area')
        
    def textMessage(self,bot, update):
        if update.channel_post:
            return
        response = '' + update.message.text
        request = apiai.ApiAI(apiaikey01).text_request()
        request.lang = 'ru'
        request.session_id = 'RNNOCAlarmAI'
        request.query = update.message.text
        responseJson = json.loads(request.getresponse().read().decode('utf-8'))
        response = responseJson['result']['fulfillment']['speech'] # Разбираем JSON и вытаскиваем ответ
        pprint(responseJson)
        if responseJson and 'action' in responseJson['result']:
            if responseJson['result']['action'] == 'showalarms':
                message = self.showalarm()
                i = 0 
                for m in range(len(message)):
                    bot.send_message(chat_id=update.message.chat_id, text=message[m])
                    i = i + 1
                    if i == 10:
                        break
                return
        if response:
            bot.send_message(chat_id=update.message.chat_id, text=response)
        else:
            bot.send_message(chat_id=update.message.chat_id, text='Я Вас не совсем понял!')

    def ping(self, bot, update, args):
         if not str(update.message.chat_id) in validuser:
             self.logger.info('Not valid user {}'.format(update.message.chat_id))
             return
         host = args[0]
         r = pyping.ping(host)
         if r.ret_code == 0:
             msg = ("{} Success".format(host))
         else:
             msg = "{} Failed with {}".format(host,r.ret_code)
         bot.send_message(chat_id=update.message.chat_id, text=msg)

    def olts(self, bot, update, args):
        if not str(update.message.chat_id) in validuser:
            self.logger.info('Not valid user {}'.format(update.message.chat_id))
            return
        for i in olt:
            r = pyping.ping(olt[i])
            if r.ret_code == 0:
                msg = ("{} - {} Success".format(i, olt[i]))
            else:
                msg = "{} - {} Failed with {}".format(i, olt[i],r.ret_code)

            bot.send_message(chat_id=update.message.chat_id, text=msg)

    def wtf(self, bot, update, args):
        if not str(update.message.chat_id) in validuser:
            self.logger.info('Not valid user {}'.format(update.message.chat_id))
            return

    def show(self, bot, update, args):
        if not str(update.message.chat_id) in validprivuser:
            self.logger.info('Not valid user {}'.format(update.message.chat_id))
            return
        host = args[0]
        a = args[:]
        del a[0]
        cmd = 'show ' + ' '.join(a)
        mo = ManagedObject.objects.get(address = host)
        print(mo.name)
        print(cmd)
        if not mo:
            bot.send_message(chat_id=update.message.chat_id, text='MO not found')
            return
        data = mo.scripts.commands(commands = [cmd])
        #AODpprint(data)
        for item in data['output']:
            bot.send_message(chat_id=update.message.chat_id, text=item)

    def kg(self, bot, update, args):
        if not str(update.message.chat_id) in validprivuser:
            self.logger.info('Not valid user {}'.format(update.message.chat_id))
            return
        mo = ManagedObject.objects.get(id = 97)
        print(mo.name)
        if not mo:
            bot.send_message(chat_id=update.message.chat_id, text='MO not found')
            return
        data = mo.scripts.commands(commands=['sh arp | i ^Internet  217.76.38.203|^Internet  217.76.38.194|^Internet  217.76.38.202'])
        for item in data['output']:
            bot.send_message(chat_id=update.message.chat_id, text=item)

    def handle(self, *args, **options):
#    def on_activate(self):
        updater = Updater(token=botkey)
        dispatcher = updater.dispatcher
        start_command_handler = CommandHandler('start', self.startCommand)
        text_message_handler = MessageHandler(Filters.text, self.textMessage)
        dispatcher.add_handler(start_command_handler)
        dispatcher.add_handler(text_message_handler)
        ping_handler = CommandHandler('ping', self.ping, pass_args=True)
        dispatcher.add_handler(ping_handler)
        olts_handler = CommandHandler('olts', self.olts, pass_args=True)
        dispatcher.add_handler(olts_handler)
        wtf_handler = CommandHandler('wtf', self.wtf, pass_args=True)
        dispatcher.add_handler(wtf_handler)
        show_handler = CommandHandler('show', self.show, pass_args=True)
        dispatcher.add_handler(show_handler)
        kg_handler = CommandHandler('kg', self.kg, pass_args=True)
        dispatcher.add_handler(kg_handler)
        updater.start_polling(clean=True)
        updater.idle()

    def api_data(self, req):
     try:
        data = json.loads(req.body.encode())
        return('{"message" : "I am heare"}')
        if 'channel_post' in data:
            message = str(data["channel_post"]["text"])
            chat_id = data["channel_post"]["chat"]["id"]
            first_name = data["channel_post"]["chat"]["title"]
            print(first_name)
        else:
            message = str(data["message"]["text"])
            chat_id = data["message"]["chat"]["id"]
            first_name = data["message"]["chat"]["first_name"]
            print("{}\n".format(first_name))

        if not any(chat_id == s for s in validuser):
            print(chat_id)
            print(' not valid user')
            return {"statusCode": 200}, None
        
        response = "Please /start, {}".format(first_name)

        if "start" in message:
            response = "Hello {}! Type /help to get list of actions.".format(first_name)

        if "help" in message:
            response = "/about - get information about rnnoc"

        if "about" in message:
            response = ("NOC bot for Raionet\n{}\t{}".format(chat_id,first_name))

        data = {"text": response.encode("utf8"), "chat_id": chat_id}
        url = BASE_URL + "/sendMessage"
        requests.post(url, data)

     except Exception as e:
        print(e)

     return {"statusCode": 200}, None

if __name__ == "__main__":
    BASE_URL = "https://api.telegram.org/bot{}".format('ACC_TELEGRAMRNNOCBOT_TOKEN')
    botkey = str(CustomFieldEnumValue.objects.get(key='botkey', enum_group=CustomFieldEnumGroup.objects.get(name='botkeys')).value)
    validuser=str(CustomFieldEnumValue.objects.get(key='validuser', enum_group=CustomFieldEnumGroup.objects.get(name='botkeys')).value).split(',')
    validprivuser=str(CustomFieldEnumValue.objects.get(key='valid-priv-user', enum_group=CustomFieldEnumGroup.objects.get(name='botkeys')).value).split(',')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    apiaikey01 = str(CustomFieldEnumValue.objects.get(key='apiai01', enum_group=CustomFieldEnumGroup.objects.get(name='aikeys')).value)
    Command().run()
