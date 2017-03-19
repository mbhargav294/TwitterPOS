#!/usr/bin/env python

from optparse import OptionParser
import os, logging, collections
import utils

def create_model(sentences):
    model = None
    ## YOUR CODE GOES HERE: create a model
    wordTagCount = collections.defaultdict(lambda: collections.defaultdict(int))
    for sentence in sentences:
        for token in sentence:
            wordTagCount[token.word][token.tag] += 1

    model = wordTagCount
    return model

def predict_tags(sentences, model):
    ## YOU CODE GOES HERE: use the model to predict tags for sentences
    for sentence in sentences:
        for token in sentence:
            ## you can access token.word and self.tag (see utils.py for details)
            try:
                maxTag = max(model[token.word], key=model[token.word].get)
            except:
                maxTag = "N"
            token.tag = maxTag
    return sentences

if __name__ == "__main__":
    usage = "usage: %prog [options] GOLD TEST"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug", action="store_true",
                      help="turn on debug mode")

    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("Please provide required arguments")

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    training_file = args[0]
    training_sents = utils.read_tokens(training_file)
    test_file = args[1]
    test_sents = utils.read_tokens(test_file)

    model = create_model(training_sents)

    ## read sentences again because predict_tags(...) rewrites the tags
    sents = utils.read_tokens(training_file)
    predictions = predict_tags(sents, model)
    accuracy = utils.calc_accuracy(training_sents, predictions)
    print "Accuracy in train set [%s tweets]: %s" % (len(sents), accuracy)

    ## read sentences again because predict_tags(...) rewrites the tags
    sents = utils.read_tokens(test_file)
    predictions = predict_tags(sents, model)
    accuracy = utils.calc_accuracy(test_sents, predictions)
    print "Accuracy in test set [%s tweets]: %s" % (len(sents), accuracy)
