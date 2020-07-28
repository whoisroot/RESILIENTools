#!/bin/python

import json, sys, colorama
from pprint import pprint, pformat
from os import environ, path, stat, system

vrd = colorama.Fore.GREEN
vrm = colorama.Fore.RED
azl = colorama.Fore.BLUE
amrl = colorama.Fore.LIGHTYELLOW_EX
rst = colorama.Fore.RESET
cnz = colorama.Fore.LIGHTBLACK_EX

tag_file = 'tags.json'
tweet_file = 'tagged_tweets.json'

if __name__ == '__main__':
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
            f.write('{}')
        tags = {}
    main()


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
    print(vrd+tab+"Retweets: "+rst+str(post['retweets_count'])+tab*3+vrd+"Likes: "+rst+str(post['likes_count']))

    return

def display(images):
    if not sys.platform.startswith('linux'):
        return
    if prompt("Esse post contém imagens. Deseja exibi-las?"):
        if environ['TERM'] == 'xterm-kitty':
            for image in images:
                system('kitty +kitten icat "'+image+'"')
        elif environ['XDG_SESSION_TYPE'] != 'tty':
            for image in images:
                system('xdg-open "'+image+'"')
        else:
            print(vrm+"Erro: "+rst+"Este terminal não suporta exibição de imagens e não detecto estar em uma sessão gráfica")
    return

def prompt(pergunta):
    value = ""
    while value != "S" and value != "N":
        value = input(pergunta,"(S/N)\n-> ")[:1].upper()
    if value == 'S':
        return True
    else:
        return False

def tag(pergunta,tags):
    aplicadas = []
    new = False
    no_tags = False
    temp = "\n"
    for i, tag in enumerate(tags):
        temp += cnz+'['+str(i)+'] '+rst+tag+'  '
    print(vrm+"\nDigite o número das tags separados por espaços ou vírgulas e/ou (n/N) para adicionar novas tags.\nCaso a pergunta não aplique, apenas digite (X/x)\n"+amrl+pergunta)
    while len(aplicadas) == 0 and not new and not no_tags:
        aplicadas = input(temp[:-2]+"\n-> ").replace(' ','%').replace(',','%').split('%')
        if 'n' in aplicadas or 'N' in aplicadas:
            nova_tag = "*"
            while nova_tag != "":
                i += 1
                nova_tag = input("Digite uma nova tag ou Enter para encerrar: ")
                if nova_tag != '':
                    aplicadas.append(str(i))
                    tags.append(nova_tag)
            new = True
            save_tags()
        if 'x' in aplicadas or 'X' in aplicadas:
            no_tags = True
        aplicadas[:] = [int(a) for a in aplicadas if a.isdecimal() and int(a) <= i]
    aplicadas = list(set(aplicadas))
    if no_tags:
        return
    aplicadas = list(set(aplicadas))
    return [tags[i] for i in aplicadas]

def main():
    if path.exists(tweet_file):
        if stat(tweet_file).st_size >  0:
            with open(tweet_file) as f:
                tagged = json.load(f)
        else:
            tagged = []
    else:
        tagged = []
    tagger()
    save_tweets(tagged, tweets)
    return

def tagger():
    try:
        for i in range(1,len(tweets)):
            tweet = tweets.pop()
            system("clear")
            print(i,"\n\n")
            pprint_tweet(tweet)
            if not prompt("Esse post é relevante para o estudo?"):
                pass
            else:
                tweet['relevante'] = True
                if tweet['photos'] != []:
                    display(tweet['photos'])
                for cat in perguntas.keys():
                    categoria = perguntas[tag]
                    if categoria ['bool']:
                        tweet[cat] = prompt(categoria['pergunta'])
                    else:
                       tweet[cat] = tag(categoria['pergunta'], tags[cat])
                tagged.append(tweet)

            if i%10 == 0:
                save_tweets(tagged, tweets)
                pass
        return
    except KeyboardInterrupt:
        save_tweets(tagged, tweets)
        if prompt("Você deseja mesmo encerrar?"):
            print(vrm+'\n\nEncerrando programa...\n')
            sleep(0.5)
            print(amrl+'Salvando tweets rotulados...')
            sleep(0.5)
            print(vrd+'\nSalvos!\n\n'+azl+'Adeus!!'+rst)
            exit(0)
        else:
            tagger()

