#!/usr/bin/env python

from optparse import OptionParser
import os, logging, collections, math
import utils, re

smoothing = '1'

def estimateLambdas(tagUnigram, tagBigram):
    lambda1 = 0.0
    lambda2 = 0.0
    lambda1 = len(tagUnigram)
    for key, value in tagBigram.iteritems():
        lambda2 += len(value)
    lamSum = lambda1 + lambda2
    lambda1 = lambda1/lamSum
    lambda2 = lambda2/lamSum
    lambdas = [lambda1, lambda2]
    return lambdas

def readInput():
	print "\n\nTWITTER DATA POS TAGGER\n---------------------------------\n\n"
	
	global smoothing
	print "Enter which smoothing to apply \n1) Linear Interpolation\n2) Laplace (Add 1)\n\n", "Enter your choice: "
	smoothing = raw_input()
	if smoothing != '1' and smoothing != '2' and smoothing != '3':
		print "Default value is taken -- 1"
		smoothing = '1'

def create_model(sentences):
    model = None
    ## YOUR CODE GOES HERE: create a model
    readInput()
    tagCount = collections.defaultdict(float)
    wordList = collections.defaultdict(float)
    
    tagCountBigram = collections.defaultdict(lambda: collections.defaultdict(float))
    tagProbBigram = collections.defaultdict(lambda: collections.defaultdict(float))
    wordTagCount = collections.defaultdict(lambda: collections.defaultdict(float))
    wordTagProb = collections.defaultdict(lambda: collections.defaultdict(float))

    singleTimeWords = 0
    for sentence in sentences:
        for i in range(len(sentence)):
            wordTagCount[sentence[i].word][sentence[i].tag] += 1.0
            #if sentence[i].tag == ',':
            #    print sentence[i].word
            tagCount[sentence[i].tag] += 1.0
            wordList[sentence[i].word] += 1.0

    for sentence in sentences:
        for i in range(len(sentence)):
            if i < len(sentence) - 1:
                tagCountBigram[sentence[i].tag][sentence[i+1].tag] += 1.0

    for key1, value1 in wordTagCount.iteritems():
        for key2, value2 in value1.iteritems():
            if wordList[key1] == 1:
                    singleTimeWords += 1.0
            wordTagProb[key1][key2] = wordTagCount[key1][key2]/tagCount[key2]

    noTags = len(tagCount)
    
    lambdas = estimateLambdas(tagCount, tagCountBigram)
    
    global smoothing
    if smoothing == '2':
        #Laplace
        for key1, value1 in tagCount.iteritems():
            for key2, value2 in tagCount.iteritems():
                tagProbBigram[key1][key2] = (tagCountBigram[key1][key2]+1)/(tagCount[key1] + len(tagCount))
    elif smoothing == '1':
        #Linear Interpolation
        lam1 = lambdas[0]
        lam2 = lambdas[1]
        for key1, value1 in tagCount.iteritems():
            for key2, value2 in tagCount.iteritems():
                tagProbBigram[key1][key2] = lam2*(tagCountBigram[key1][key2]/tagCount[key1]) + lam1*(tagCount[key2]/len(wordList))
    else:
        readInput()
    model = [tagCount, tagProbBigram, wordTagProb, wordList, lambdas, wordTagCount, singleTimeWords]
    print "Training Completed"
    print "Should wait around 4 mins for every 10,000 sentences\n"
    return model

