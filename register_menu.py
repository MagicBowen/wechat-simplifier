import os
import sys
sys.path.append("lib/itchat")
import itchatmp
 
menu = {
    "button":[
    {    
        "type":"click",
        "name":"纠正",
        "key":"modify"
    }
    ]
}
    
def register_menu():
    r = itchatmp.menu.create(menu)
    print('register menu complete!')