# mongoimport -h ds115573.mlab.com:15573 -d cards-against-humanity -c cards -u admin -p password1 --jsonArray base.json
import random, fileinput, sys


def create_id(id_length):
    id = ''
    characters = "ABCDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
    for i in range(id_length):
        id += random.choice(characters)
    return id


filename = 'base.json'
text_to_search = '{'

for line in fileinput.input(filename, inplace=1):
    replacement_text = '{\n\t\"_id\": \"' + create_id(24) + '\",'
    if text_to_search in line:
        line = line.replace(text_to_search, replacement_text)
    sys.stdout.write(line)
