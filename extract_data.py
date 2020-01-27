#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 21:16:33 2019

@author: Katarina
"""

import re

def create_masterfile(): #BNC gaf me allemaal losse files, stop alles in 1 file
    for number in range(1,9):
        number = str(number)
        filename = "data"+number+".txt"
        process_file(filename, number)

def process_file(filename, n): #zet alle lines van de datafile bij de masterfile, incl. WRITTEN/SPOKEN
    datafile = open(filename, mode="r")
    n = int(n)
    if n < 5:
        spoken = True
    else:
        spoken = False
    for line in datafile:
        if spoken:
            masterfile.write("SPOKEN ")
        else:
            masterfile.write("WRITTEN ")
        linewords = re.split(" |\t", line)
        for word in linewords:
            if re.search("_", word) is not None:
                masterfile.write(f"{word} ")    
        masterfile.write("\n")
    datafile.close()
    
def create_testfile(): #om op te testen ivm runtime
    it = 0
    bigfile=open("masterfile.txt", mode="r")
    smallfile = open("testfile.txt", mode="w")
    for line in bigfile:
        it += 1
        if it%300 == 0:
            smallfile.write(line)
    smallfile.close()
    bigfile.close()
    
def is_messy(line): #'have to' is niet wat ik wil
    if re.search("_VH[A-Z] to_", line) is not None:
        return True
    else:
        return False
    
def is_ppp(line):        
    #if re.search("_VH[BZ][^,]+?_VBN[^,]+?_V[A-Z]G", line) is not None:
    regex = re.search("_VH[BZGI] [^,]+?_VBN [^,]+?_V[A-Z]G", line)
    if regex is not None:
        beendoing = re.search("_VBN [^,]+?_V[A-Z]G", regex.group())
        beendoing = beendoing.group()
        if re.search("_AT", beendoing) is None:
            if len(re.findall("_V[DV]N", regex.group())) > 0:
                return False
            elif(re.search("_PRP [a-z]+_V[DVH]G",beendoing)) is not None:
                return False
            elif(re.search("_VBN [a-z]+_AJ",beendoing)) is not None:
                return False
            return True
        else:
            return False
    else:
        return False

def is_pp(line):
    if re.search("_VBN", line) is not None:
        return False
    matching = re.search("_VH[BZGI] [^,]{,50}?_V[VBD]N", line)
    if matching is not None:
        matching = matching.group()
        if re.search("_AT", matching) is None:
            return True
        else:
            if re.search("_AT [a-z]+_V[VBD]N", matching) is not None:
                return True
            else:
                return False
    else:
        return False

def find_ppp_and_pp():
    messy = 0
    ppp = 0
    pp = 0
    restjes = 0
    bigfile=open("masterfile.txt", mode="r")
    for line in bigfile:
        if is_messy(line):
            messy += 1
            prullen.write(line)
        elif is_ppp(line):
            ppp += 1
            ppp_file.write(line)
        elif is_pp(line):
            pp += 1
            pp_file.write(line)
        else:
            restjes+=1
            rest.write(line)
    print(f"Aantal messy: {messy}\nAantal ppp:{ppp}\nAantal pp:{pp}\nAantal restjes:{restjes}")
    bigfile.close()
    
#masterfile = open("masterfile.txt", mode="w")
#create_masterfile()
#masterfile.close()
            
#create_testfile()

ppp_file = open("ppp_file.txt", mode="w")
pp_file = open("pp_file.txt", mode="w")
prullen = open("zooi.txt", mode="w")
rest = open("restjes.txt", mode="w")
find_ppp_and_pp()
pp_file.close()
ppp_file.close()
prullen.close()
rest.close()