#!/usr/bin/env python3
from sys import argv
import re
import json
import datetime

def printUsage():
    print('Usage:')
    print('\tpython3 zgodogrep.py [revision log file] [search regex]')

# parses the change and modifies data
# 
# return value is an extra note to be displayed in the output
def parseEl(change):
    global data
    global elemind
    if change['ty'] == 'is': # inserting a string
        ind = change['ibi']
        s = change['s']
        data = data[:ind-1] + s + data[ind-1:]
    elif change['ty'] == 'ds': # deleting part of the document
        data = data[:((change['si'])-1)] + data[change['ei']:]
    elif change['ty'] == 'mlti': # multiset of changes - perform all of them
        ret = []
        for el in change['mts']:
            notes = parseEl(el)
            ret.extend(notes)
        return ret
    elif change['ty'] == 'ae': # inserted image
        try:
            elemind += 1
            ind = change['epm']['ee_eo']
            return ['---- inserted element ' + str(elemind-1) + ' with name ' + ind['eo_ad']]
        except:
            return ['---- inserted element ' + str(elemind-1)]
    return []

dateformat = "%Y-%m-%d %H:%M:%S"
#debug = True
debug = False

if len(argv) < 3:
    pattern = None
    print("Not enough arguments")
    printUsage()
    exit(1)

# first argument is the filename
name = argv[1]
f = open(name, 'r')

# second argument is the search term
pattern = re.compile(argv[2], re.UNICODE)

beg = True
data = ""
elemind = 0

limit=0x10000000000
ind = 0

found = 0

# iterate over all the changes, 
# display revision if it countains the pattern
for line in f:
    if beg and not line.startswith("changelog"):
        continue
    elif beg:
        beg = False
        continue
    i = line.index("[")
    obj = json.loads(line[i:])
    notes = parseEl(obj[0])
    timestamp = datetime.datetime.fromtimestamp(obj[1]/1000.0).strftime(dateformat)

    if debug:
        print("====", timestamp)
        print(data)
        for note in notes:
            print(note)

    if pattern:
        s = pattern.search(data)
        if s:
            print("=== found instance ", found, "at step", ind, "on", timestamp)
            found += 1
            print(data)
            for note in notes:
                print(note)

    ind += 1
    if ind == limit:
        break
