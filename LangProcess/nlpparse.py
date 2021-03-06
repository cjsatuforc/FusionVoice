# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 12:57:35 2016

@author: charu
"""
import sys
sys.path.append("/usr/local/lib/python3.5/site-packages/")
import nltk


UNITS_DICT = {"inches":1, "inch":1, "centimeter":1, "centimeters":1, "millimeter":1, "millimeters":1,\
    "meters":1, "meters":1}

PUNCTUATION_LIST = {".":1} #to be determined

COMMAND_VERBS = {"saw":1, "ate":1, "walked":1, "draw":{"circle":{"diameter":UNITS_DICT, "radius":UNITS_DICT}, "square":{"side":UNITS_DICT, None:UNITS_DICT}}, \
    "design":{"gear":1, "spring":1}, "extrude":{"circle":{None:UNITS_DICT}, "square":{None:UNITS_DICT}, "sketch":{None:UNITS_DICT}, None:{None:UNITS_DICT}, "inches":{None:UNITS_DICT}, "inch":{None:UNITS_DICT}, "centimeter":{None:UNITS_DICT}, "centimeters":{None:UNITS_DICT}, "millimeter":{None:UNITS_DICT}, "millimeters":{None:UNITS_DICT},\
    "meters":{None:UNITS_DICT}, "meters":{None:UNITS_DICT}}, "open":{ "sketch":{None:[], "plane":[]} } }

grammar1 = nltk.CFG.fromstring("""
  S -> NP VP | VP
  VP -> V | V NP | V NP PP | V PP NP
  PP -> P NP
  V -> "saw" | "ate" | "walked" | "draw" | "design" | "extrude" | "open" | "create"
  NP -> "john" | "mary" | "bob" | "filler" | Det N | Det N PP | N | N PP | Det AdjP N | AdjP Ns
  Det -> "a" | "an" | "the" | "my"
  AdjP -> Adj
  Adj -> "new"
  N -> "circle" | "square" | "diameter" | "gear" | "sphere" | "radius" | "sketch" | "inches" | "inch" | "centimeters" | "centimeter" | "millimeter" | "millimeters" | "meters" | "meter" | "teeth" | "side" | "plane"
  P -> "in" | "of" | "by" | "with" | "on"
  """)


sr_parser = nltk.ChartParser(grammar1)

def remove_punctuation(sentence):
    sentence = sentence.split()
    new_sentence = [val for val in sentence if val not in PUNCTUATION_LIST]


def is_param_val(num):
    try:
        float(num)
        return True
    except ValueError:
        if num == "xy" or num == "yx" or num == "yz" or num == "zy" or num == "xz" or num =="zx":
            return True
        return False

def is_float(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def parse_for_number(sent):
    new_str = []
    temp_val = []
    for x in range(len(sent)):
        if is_param_val(sent[x]):
            if is_float(sent[x]):
                temp_val.append(float(sent[x]))
            else:
                temp_val.append(sent[x])
        else:
            new_str.append(sent[x])
    return new_str, temp_val


def find_command(tree,  sentence, numlist):
    print("finding command...")
    #Find verb
    VPs = list(tree.subtrees(filter=lambda x: x.label()=='VP'))
    '''
    for VP in VPs:
        for subtree in list(VP.subtrees(filter=lambda x: x.label()=='V')):
            if str(subtree.leaves()[0]) in COMMAND_VERBS:
                valid_VPs.append(VP)
                '''
    #print(VPs)

    valid_VPs = [(subtree.leaves()[0], VP) for VP in VPs for subtree in list(VP.subtrees(filter=lambda x: x.label()=='V')) \
        if str(subtree.leaves()[0]) in COMMAND_VERBS]

    if len(valid_VPs) == 0:
        return []

    print("Valid VPs:" + str(valid_VPs))
    #Find object

    '''
    for VP in valid_VPs:
        for x in range(len(VP)):
            if VP[1][x].label() == 'NP':
                OBJ_NPs.append(VP[1][x])
                '''

    OBJ_NPs = [(VP[0], VP[1][x]) for VP in valid_VPs for x in range(len(VP)) if VP[1][x].label()=='NP']

    '''
    for NP in OBJ_NPs:
        for subtree in range(len(NP[1])):
            if NP[1][subtree].label() == 'N' and NP[1][subtree].leaves()[0] in COMMAND_VERBS[NP[0]]:
                valid_OBJ_NPs.append( (NP[0], NP[1][subtree].leaves()[0], NP[1]) )
    '''

    valid_OBJ_NPs = [(NP[0], NP[1][subtree].leaves()[0], NP[1]) for NP in OBJ_NPs for subtree in range(len(NP[1])) \
        if NP[1][subtree].label() == 'N' and NP[1][subtree].leaves()[0] in COMMAND_VERBS[NP[0]]]

    if len(valid_OBJ_NPs) == 0:
        return []
    print("Valid OBJ_NPs:" + str(valid_OBJ_NPs))

    #Find parameters

    PARAMS = []

    for OBJ_NP in valid_OBJ_NPs:
        PARAMS_LIST = []
        for subtree in list(OBJ_NP[2].subtrees(filter=lambda x: x.label()=='N')):
            if subtree.leaves()[0] in COMMAND_VERBS[OBJ_NP[0]][OBJ_NP[1]]:
                PARAMS_LIST.append(subtree.leaves()[0])
        if len(PARAMS_LIST) > 0 or (None in COMMAND_VERBS[OBJ_NP[0]][OBJ_NP[1]]):
            PARAMS.append( (OBJ_NP[0], OBJ_NP[1], PARAMS_LIST, OBJ_NP[2]) )

    #possibly missed the prepositional phrase because of the way nlp parsed it

    for PARAM in PARAMS:
        if len(PARAM[2]) == 0:
           # print("ran")
            for key in COMMAND_VERBS[PARAM[0]][PARAM[1]]:
                print(key)
                print(sentence)
                if key in sentence:
                    #print("truu")
                    PARAM[2].append(key)


    print("PARAMS: " + str(PARAMS))
    PARAMS_and_UNITS = []

    for OBJ_NP in PARAMS:
        UNITS_LIST = []
        param_ind = 0
       # print(OBJ_NP[3])
        for subtree in list(OBJ_NP[3].subtrees(filter=lambda x: x.label()=='N')):
            if len(OBJ_NP[2]) <= param_ind:
                break
            if subtree.leaves()[0] in COMMAND_VERBS[OBJ_NP[0]][OBJ_NP[1]][OBJ_NP[2][param_ind]]:
                UNITS_LIST.append(subtree.leaves()[0])
                param_ind += 1
        print(OBJ_NP)
        if len(OBJ_NP[2]) > 0 and COMMAND_VERBS[OBJ_NP[0]][OBJ_NP[1]][OBJ_NP[2][0]] == UNITS_DICT:
            if len(UNITS_LIST) == len(OBJ_NP[2]):
                PARAMS_and_UNITS.append( (OBJ_NP[0], OBJ_NP[1], OBJ_NP[2], UNITS_LIST) )
        else:
            PARAMS_and_UNITS.append( (OBJ_NP[0], OBJ_NP[1], OBJ_NP[2], numlist) )


#    print(PARAMS_and_UNITS)

    return PARAMS_and_UNITS

#sent = 'open a sketch'

#should be run with a try catch 
def parse_sentence(sentence):

    sentence = sentence.lower()
    sent = sentence.split(' ')
    sent, numlist = parse_for_number(sent)

    parsed = sr_parser.parse(sent)
    #print(sent)
    command_dict = {}
    for tree in sr_parser.parse(sent):
        print(tree)
    possible_commands = [find_command(tree, sent, numlist) for tree in sr_parser.parse(sent)]
    print(possible_commands)
    possible_commands = [subcommand for command in possible_commands for subcommand in command if len(command) > 0]
    possible_commands = [command for command in possible_commands if len(command[3]) == len(numlist)]
    possible_commands = [(command[0], command[1], command[2], list(zip(numlist, command[3]))) for command in possible_commands]

    return possible_commands


#print(parse_sentence(sent))

#for tree in sr_parser.parse('draw a square with a side of inches'.split(' ')):
 #   print(tree)
    

    
                
            
                
                