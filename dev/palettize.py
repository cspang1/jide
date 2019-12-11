import json
from collections import defaultdict

def palettize(data):
    new = [{"name" : "test", "contents" : [[0]*8]*8}]*(len(data)+16)
    index = 0

    for i in range(int(len(data)/4)):
        new[index] = data[4*i]
        new[index+1] = data[4*i+1]
        new[index+16] = data[4*i+2]
        new[index+17] = data[4*i+3]
        index += 2
        if index % 16 == 0:
            index += 16

    return new
