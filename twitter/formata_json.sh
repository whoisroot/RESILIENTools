#!/bin/bash

# Inclui "[" no início do arquivo para transformar os tweets em um array
sed -i '1s/{/\[\{/' $1

# Adiciona uma virgula ao final de cada linha/tweet
sed -i 's/\}$/\},/g' $1

# Inverte a ordem das linhas, troca a primeira (originalmente a última) "," por "]"
# para fechar o array e desinverte as linhas. O resultado é salvo em um arquivo
# temporário para não sobrescrever o original enquanto é lido
tac $1 | sed '1s/\},$/}]/' | tac > /tmp/tmp_file

# Sobrescreve o arquivo original com o dos tweets organizados em um array
cp /tmp/tmp_file $1
