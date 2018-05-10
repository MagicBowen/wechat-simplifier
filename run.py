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
last_reply = ''

mark_file = './marked_replies.txt'
file = open(mark_file, 'a', encoding='utf-8')

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

    if query == 'x' and last_reply.strip() != '':
        file.write(last_reply)
        return '已标记，谢谢！'

    request_json = { "x": query } 

    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url=config.CHATBOT_URL, headers=headers, data=json.dumps(request_json))
        if response.status_code != 200: 
            logger.error('requested chatbot failed, error code = {0}!'.format(response.status_code))
            return '升级维护中，请稍后再试...'
        last_reply = response.json()['y']
        return last_reply
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
            file.write(last_reply)
            return '已记录'

# register_menu()
itchatmp.run(port=config.HTTP_PORT)