#! /usr/bin/env python

import json, sys, colorama
from pprint import pprint, pformat
from os import environ, path, stat, system
from time import sleep
from wget import download

vrd = colorama.Fore.GREEN
vrm = colorama.Fore.RED
azl = colorama.Fore.BLUE
amrl = colorama.Fore.LIGHTYELLOW_EX
rst = colorama.Fore.RESET
cnz = colorama.Fore.LIGHTBLACK_EX

def save_tags():
    with open(tag_file,'w') as f:
        json.dump(tags,f)
    return

def save_tweets(tagged, left):
    with open(tweet_file,'w') as f:
        json.dump(tagged,f)
    with open(raw_tweet_file,'w') as f:
        json.dump(left,f)
    return

def pprint_tweet(post):
    tab = " "*4
    tweet = post['tweet']
    sz = 80
    print(tab+vrm+"Data: "+vrd+post['date']+" "+post['time']+rst)
    print(tab+vrm+"Tweet: "+rst)
    if len(tweet)>sz:
        out = ""
        for line in pformat(tweet, width=sz):
                out += line.replace('\'','').replace('(','').replace('\\n','\n')
        for a in out.split('\n'):
                print(tab*2+a.strip('\\n').strip(' '))

    else:
        print(tab*2+tweet+"\n")
    print(vrd+tab+"Retweets: "+rst+str(post['retweets_count'])+tab*3+vrd+"Likes: "+rst+str(post['likes_count'])+tab*3+vrd+"User: "+rst+post['username'])

    return

def display(images):
    if not sys.platform.startswith('linux'):
        return
    if prompt("Esse post contém imagens. Deseja exibi-las?"):
        if environ['TERM'] == 'xterm-kitty':
            for image in images:
                system('kitty +kitten icat "'+image+'"')
                input(vrm+"\n\n[OK]"+rst)
        elif environ['XDG_SESSION_TYPE'] != 'tty':
            for image in images:
                path = "/tmp/rotulador_imgs/"+image.rsplit('/',1)[1]
                download(image, path, bar=None)
                system('xdg-open "'+path+'"')
        else:
            print(vrm+"Erro: "+rst+"Este terminal não suporta exibição de imagens e não detecto estar em uma sessão gráfica.\nDe OK para continuar ou Ctrl+C para interromper.")
            input(amrl+"\n[OK]"+rst)
    return

def prompt(pergunta):
    value = ""
    print('\n'+amrl+pergunta)
    while value != "S" and value != "N":
        value = input(cnz+"[S/N]"+rst+"\n-> ")[:1].upper()
    if value == 'S':
        return True
    else:
        return False

def tag(pergunta,tag_values):
    aplicadas = []
    new = False
    no_tags = False
    temp = "\n"
    i = 0
    for i, tag in enumerate(tag_values):
        temp += cnz+'['+str(i)+'] '+rst+tag+'  '
    temp += cnz+'\n[n] '+rst+'Adicionar nova tag    '+cnz+"[x]"+rst+" Pergunta não se aplica"
    print(vrm+"\nDigite o número das tags separados por espaços ou vírgulas.\n\n"+amrl+pergunta+rst)
    while len(aplicadas) == 0 and not new and not no_tags:
        aplicadas = input(temp+"\n-> ").replace(' ','%').replace(',','%').split('%')
        if 'n' in aplicadas or 'N' in aplicadas:
            nova_tag = "*"
            while nova_tag != "":
                if i != 0:
                    i += 1
                nova_tag = input("Digite uma nova tag ou Enter para encerrar: ")
                if nova_tag != '':
                    aplicadas.append(str(i))
                    tag_values.append(nova_tag)
            new = True
            save_tags()
        if 'x' in aplicadas or 'X' in aplicadas:
            no_tags = True
        aplicadas[:] = [int(a) for a in aplicadas if a.isdecimal() and int(a) <= i]
    aplicadas = list(set(aplicadas))
    if no_tags:
        return
    aplicadas = list(set(aplicadas))
    return [tag_values[i] for i in aplicadas]

def main():
    try:
        with open(raw_tweet_file) as f:
            tweets = json.load(f)
    except FileNotFoundError:
        print("O arquivo não existe.\n"+vrm+"Por favor, verifique se o arquivo existe ou se\nnão digitou errado antes de tentar novamente."+rst)
        exit(0)

    with open('perguntas.json') as f:
        perguntas = json.load(f)

    global tags
    try:
        with open(tag_file) as f:
            tags = json.load(f)
    except FileNotFoundError:
        tags = {}
        with open(tag_file, 'w') as f:
            json.dump(tags,f)
    if not len(tags) > 0:
        print("tags if")
        for cat in perguntas.keys():
            tags[cat] = []

    if path.exists(tweet_file):
        if stat(tweet_file).st_size >  0:
            with open(tweet_file) as f:
                tagged = json.load(f)
        else:
            tagged = []
    else:
        tagged = []

    system("mkdir -p /tmp/rotulador_imgs")
    tagger(tweets, tags, tagged, perguntas)
    save_tweets(tagged, tweets)
    save_tags()

    return

def tagger(tweets, tags, tagged, perguntas):
    total = len(tweets)
    try:
        for i in range(1,len(tweets)):
            tweet = tweets.pop()
            system("clear")
            print(i,'/',total,"\n\n")
            pprint_tweet(tweet)
            if not prompt("Esse post é relevante para o estudo?"):
                pass
            else:
                tweet['relevante'] = True
                if tweet['photos'] != []:
                    display(tweet['photos'])
                for cat in perguntas.keys():
                    categoria = perguntas[cat]
                    if categoria ['bool']:
                        tweet[cat] = prompt(categoria['pergunta'])
                    else:
                        tweet[cat] = tag(categoria['pergunta'], tags[cat])
                tagged.append(tweet)

            if i%10 == 0:
                save_tweets(tagged, tweets)
                system("rm /tmp/rotulador_imgs/*")
        return
    except KeyboardInterrupt:
        tweets.append(tweet)
        save_tweets(tagged, tweets)
        if prompt("Você deseja mesmo encerrar?"):
            print(vrm+'\n\nEncerrando programa...\n')
            sleep(0.5)
            print(amrl+'Salvando tweets rotulados...')
            sleep(0.5)
            print(vrd+'\nSalvos!\n\n'+rst)
            exit(0)
        else:
            tagger(tweets, tags, tagged,perguntas)


if __name__ == '__main__':
    tag_file = 'tags.json'
    if len(sys.argv) < 2:
        print(vrm+"\nUso: "+rst+sys.argv[0]+" arquivo_com_tweets.json"+amrl+" [arquivo_com_os_rotulos]\n"+rst)
        exit(0)
    elif len(sys.argv) == 3:
        tag_file = sys.argv[2]
    raw_tweet_file = sys.argv[1]
    global tweets, tags, tagged
    name = raw_tweet_file.split('/')[-1].split('.')
    tweet_file = name[0]+"_tagged."+name[1]

    main()

