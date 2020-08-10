#!/bin/bash

sed -i '1s/{/\[\{/' $1
sed -i 's/\}$/\},/g' $1
tac $1 | sed '1s/\},$/}]/' | tac > /tmp/tmp_file
cp /tmp/tmp_file $1
