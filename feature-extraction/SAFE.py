
# coding: utf-8

# In[66]:

import spacy
import SAFE_Patterns
from Text_Preprocessing import TextProcessing
from Feature_Matching import Merge_Features
import SAFE_Evaluation
#from SAFE_Evaluation import Evaluate
import ReadXMLData
from ReadXMLData import XML_REVIEW_DATASET
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

# In[67]:

from enum import Enum

class ANNOTATORS:
    CODER1 = 1 
    CODER2 = 2 

class MOBILE_APPS(Enum):
    WHATSAPP = 1

class DATASETS(Enum):
    GUZMAN=1

class EXTRACTION_MODE(Enum):
    APP_DESCRIPTION = 1
    USER_REVIEWS= 2


# In[68]:

importlib.reload(SAFE_Evaluation)
importlib.reload(SAFE_Patterns)
importlib.reload(Text_Preprocessing)
importlib.reload(Feature_Matching)


# In[11]:

nlp = spacy.load('en')


# In[69]:

class SAFE:
    def __init__(self,appid,appName,description,reviews,nlp):
        self.appID = appid
        self.appName = appName
        self.app_description = description
        self.user_reviews = reviews
        self.nlp = nlp
    
    def ExtractFeaturesFromAppDescription(self):
        
        textProcessor = TextProcessing(self.appName,self.app_description)
        unclean_sents = textProcessor.SegmemtintoSentences(sents_already_segmented=False)
        clean_sentences = textProcessor.GetCleanSentences()
        SAFE_Patterns_Obj = SAFE_Patterns.SAFE_Patterns(self.appName,None,clean_sentences,unclean_sents)
        sents_with_features= SAFE_Patterns_Obj.ExtractFeatures_Analyzing_Sent_POSPatterns()
        
        app_features_desc = []
        
        for sent_id in sents_with_features.keys():
            extracted_features = sents_with_features[sent_id]['extracted_features']
            app_features_desc.extend(extracted_features)

        self.extracted_app_features_dec =  app_features_desc
    
    
    def ExtractFeaturesFromUserReviews(self):
        dict_user_reviews={}
        
        for user_review in self.user_reviews:
            dict_user_reviews[int(user_review['id'])] = {'review_text': user_review['text'],'predicted_features':[]}
          
        self.data = dict_user_reviews
        
    def PreprocessData(self):
        
        # extract features from app description
        self.ExtractFeaturesFromAppDescription()
        
        #exract features from user reviews
        self.ExtractFeaturesFromUserReviews()
        
        #if self.extraction_mode.value == EXTRACTION_MODE.USER_REVIEWS.value:
            #reviews sents with extracted app features
        self.reviews_with_sents_n_features={}
            
        for review_id in self.data.keys():
            review_text  = self.data[review_id]['review_text']
                #self.clean_sentences=[]
            textProcessor = TextProcessing(self.appName,review_text)
            unclean_sents = textProcessor.SegmemtintoSentences(sents_already_segmented=False)
                
            review_clean_sentences = textProcessor.GetCleanSentences()
            SAFE_Patterns_Obj=SAFE_Patterns.SAFE_Patterns(self.appName,review_id,review_clean_sentences,unclean_sents)
            sents_with_features = SAFE_Patterns_Obj.ExtractFeatures_Analyzing_Sent_POSPatterns()
            review_wise_features=[]
            for sent_id in sents_with_features.keys():
                del sents_with_features[sent_id]['clean_sent']
                review_wise_features.extend(sents_with_features[sent_id]['extracted_features'])
                    
            self.reviews_with_sents_n_features[review_id] = sents_with_features
            self.data[review_id]['predicted_features'] = review_wise_features
                
        self.extracted_app_features_reviews = self.GetListOfExtractedAppFeatures()
    
    def GetReviewsWithExtractedFeatures(self):
        return self.data

    def GetReview_Sents_WithExtractedFeatures(self):
        return self.reviews_with_sents_n_features
    
    def GetListOfExtractedAppFeatures(self):
        list_extracted_app_features=[]
        for review_id in self.reviews_with_sents_n_features.keys():
            sents_with_app_features = self.reviews_with_sents_n_features[review_id]
            for sent_id in sents_with_app_features.keys():
                app_features = sents_with_app_features[sent_id]['extracted_features']
                list_extracted_app_features.extend(app_features)
        
        return(list_extracted_app_features)
        
    def ExtractAppFeatures(self):
        SAFE_Patterns_Obj=SAFE_Patterns.SAFE_Patterns(self.appName, self.clean_sentences,self.data)
        SAFE_Patterns_Obj.ExtractFeatures_Analyzing_Sent_POSPatterns()
    
    def Group_Features(self,similarity_th=.70):
        obj_merge_features = Merge_Features(self.appName,list(self.clean_review_features),self.nlp)
        return(obj_merge_features.Merge(similarity_th))
    
    def Extract_Raw_App_Features_From_Reviews_n_Desc(self):
        self.PreprocessData()
    
    def CleanExtractedFeaturesReview_By_Desc(self,th_similarity_with_desc_features,th_similarity_feature_cluster):
        obj_merge_features = Merge_Features(self.appName,self.extracted_app_features_reviews,self.nlp)
        self.clean_review_features = obj_merge_features.FilterReviewAppFeaturesByAppFeaturesExtractedFromDesciption(self.extracted_app_features_reviews,self.extracted_app_features_dec,th_similarity_with_desc_features)
        json_output = self.Group_Features(th_similarity_feature_cluster)
        return(json_output)


#Read data from stdin
def read_in():
    lines = sys.stdin.readlines()
    return json.loads(lines[0])

# In[71]:

if __name__ == '__main__':
    lines = read_in()

    app_id = lines[0]['appID']
    app_reviews = lines[0]['reviews']
    app_description = lines[0]['description']
    appName = lines[0]['name']


    #objXML_DS = XML_REVIEW_DATASET(DATASETS.GUZMAN,MOBILE_APPS.WHATSAPP,ANNOTATORS.CODER1)
    #reviews_data = objXML_DS.ReadReviewWithAspectTerms()
    #print(reviews_data)
    #reviews_list = [review_with_true_features[review_id]['review_text'] for review_id in review_with_true_features.keys()]
    
#     app_name = 'PyCharm'
#     file_path = app_name + '.txt'

#     with open(file_path,encoding="latin-1") as f:
#         content = f.readlines()
    
#     content = [x.strip() for x in content] 
    

    SIMILARITY_THRESHOLD_WITH_APP_DESRIPTION_FEATURES = (lines[0]['appDescThreshold']/100)
    SIMILARITY_THRESHOLD_FEATURE_CLUSTERING = (lines[0]['featureThreshold']/100)
    
    obj_surf = SAFE(app_id,appName,app_description,app_reviews,nlp)
    obj_surf.Extract_Raw_App_Features_From_Reviews_n_Desc()
    json_output = obj_surf.CleanExtractedFeaturesReview_By_Desc(SIMILARITY_THRESHOLD_WITH_APP_DESRIPTION_FEATURES,SIMILARITY_THRESHOLD_FEATURE_CLUSTERING)
    
    review_sents_with_features = obj_surf.GetReview_Sents_WithExtractedFeatures()
    
    print(json.dumps({'features': json_output['app_features'],
                      'sentences': review_sents_with_features,
                      'appName': appName}))
   
    #     predicted_features_json =json_output['app_features']
#     #print(predicted_features_json)

#     cluster_predicted_features=[]

#     print("++++++++++++++++++++++++++++++++++++++++++++++++++")

#     print('Number of clusters are %d' % len(predicted_features_json))

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




# In[ ]:



