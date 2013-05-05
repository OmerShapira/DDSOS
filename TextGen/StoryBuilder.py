import json
from csv import DictReader
import re
from random import choice
#import nltk

countriesFile = "countries-alpha-2.json"
attackFile = "DDOS_Geo.csv"
#TODO: adapt this to multiple Values
attackType = 'BOTNET_DDOS'

# this will be a LIST of DICTIONARIES
attackEntries = []
countryDict = {}

numbers = {'1': "One", '2': "Two", '3': "Three", '4': "Four", '5': "Five", '6': "Six", '7': "Seven", '8': "Eight", '9': "Nine"}

sym_dictionary = {'!': 'exclamation point', '#': 'number sign', '"': 'double quotes', '%': 'percent sign', '$': 'dollar sign', "'": 'single quote', '&': 'ampersand', ')': 'closing parenthesis', '(': 'opening parenthesis', '+': 'plus sign', '*': 'asterisk', '-': 'hyphen', ',': 'comma', '/': 'slash', '.': 'period'}

ascii_dict = reduce(lambda x, y: x + y.items(), [numbers, sym_dictionary], [])


templateMatcher = re.compile('\$\w+')


def main():
    loadAttackEntries(attackFile)
    loadCountryData(countriesFile)
    #print attackEntries
    for attackData in attackEntries:
        print genTemplate(attackType, attackData)


def loadAttackEntries(attackFile):
    global attackEntries
    with open(attackFile) as csvFile:
        reader = DictReader(csvFile)
        attackEntries = [row for row in reader]
    # print attackEntries


def loadCountryData(countriesFile):
    global countryDict
    with open(countriesFile) as jsonFile:
        decodedJson = json.load(jsonFile)
        countryDict = {entry['alpha-2'] : entry['name'] for entry in decodedJson}


def genTemplate(attackType, attackData):
    '''
    Using a dictionary attackData and a keyword attackType, generate a sentence out of the list of possible sentences, using default values if no information is given.
    '''
    compiled = ""
    try:
        #Get the entry. May fail, hence the 'try'
        templateEntry = templates[attackType]
        #extract dictionary
        templateDict = templateEntry[1]
        #Get a random sentence from the list
        templateString = choice(templateEntry[0])
        # Get the toString functions
        toStringFunctions = templateEntry[2]

        #literate programming yo
        def keyToAttackValue(key):
            # may throw KeyError, hence the try:
            possibleValues = templateDict[key.group(0)]
            for i in xrange(len(possibleValues) - 1):
                replacement = attackData.get(possibleValues[i], '')
                #pick the first description which isn't empty
                if replacement is not '':
                    toString = toStringFunctions.get(possibleValues[i], lambda x : x)
                    return toString(replacement)

            #else, return the last (default) value
            return possibleValues[-1]

        #find all the matchable keys
        # keys = templateMatcher.findall(templateString)
        # compiledKeys = [keyToAttackValue(key) for key in keys]
        # print zip(keys, compiledKeys)
        # replace using regex
        compiled = templateMatcher.sub(keyToAttackValue, templateString)
    except :
        compiled = "SYSTEM ERROR : CANNOT COMPILE ATTACK DATA"
    finally:
        return compiled


def country(short):
    "Translates a 2-symbol country code to a country name"
    return countryDict.get(short.upper()[:2], short)


def symbolFormat(symbol):
    "Returns a string format out of any series of characters. If it isn't a number, returns the original character. Assumes dictionaries are disjoint"
    return ' '.join(map(lambda x : numbers.get(x, x), [str(sym) for sym in symbol.strip()]))


templates = {
    # Date,Time,C&C,C&C Port, C&C, C&C Geo, C&C DNS,Channel,Command,TGT,TGT ASN  ,TGT Geo,TGT DNS
    "BOTNET_DDOS":
    # String templates
    (["Attack on $TGTGEO . Repeat, attack on $TGTGEO . A commmand and control post from $CCGEO issued a Distributed denial of service attack on $TGTADDR . Attack started at $TIME . Command and control server traced to $CCADDR."],
    #Order of preference for data
    {
    "$TGTGEO" : ("TGT Geo", "an unknown location"),
    "$CCGEO"  : ("C&C Geo", "an unknown location"),
    "$TGTADDR": ("TGT DNS", "TGT", "an unknown address"),
    "$CCADDR": ("C&C DNS", "C&C", "an unknown address"),
    "$TIME"   : ("Time", "an unknown time")
    },
    #Dictionary for data to speech functions
    {
    "C&C Geo" : country,
    "TGT Geo" : country
    })
}


if __name__ == '__main__':
    main()
