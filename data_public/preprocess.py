#!/usr/bin/env python

from optparse import OptionParser
import os, logging, collections, re

def read_tokens(file):
    f = open(file)
    f1 = open("output.txt", "w")
    sentences = []
    for l in f.readlines():
        #l = "<s>/<s> " + l + " <$>/<$>"
        if re.match("TWEET.*", l):
            f1.write("\n")
        elif re.match("TOKENS.*", l):
            continue
        else:
            tokens = l.split()
            token = None
            tag = None
            i = 0
            for tok in tokens:
                if i == 0:
                    tag = tok
                    i += 1
                else:
                    token = tok
            #print token, tag
            if token != None and tag != None:
                f1.write(token+"/"+tag+" ")
            #print tokens
    f1.close()
    f.close()

if __name__ == "__main__":
    usage = "usage: %prog [options] GOLD SYSTEM"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug", action="store_true",
                      help="turn on debug mode")

    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Please provide required arguments")

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    read_tokens(args[0])