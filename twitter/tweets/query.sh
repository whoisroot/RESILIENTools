#!/bin/bash

div="------------------------------------------------------------------------"
while read evento; do
	info=($evento)
	cidade=${info[0]}
	since=${info[1]}
	until=${info[2]}
	ano=$(printf $since | cut -d"-" -f1)

	mkdir -p $cidade-$ano

	i=0
	while read QUERY; do
		i=$(( $i + 1 ))
		echo -e "\nQuery $i:\n$QUERY"
		echo -e "Cidade: $cidade\tSince: $since\tUntil: $until"
		twint -cq "$QUERY lang:pt since:$since until:$until" --json -o $cidade-$ano/${cidade}_$ano-query_$i.json -ho 2>&1
		echo -e "Query $i encerrada\n$div"
		sleep 5
	done < ../../queries.txt
done < ../../eventos.txt
