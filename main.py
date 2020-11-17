#!/usr/bin/python




# DESCRIPTION:
# This script executes 2 actions:
# 1.) Monitors for new image posted in a instagram account (create a cronjob).
# 2.) If found new image, a bot posts new instagram image in a discord channel.

# REQUIREMENTS:
# - Python v3
# - Python module re, json, requests
import re
import json
import sys
import requests
import urllib.request
import os
import time
import discord
from discord.ext import commands,tasks

# USAGE:
# Replace INSTAGRAM_USERNAME with username account you want to monitor.
# Replace WEBHOOK_URL with Discord account webhook url. To know how, just Google: "how to create webhook discord".
# Replace DATABASE with any finename you want to use as temporary data for checking new photos.

ACCOUNTS={

}
#URL WEBHOOK
WEBHOOK_URL = ""
#TOKEN BOT
TOKEN_BOT=''
bot = commands.Bot(command_prefix='!', description='Monitor de instagram ')


def get_user_fullname(html):
    return html.json()["graphql"]["user"]["full_name"]

def get_total_photos(html):
    return int(html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["count"])

def get_last_publication_url(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["shortcode"]

def get_last_photo_url(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["display_url"]

def get_last_thumb_url(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["thumbnail_src"]
    
def get_description_photo(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"]

def webhook(webhook_url,html, username):
    #for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
    #for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
    data = {}
    data["embeds"] = []
    embed = {}    
    embed["color"] = 8974041
    embed["title"] = ""+username+""
    embed["url"] = "https://www.instagram.com/p/"+get_last_publication_url(html)+"/"
    embed["description"] = get_description_photo(html)
    embed["image"] = {"url":get_last_thumb_url(html)} # unmark to post bigger image
    embed["footer"]={"text": "INSTAGRAM · Atlas Notify","icon_url":'https://cdn.discordapp.com/attachments/764933346450210847/764933407637504000/LOGO_footer-01.png'}
    data["embeds"].append(embed)
    result = requests.post(webhook_url, data=json.dumps(data), headers={"Content-Type": "application/json"})
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Image successfully posted in Discod, code {}.".format(result.status_code))

def get_instagram_html(username):
    html = requests.get("https://www.instagram.com/" + username+ "/?__a=1")
    return html


def checker(username,total):
    try:
        html = get_instagram_html(username)
        totalnow=get_total_photos(html)
        if(total==totalnow):
            print("Not new image to post in discord.")
        else:
            print("New image to post in discord.")
            ACCOUNTS[username]=totalnow
            webhook(WEBHOOK_URL, get_instagram_html(username),username)
    except:
        print("An error occured.")


#check every account each 3 minutes 
@tasks.loop(minutes=3)
async def checkAccounts():
    if ACCOUNTS:
        for username, total in ACCOUNTS.items():
            checker(username,total)
            time.sleep(20)


#add new account
@bot.command(name='add')
async def addAccount(ctx, username):
    html = get_instagram_html(username)
    ACCOUNTS[username]=get_total_photos(html)
    print(ACCOUNTS)


@bot.event
async def on_ready():
    print('listo')
    checkAccounts.start()

bot.run(TOKEN_BOT)
