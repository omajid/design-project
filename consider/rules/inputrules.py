
import re

from twisted.python import log

# This file contains rules for processing input files
#


# regexp -> function to manipulate input
nameRules = {}


# all rules are functions. input is the parse tree ?!?
# output is the modified parse tree

def slashdot(soup):
    log.msg('rules.slashdot(): processing slashdot.org')
    junk = soup.body.findAll(True, {'class': re.compile(r'\badvertisement\b') } ) 
    [junkSection.extract() for junkSection in junk]
    return soup

nameRules[r'.*slashdot\.org\b'] = slashdot
