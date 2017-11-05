
# coding: utf-8

# In[1]:

import spacy
import SAFE_Patterns
from Text_Preprocessing import TextProcessing
from Feature_Matching import Merge_Features
import Feature_Matching
import Text_Preprocessing
import importlib
import json
from urllib.request import urlopen
import re
import requests
import time
import nltk
import sys, json


# In[2]:

importlib.reload(SAFE_Patterns)
importlib.reload(Text_Preprocessing)
importlib.reload(Feature_Matching)


# In[3]:

nlp = spacy.load('en')

# In[4]:

from enum import Enum
class EXTRACTION_MODE(Enum):
    APP_DESCRIPTION = 1
    USER_REVIEWS= 2

class MERGE_MODE(Enum):
    DESCRIPTION=1
    USER_REVIEWS=2
    DESCRIPTION_USER_REVIEWS=3

class EVALUATION_TYPE(Enum):
    EXACT=1
    PARTIAL=2


# In[5]:

class SAFE:
    def __init__(self,appID,extraction_mode,data,nlp):
        self.appID=str(appID)
        self.extraction_mode = extraction_mode
        self.nlp = nlp
        self.data = data
        self.ExtractData()
        
    def ExtractData(self):
        if self.extraction_mode == EXTRACTION_MODE.APP_DESCRIPTION:
            self.app_description = self.data
            
        elif self.extraction_mode ==  EXTRACTION_MODE.USER_REVIEWS:
            self.reviews_text=[]
            user_reviews = data
        
            for user_review in user_reviews:
                relevant_review_info = {'id' : user_review['id'],'text': user_review['text']}
                self.reviews_text.append(relevant_review_info)
    
    def PreprocessData(self):
        #print('spacy segmemtation')
        self.clean_sentences=[]
        if self.extraction_mode == EXTRACTION_MODE.APP_DESCRIPTION:
            textProcessor = TextProcessing(self.appID,self.app_description)
            textProcessor.SegmemtintoSentences(sents_already_segmented=True)
            self.clean_sentences = textProcessor.GetCleanSentences()
            #print(self.clean_sentences)
        elif self.extraction_mode == EXTRACTION_MODE.USER_REVIEWS:
            #count=0
            start_time = time.time()
            #self.all_clean_sentences=[]
            for review_text in self.reviews_text:
                textProcessor = TextProcessing(self.appID,review_text['text'])
                textProcessor.SegmemtintoSentences(sents_already_segmented=False)
                clean_sents = textProcessor.GetCleanSentences()
                self.clean_sentences.extend(clean_sents)
            
                
            #print("--- %s seconds ---" % (time.time() - start_time))
            #print()
    
    def ExtractAppFeatures(self):
        SAFE_Patterns_Obj=SAFE_Patterns.SAFE_Patterns(self.appID, self.clean_sentences, self.extraction_mode)
        SAFE_Patterns_Obj.ExtractFeatures_Analyzing_Sent_POSPatterns()
    
    def Group_Features(self,similarity_th=.70):
        obj_merge_features = Merge_Features(self.appID,self.extraction_mode ,self.nlp)
        return(obj_merge_features.Merge(similarity_th))
    
    def Extract_App_Features(self):
        self.PreprocessData()
        self.ExtractAppFeatures()
        json_output = self.Group_Features()
        return(json_output)

#Read data from stdin
def read_in():
    lines = sys.stdin.readlines()
    return json.loads(lines[0])

# In[6]:

if __name__ == '__main__':
    lines = read_in()
    
    mode = lines[0]['mode']
    appID = lines[0]['appID']
    data = lines[0]['data']
    if EXTRACTION_MODE(mode) == EXTRACTION_MODE.APP_DESCRIPTION: 
        obj_surf = SAFE(appID, EXTRACTION_MODE.APP_DESCRIPTION, data, nlp)
    elif EXTRACTION_MODE(mode) == EXTRACTION_MODE.USER_REVIEWS:
        obj_surf = SAFE(appID, EXTRACTION_MODE.USER_REVIEWS, data, nlp)
    
    json_output = obj_surf.Extract_App_Features()
    predicted_features_json = json_output['app_features']
    print(json.dumps(predicted_features_json))

#     cluster_predicted_features=[]

#     print("++++++++++++++++++++++++++++++++++++++++++++++++++")

#     print('Numer of clusters are %d' % len(predicted_features_json))

#     for cluster_features in predicted_features_json:
#         app_features_group = cluster_features['cluster_features']
#         #print(app_features_group)
#         app_features_cluster=[]
#         for app_feature in app_features_group:
#         #predicted_features.append(app_feature['feature'])
#             app_features_cluster.append(app_feature['feature'])

#         cluster_predicted_features.append(app_features_cluster)

#     print(cluster_predicted_features)


# In[ ]:



