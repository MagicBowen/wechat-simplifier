import os
import sys
sys.path.append("lib/itchat")
import itchatmp
import json
import time
import logging
import requests
import config
from register_menu import register_menu

#########################################################
logger = logging.getLogger('wechat')

#########################################################
class Marker:
    def __init__(self):
        self.file = open('./marked_replies.txt', 'a', encoding='utf-8')
        self.query = ''
        self.reply = ''

    def save_reply(self, query, reply):
        self.query = query
        self.reply = reply

    def mark(self):
        if (self.reply.strip() != ''):
            self.file.write(self.query + '    :    ' + self.reply + "\n")
            return '已标记，谢谢'

marker = Marker()            

#########################################################
# for production environment
#########################################################
itchatmp.update_config(itchatmp.WechatConfig(
    token = config.TOCKEN,
    appId = config.APP_ID,
    appSecret = config.APP_SECRET,
    encryptMode = itchatmp.content.SAFE if config.ENCRYPT else itchatmp.content.NORMAL,
    encodingAesKey = config.ENCODING_AES_KEY if config.ENCRYPT else ''))

#########################################################
def get_reply(query):
    if not query or query.strip() == '':
        return '对不起，不能发送空消息哦~'

    if query == 'x':
        return marker.mark()

    request_json = { "x": query } 

    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url=config.CHATBOT_URL, headers=headers, data=json.dumps(request_json))
        if response.status_code != 200: 
            logger.error('requested chatbot failed, error code = {0}!'.format(response.status_code))
            return '升级维护中，请稍后再试...'
        marker.save_reply(query, response.json()['y'])
        return response.json()['y']
    except Exception as e:
        logger.error('requested chatbot exception: {0}!'.format(str(e)))
        return '升级维护中，请稍后再试...'
    
#########################################################
@itchatmp.msg_register(itchatmp.content.TEXT)
def text_reply(msg):
    user_id = msg['FromUserName']
    content = msg['Content']
    return get_reply(content)

#########################################################
@itchatmp.msg_register(itchatmp.content.VOICE)
def voice_reply(msg):
    user_id = msg['FromUserName']
    content = msg['Recognition']
    return get_reply(content)

#########################################################
@itchatmp.msg_register(itchatmp.content.EVENT)
def subscribe_reply(msg):
    user_id = msg['FromUserName']
    if msg['Event'] == 'subscribe' :
        print("receive event: subscribe")
        return "欢迎加入小哒智能AI内测训练，回复 x 对不正确的语义结果进行标记，以帮助随后更好的训练，谢谢！"   
    elif msg['Event'] == 'CLICK' :
        print("receive event: CLICK")
        key = msg['EventKey']
        if key == 'modify':
            return marker.mark()

# register_menu()
itchatmp.run(port=config.HTTP_PORT)