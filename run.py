import os
import sys
sys.path.append("lib/itchat")
import itchatmp
import json
# import qrcode
import time
import logging
import requests
import config
from register_menu import register_menu

#########################################################
logger = logging.getLogger('wechat')

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

    request_json = { "x": query } 

    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url=config.CHATBOT_URL, headers=headers, data=json.dumps(request_json))
        if response.status_code != 200: 
            logger.error('requested chatbot failed, error code = {0}!'.format(response.status_code))
            return '升级维护中，请稍后再试...'
        return response.json()['y']
    except Exception as e:
        logger.error('requested chatbot exception: {0}!'.format(str(e)))
        return '升级维护中，请稍后再试...'
    
#########################################################
@itchatmp.msg_register(itchatmp.content.TEXT)
def text_reply(msg):
    user_id = msg['FromUserName']
    content = msg['Content']
    print("receive text: ${content}")
    rsp = get_reply(content)
    print("response text: ${rsp}")
    return rsp

#########################################################
@itchatmp.msg_register(itchatmp.content.VOICE)
def voice_reply(msg):
    user_id = msg['FromUserName']
    content = msg['Recognition']
    rsp = get_reply(content)
    print("response text: ${rsp}")
    return rsp

# register_menu()
itchatmp.run(port=config.HTTP_PORT)    
