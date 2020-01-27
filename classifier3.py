#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 11:36:23 2020

@author: hp
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 23:14:40 2019

@author: hp
"""
import nltk
from nltk.corpus import stopwords
import nltk.classify
import sklearn.datasets
import sklearn.metrics
import sklearn.model_selection
from sklearn.svm import SVC
import re
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.classify import SklearnClassifier
from sklearn.naive_bayes import BernoulliNB
from nltk.classify import maxent

def load_data(dir_name):
    return sklearn.datasets.load_files('%s' % dir_name, encoding='utf-8')

def get_other_counts(sentence):
    features = {}
    spokenstuff = 0
    questions = 0
    stopwordscount = 0
    time = 0
    humansubject = 0
    whenafter = 0
    whenbefore = 0
    addressee = 0
    existence_target = 0
    uncountable_NP = 0
    written = 0
    findstring = " ".join(sentence)
    if sentence[0] == "WRITTEN":
        written = 1
        features["WRITTEN"] = 1
    else:
        features["WRITTEN"] = 0
    sentence.pop(0)
    testing=False
    for index, word in enumerate(sentence):
        if testing:
            break
        if index > 1:
            ngram = "3gram_" + sentence[index-2] + "+" + sentence[index -1] + "+" + sentence[index]
            if ngram in features:
                features[ngram] =1
            else:
                features[ngram] = 1
        if re.search("(_ITJ|_UNC)", word) is not None:
            spokenstuff = 1
        elif re.search("(_AVQ|_DTQ)", word) is not None:
            questions = 1
        elif re.search("[A-Za-z0-9-']_VTARGET", word) is not None:
            word = word.lower()
            priorword = sentence[index-1]
            regex = re.compile("(np0|he_|man_|girl|boy|men_| i_|you_|er_n).*?%s"%word)
            if re.search(regex, priorword.lower()) is not None:
                humansubject = 1
            regex = re.compile("%s.*when"%word)
            if re.search(regex, findstring.lower()) is not None:
                whenafter =1
            regex = re.compile("when.*%s"%word)
            if re.search(regex, findstring.lower()) is not None:
                whenbefore =1 
            regex = re.compile("%s \w*?[^s]{1}_nn0"%word)
            if re.search(regex, findstring.lower()) is not None:
                uncountable_NP =1
                #print(sentence)
            baseword = re.search("[A-Za-z'-0-9]+",word).group()
            if re.search("(seem|appear|stay|remain|become|became|agree|includ|belong|consist)", baseword.lower()) is not None:
                existence_target = 1
            feature = "VTARGET_"+baseword.lower()
            if feature in features:
                features[feature] =1
            else:
                features[feature] = 1
        baseword = re.search("[A-Za-z'-0-9]+",word)
        if baseword is None:
            continue
        baseword = baseword.group()
        if baseword.lower() in set(stopwords.words('english')):
            stopwordscount += 1    
        if re.search("you", findstring.lower()) is not None:
            addressee = 1
    if len(re.findall("(feel|lik| hate_| hati|approv|agree|imagine|love|adore|suppos|think|remember|reali|thought|matter[a-z]._V)",findstring.lower())) > 0:
        mental = 1
    else:
        mental = 0
    politeness = len(re.findall("wonder|please|kind|madam|sir|thank",findstring))
    disapproval = len(re.findall("bitch|stupid|dumb|cunt|hate|wrong|bad",findstring))
    features["UNCOUNTABLENP"] = uncountable_NP
    features["MENTAL"] = mental
    features["EXISTENCEVERB"] = existence_target
    features["ADDRESSEE"] = addressee
    features["WHENAFTER"] = whenafter
    features["WHENBEFORE"] = whenbefore
    features["DISAPPROVAL"] = disapproval
    features["HUMANSUBJECT"] = humansubject
    features["POLITENESS"] = politeness
    features["SPOKENTHINGS"] = spokenstuff
    features["QUESTIONWORDS"] = questions
    features["STOPWORDS"] = stopwordscount
    return(features)
    
def extract_features(text):
    sentence = re.split(" ", text)
    sentencefeatures = {}
    sentencefeatures = get_other_counts(sentence)
    categorical = False
    if categorical:
        for feat in sentencefeatures:
            if sentencefeatures[feat] == None or sentencefeatures[feat] == 0:
                sentencefeatures[feat] = 0
            elif sentencefeatures[feat] == 1:
                sentencefeatures[feat] = 1
            elif sentencefeatures[feat] > 1 and sentencefeatures[feat] < 3:
                sentencefeatures[feat] = 2
            elif sentencefeatures[feat] >= 3:
                sentencefeatures[feat] = 3
    return(sentencefeatures)

def feat_in_sentence(informativelist):
    training_list = []
    trainingdata = load_data('train data2')
    for index, dataset in enumerate(trainingdata.data):
        informative_features_sentence={}
        all_features = extract_features(trainingdata.data[index])
        for informativefeature in informativelist:
            if informativefeature[0] in all_features:
                informative_features_sentence[informativefeature[0]] = all_features[informativefeature[0]]
        label = str(trainingdata.target[index])
        training_list.append((informative_features_sentence,label))
    return training_list
    
def main():
    training_list = []
    training_data = load_data('train data2')
    print(training_data.target_names)
    right = 0
    wrong = 0
    for index, dataset in enumerate(training_data.data):
        feats = extract_features(training_data.data[index])
        label = str(training_data.target[index])
        training_list.append((feats,label))
    #print(training_list)
    totalfeats = {}
    for pair in training_list:
        for feat in pair[0]:
            if feat in totalfeats:
                continue
            else:
                totalfeats[feat] = 'exists'
    print("total features:")
    n = len(totalfeats)
    print(n)
    classifier = nltk.classify.NaiveBayesClassifier.train(training_list)
    testing_data = load_data('test data2')
    for index, dataset in enumerate(testing_data.data):
        feats = extract_features(testing_data.data[index])
        pred = classifier.classify(feats)
        pred = int(pred)
        actual = int(testing_data.target[index])
        if actual == pred:
            right +=1
        else:
            wrong +=1
    score = right / (right+wrong)
    print(score)
    classifier.show_most_informative_features(200)
    informativelist=[]
    featfile=open("featfile.txt", "w")
    count=0
    for (fword, fvalue) in classifier.most_informative_features(10):
        count+=1
        feat = [fword, fvalue]
        featfile.write(fword)
        featfile.write("\n")
        informativelist.append(feat)
    featfile.close()
    print(count)
    training_list = feat_in_sentence(informativelist)
    right = 0
    wrong = 0
    totalfeats = {}
    for pair in training_list:
        for feat in pair[0]:
            if feat in totalfeats:
                continue
            else:
                totalfeats[feat] = 'exists'
    print("total features:")
    n = len(totalfeats)
    print(n)
    classifier = nltk.classify.NaiveBayesClassifier.train(training_list)
    for index, dataset in enumerate(testing_data.data):
        informative_features_test={}
        feats = extract_features(testing_data.data[index])
        for informativefeature in informativelist:
            if informativefeature[0] in feats:
                informative_features_test[informativefeature[0]] = feats[informativefeature[0]]
        pred = classifier.classify(informative_features_test)
        pred = int(pred)
        actual = int(testing_data.target[index])
        if actual == pred:
            right +=1
        else:
            wrong +=1
    score = right / (right+wrong)
    print(score)
    
if __name__ == '__main__':
    main()