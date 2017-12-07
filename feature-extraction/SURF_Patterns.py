
# coding: utf-8

# In[68]:

import spacy
from Text_Preprocessing import TextProcessing
import re
import itertools


# In[2]:

nlp = spacy.load('en')


# In[332]:

from enum import Enum
class MOBILE_APPS(Enum):
    ANGRY_BIRDS = 1
    DROP_BOX= 2
    EVERNOTE = 3
    TRIP_ADVISOR = 5
    PICS_ART = 6
    PINTEREST = 7
    WHATSAPP = 8
    YAHOO_MAIL=9


# In[780]:

class SURFPatterns:
    def __init__(self,data):
        self.data = data
    
    def PreprocessData(self):
        textProcessor = TextProcessing(app_description,nlp)
        textProcessor.SegmemtintoSentences()
        self.clean_pos_tag_sentences = textProcessor.GetCleanSentences()
    
    def ExtractFeatures_Analyzing_Sent_POSPatterns(self):
        pass
    
    def SentencePattern_Case1(self,sentence):
        raw_features=[]
        tokens= nlp(sentence)
        tag_text = ' '.join([token.lower_  + "/" + token.pos_ for token in tokens])
        #print(tag_text)
        regex_case1 = r"\w+\/(VERB|NOUN|PROPN)\s(and|or)\/CONJ\s\w+\/(VERB|NOUN|PROPN)\s\w+\/NOUN"
        match = re.search(regex_case1,tag_text)
        if match!=None:
            matched_text= tag_text[match.start():match.end()]
            words= [w.split("/")[0] for w in matched_text.split()]
            #print(words)
            raw_features.append(words[0] + " " + words[3])
            raw_features.append(words[2] + " " + words[3])
        
        return(raw_features)
    
    def SentencePattern_Case2(self,sentence):
        raw_features=[]
        tokens= nlp(sentence)
        tag_text = ' '.join([token.lower_  + "/" + token.pos_ for token in tokens])
        regex_case2 = r"\w+\/(VERB|NOUN|PROPN)\s\w+\/(NOUN|PROPN)(\s,\/PUNCT(\s)\w+\/\NOUN|PROPN)+(\s,\/PUNCT)?\sand\/CONJ\s\w+\/(NOUN|PROPN)"
        match=re.search(regex_case2,tag_text)
        if match!=None:
            matched_text= tag_text[match.start():match.end()]
            words = matched_text.split()

            first_word = words[0].split("/")[0]
            last_word = words[len(words)-1].split("/")[0]

            enumeration_words = [w.split('/')[0] for index,w in enumerate(matched_text.split()) if index not in[0,len(words)-1] and w.split("/")[1] not in ['PUNCT','CONJ']]
            raw_features.append(first_word + " " + last_word)

            raw_features += [first_word + " " + w2 for w2 in enumeration_words]

        return(raw_features)
    
    def SentencePattern_Case3(self,sentence):
        raw_features=[]
        tokens= nlp(sentence)
        tag_text = ' '.join([token.lower_  + "/" + token.pos_ for token in tokens])
        regex_case3 = r"\w+\/(VERB|NOUN|PROPN)\sand\/CONJ\s\w+\/(VERB|NOUN|PROPN)\s\w+\/(VERB|NOUN|PROPN)\sand\/CONJ\s\w+\/(VERB|NOUN|PROPN)"
        match = re.search(regex_case3,tag_text)
        if match!=None:
            matched_text= tag_text[match.start():match.end()]
            words = matched_text.split()
            words = [w.split("/")[0] for w in words]
            l1 = [words[0],words[2]]
            l2 = [words[3],words[5]]
            list_raw_features =list(itertools.product(l1,l2))
            raw_features= [feature_words[0] + " " + feature_words[1] for feature_words in list_raw_features]
            
        return(raw_features)
    
    def SentencePattern_Case4(self,sentence):
        raw_features=[]
        tokens= nlp(sentence)
        tag_text = ' '.join([token.lower_  + "/" + token.pos_ for token in tokens])
        regex_case4 = r"\w+\/(VERB|NOUN|PROPN)\sand\/CONJ\s\w+\/(VERB|NOUN|PROPN)\s\w+\/ADP((\s\w+\/(NOUN|PROPN))(\s\w+\/(ADP)))?\s\w+\/(NOUN|PROPN)"
        regex_case4 += "(\s,\/PUNCT)?\s(including\/\w+)((\s\w+\/(VERB|NOUN|PROPN))+\s,\/PUNCT)+\s\w+\/(NOUN|PROPN|VERB)\s(and\/CONJ)\s\w+\/(NOUN|PROPN|VERB)"

        match=re.search(regex_case4,tag_text)
    
        if match!=None:
            matched_text= tag_text[match.start():match.end()]
            words = matched_text.split()
            words = [w.split("/")[0] for w in words]

            #words attach with first conjunction
            feature_word1 = words[0]
            feature_word2 = words[2]

            feature_list1=[words[0],words[2]]

            #feature words attach with second conjection
            count=0
            feature_list2=[]
            fwords=[]
            for i in range(3,len(words)):
                if i<len(words)-1:
                    if words[i+1]=="," and count==0:
                        feature_list2.append(words[i])
                        count = count + 1
                    elif count==1:
                        if words[i]!="including" and words[i]!=',':
                            fwords.append(words[i])
                        if words[i] == ","  : 
                            if len(fwords)>0:
                                feature_list2.append(' '.join(fwords))
                            fwords=[]


            feature_list2.append(words[len(words)-1])
            feature_list2.append(words[len(words)-3])

            list_raw_features = list(itertools.product(feature_list1,feature_list2))

            raw_features= [feature_words[0] + " " + feature_words[1] for feature_words in list_raw_features]

        return(raw_features)
    
    def SentencePattern_Case5(self,sentence):
        raw_features=[]
        tokens= nlp(sentence)
        tag_text = ' '.join([token.lower_  + "/" + token.pos_ for token in tokens])
        #print(tag_text)
        regex_case5 = r"\w+\/(VERB|NOUN|PROPN)\s,\/PUNCT\s\w+\/(VERB|NOUN|PROPN)\sand\/CONJ\s\w+\/(VERB|NOUN|PROPN)\s\w+\/(VERB|NOUN|PROPN)\s(as\/ADP)\s"
        regex_case5 += "\w+\\/(ADJ|NOUN|PROPN|VERB)(\s\w+\\/(ADJ|NOUN|PROPN|VERB)\s,\/PUNCT)+\s\w+\/(NOUN|VERB|PROPN)\s(and\/CONJ)"
        regex_case5 += "\s\w+\/(VERB|NOUN|PROPN)\s\w+\/(VERB|NOUN|PROPN)"
        match=re.search(regex_case5,tag_text)
        if match!=None:
            match_text=tag_text[match.start():match.end()]
            words_with_tags = match_text.split()
            words = [w.split("/")[0] for w in words_with_tags]

            feature_list1=[words[0],words[2]]
            feature_list2=[words[4] + " "  + words[5],words[7] + " " + words[8]]
            feature_list3=[words[10],words[12],words[14] + " " + words[15]]
            list_raw_features=list(itertools.product(feature_list1,feature_list3))
            raw_features= [feature_words[0] + " " + feature_words[1] for feature_words in list_raw_features]
            raw_features = raw_features + feature_list2
            
        return(raw_features)

    
    def PrintCleanandPOSTagSentences(self):
        for sent in self.clean_pos_tag_sentences:
            sentence = ' '.join([word for word,tag in sent])
            #print(sentence)
            #case 1
            raw_features = self.SentencePattern_Case1(sentence)
            if len(raw_features)!=0:
                print("######CASE 1########")
                #print(sentence + "\n")
                print(raw_features)
            #case 2
            raw_features = self.SentencePattern_Case2(sentence)
            if len(raw_features)!=0:
                print("####CASE 2##########")
                #print(sentence + "\n")
                print(raw_features)
                
            #case 3
            raw_features = self.SentencePattern_Case3(sentence)
            if len(raw_features)!=0:
                print("####CASE 3##########")
                #print(sent)
                print(raw_features)
            
            #case 4
            raw_features = self.SentencePattern_Case4(sentence)
            if len(raw_features)!=0:
                print("####CASE 4##########")
                #print(sent)
                print(raw_features)
            
            #case 5
            raw_features = self.SentencePattern_Case5(sentence)
            if len(raw_features)!=0:
                print("####CASE 5##########")
                #print(sent)
                print(raw_features)


# In[782]:

if __name__ == '__main__':
    app = MOBILE_APPS.YAHOO_MAIL

    file_path = app.name.lower() + "_app_description.txt"
    with open(file_path) as f:
        app_desc = f.readlines()
    
    content = [x.strip() for x in app_desc] 
    app_description = ' '.join(content)
    
    obj_surf = SURF(app_description)
    obj_surf.PreprocessData()
    obj_surf.PrintCleanandPOSTagSentences()


# In[ ]:



