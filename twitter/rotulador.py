#!/bin/python

import json, sys, colorama
from pprint import pprint
from os import system

vrd = colorama.Fore.GREEN
vrm = colorama.Fore.RED
azl = colorama.Fore.BLUE
amrl = colorama.Fore.LIGHTYELLOW_EX
rst = colorama.Fore.RESET
cnz = colorama.Fore.LIGHTBLACK_EX

tag_file = 'tags.json'

if len(sys.argv) < 2:
    print(vrm+"\nUso: "+rst+sys.argv[0]+" arquivo_com_tweets.json"+amrl+" [arquivo_com_os_rotulos]\n"+rst)
    exit(0)
elif len(sys.argv) == 3:
    tag_file = sys.argv[2]

raw_tweet_file = sys.argv[1]

try:
    with open(raw_tweet_file) as f:
        tweets = json.load(f)
except FileNotFoundError:
    print("O arquivo não existe.\n"+vrm+"Por favor, verifique se o arquivo existe ou se\nnão digitou errado antes de tentar novamente."+rst)
    exit(0)

try:
    with open(tag_file) as f:
        tags = json.load(f)
        print(f.read())
except FileNotFoundError:
    with open(tag_file, 'w') as f:
        f.write('[]')
    tags = []

"""
print("TAGS:")
pprint(tags)
print("\nTWEETS:\n")
pprint(tweets)
#"""

def save_tags():
    with open(tag_file,'w') as f:
        json.dump(tags,f)
    return

def save_tweets():
    with open(raw_tweet_file,'w') as f:
        json.dump(tags,f)
    return

def pprint_tweet(post):
    tab = " "*4
    tweet = post['tweet']
    sz = 80
    lines = len(tweet)//sz
    i = 0
    print(tab+vrm+"Tweet: "+rst)
    if len(tweet)>sz:
        for i in range(lines):
            print(tab*2+tweet[i*sz:(i+1)*sz])
        print(tab*2+tweet[(i+1)*sz:-1]+"\n")
    else:
        print(tab*2+tweet+"\n")
    print(vrd+tab+"Retweets: "+rst+str(post['retweets_count'])+tab*3+vrd+"Likes: "+rst+str(post['likes_count']))

    return

def relevante():
    value = ""
    while value != "S" and value != "N":
        value = input("Esse post é relevante para o estudo? (S/N)\n-> ")[:1].upper()
    if value == 'S':
        return True
    else:
        return False

tagged = []
for i, tweet in enumerate(tweets):
    system("clear")
    print("\n\n")
    pprint_tweet(tweet)
    if not relevante():
        pass
    else:
        tagged.append(tweet)

pprint(tagged[-1]['tweet'])    