def predict_tags(sentences, model):
    ## YOU CODE GOES HERE: use the model to predict tags for sentences
    tagCount = model[0]
    tagProbBigram = model[1]
    wordTagProb = model[2]
    wordList = model[3]
    lambdas = model[4]
    wordTagCount = model[5]
    singleTimeWords = model[6]
    lam1 = lambdas[0]
    lam2 = lambdas[1]
    
    tagIndex = []
    for key in tagCount:
        if key == '<s>':
            continue
        tagIndex.append(key)
    
    abc = 1
    for sentence in sentences:
        #print abc
        #abc += 1
        #if abc == 50:
        #    break
        Viterbi = [{}]
        noOfWords = len(wordList)
        senLen = len(sentence)
        for i in range(1, senLen):
            word = sentence[i].word
            if wordList[word] == 0:
                matched = 0
                hash = re.match('^#.*',word)
                user = re.match('^@.*',word)
                nums = re.match('.*[0-9].*',word)
                urls = re.match('(^http.*)|(^www.*)',word)
                emoticon = re.match(':.',word)
                proper = re.match('[A-Z]',word)
                verb = re.match('.*ing$|.*ed$|.*in$|.*\'t$|.*\'nt$',word)
                adj = re.match('.*ed$', word)
                adverb = re.match('.*ly$', word)
                inter = re.match('^[A-Z]{2,5}$', word)
                abb = re.match('([a-zA-Z])(\\1)+', word)
                retweets = re.match('\\.\\.\\.', word)
                if i <= 3:
                    wordTagProb[word]['^'] = singleTimeWords/noOfWords
                    matched = 1
                if hash != None:
                    wordTagProb[word]['#'] = singleTimeWords/noOfWords
                    wordTagProb[word]['^'] = 0
                    matched = 1
                if user != None:
                    wordTagProb[word]['@'] = singleTimeWords/noOfWords
                    wordTagProb[word]['^'] = 0
                    matched = 1
                if nums != None:
                    wordTagProb[word]['$'] = singleTimeWords/noOfWords
                    wordTagProb[word]['^'] = 0
                    matched = 1
                if urls != None:
                    wordTagProb[word]['U'] = 50 * singleTimeWords/noOfWords
                    wordTagProb[word]['^'] = 0
                    matched = 1
                if emoticon != None:
                    wordTagProb[word]['E'] = singleTimeWords/noOfWords
                    wordTagProb[word]['^'] = 0
                    matched = 1
                if proper != None:
                    wordTagProb[word]['^'] = singleTimeWords/noOfWords
                    matched = 1
                if verb != None:
                    wordTagProb[word]['V'] = singleTimeWords/noOfWords
                    wordTagProb[word]['^'] = 0
                    matched = 1
                if adj != None:
                    wordTagProb[word]['A'] = singleTimeWords/noOfWords
                    wordTagProb[word]['^'] = 0
                    matched = 1
                if adverb != None:
                    wordTagProb[word]['R'] = singleTimeWords/noOfWords
                    wordTagProb[word]['^'] = 0
                    matched = 1
                if inter != None:
                    wordTagProb[word]['!'] = singleTimeWords/noOfWords
                    wordTagProb[word]['^'] = 0
                    matched = 1
                if abb != None:
                    wordTagProb[word]['!'] = singleTimeWords/noOfWords
                    wordTagProb[word]['^'] = 0
                    matched = 1
                if retweets != None:
                    print word
                    wordTagProb[word]['~'] = singleTimeWords/noOfWords
                    wordTagProb[word]['^'] = 0
                    matched = 1
                if matched == 0:
                    wordTagProb[word]['N'] = 1 * singleTimeWords/noOfWords
            if i == 1:
                for key in tagIndex:
                    wordProb = wordTagProb[word][key]
                    prevBigram = tagProbBigram['<s>'][key]
                    Viterbi[i-1][key] = {"Prob": wordProb * prevBigram, "Prev": None}
            else:
                Viterbi.append({})
                for key in tagIndex:
                    max_val = max(Viterbi[i-2][key1]["Prob"] * tagProbBigram[key1][key] for key1 in tagIndex)
                    for key1 in tagIndex:
                        if max_val == Viterbi[i-2][key1]["Prob"] * tagProbBigram[key1][key]:
                            Viterbi[i-1][key] = {"Prob": max_val * wordTagProb[word][key], "Prev": key1}
                            break
        prev_tag = None
        for i in range(senLen-1,0,-1):
            word = sentence[i].word
            max_prob = 0
            max_prev = None
            if i == len(sentence)-1:
                for key,val in Viterbi[i-1].iteritems():
                    if val["Prob"] >= max_prob:
                        max_prob = val["Prob"]
                        max_prev = val["Prev"]
                        max_curr = key
                sentence[i].tag = max_curr
                prev_tag = max_prev
            else:
                sentence[i].tag = prev_tag
                prev_tag = Viterbi[i-1][prev_tag]["Prev"]
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
