#! /usr/bin/env python

import json, sys, colorama
from pprint import pprint, pformat
from os import environ, path, stat, system
from time import sleep
from wget import download

"""
    Atalhos para constantes da biblioteca colorama,
    utilizada colorir o texto a ser exibido na tela
"""
vrd = colorama.Fore.GREEN
vrm = colorama.Fore.RED
azl = colorama.Fore.BLUE
amrl = colorama.Fore.LIGHTYELLOW_EX
rst = colorama.Fore.RESET
cnz = colorama.Fore.LIGHTBLACK_EX

"""
    Salva os rótulos conhecidos até agora
"""
def save_tags():
    with open(tag_file,'w') as f:
        f.write(tags)
    return

"""
    Salva os arquivos JSON com a totalidade dos tweets
"""
def save_tweets(tagged, left):
    # Tweets limpos e rotulados
    with open(tweet_file,'w') as f:
        json.dump(tagged,f)
    # Tweets restantes/sem classificação
    with open(raw_tweet_file,'w') as f:
        json.dump(left,f)
    return

"""
    Formata e exibe o tweet de forma estruturada e "bonita", destacando o conteúdo
    e metadados do tweet, como data, autor e número de likes e retweets.
"""
def pprint_tweet(post):
    tab = " "*4
    tweet = post['tweet']
    sz = 80 # Largura máxima de cada linha, em caracteres
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

"""
    Caso a postagem contenha imagens, essa função controla como serão exibidas
"""
def display(images):
    # Atualmente a função só funciona em ambiente GNU/Linux
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
            print(vrm+"Erro: "+rst+"Este terminal não suporta exibição de imagens e não detecto estar em uma sessão gráfica.\n\
                    De OK para continuar ou Ctrl+C para interromper.")
            input(amrl+"\n[OK]"+rst)
    return

"""
    Interface facilitada para perguntas do tipo "Sim ou Não"
"""
def prompt(pergunta):
    value = ""
    print('\n'+amrl+pergunta)
    while value != "S" and value != "N":
        value = input(cnz+"[S/N]"+rst+"\n-> ")[:1].upper()
    if value == 'S':
        return True
    else:
        return False

"""
    Exibe uma pergunta e os rótulos associados a ela até então, dando a opção de adicionar
    novas tags ou ignorar a pergunta, caso ela não se aplique ao conteúdo do post
"""
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

"""
    Função de inicialização do rotulador para o funcionamento independente
"""
def main():
    # Carrega os tweets coletados
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
            tags = f.read().split('\n')
    except FileNotFoundError:
        tags = []
        with open(tag_file, 'w') as f:
            f.write('[]\n')

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

"""
    Função principal executada no rotulador para tratar os posts
"""
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
                tweet['palavras_chave'] = tag("Quais das palavras chaves se aplicam?", tags)
                tagged.append(tweet)

            if i%10 == 0:
                save_tweets(tagged, tweets)
                system("rm /tmp/rotulador_imgs/*")
        return
    # Caso o usuário envie CTRL+C para interromper a execução do programa
    except KeyboardInterrupt:
        # Salva o estado atual de execução
        if prompt("Você deseja mesmo encerrar?"):
            print(vrm+'\n\nEncerrando programa...\n')
            save_tweets(tagged, tweets)
            sleep(0.5)
            print(amrl+'Salvando tweets rotulados...')
            tweets.append(tweet)
            sleep(0.5)
            print(vrd+'\nSalvos!\n\n'+rst)
            exit(0)
        # Retorna à função de rotulamento
        else:
            tagger(tweets, tags, tagged,perguntas)


"""
    Tratamento inicial de parâmetros de linha de comando e configuração de constantes para execução indendente
"""
if __name__ == '__main__':
    tag_file = '../Palavras-chave.txt'
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

