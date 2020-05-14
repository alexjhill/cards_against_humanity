import random

def create_id(id_length):
    id = ''
    characters = "ABCDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
    for i in range(id_length):
        id += random.choice(characters)
    return id
