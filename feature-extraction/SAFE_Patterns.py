
# coding: utf-8

# In[61]:

import spacy
import re
import itertools
import pickle
import nltk
from Text_Preprocessing import TextProcessing
import Text_Preprocessing
import importlib
import requests
from langdetect import detect
import json


# In[62]:

#importlib.reload(Text_Preprocessing)


# In[63]:

from enum import Enum
class EXTRACTION_MODE(Enum):
    APP_DESCRIPTION = 1
    USER_REVIEWS= 2


# In[291]:

class SAFE_Patterns:
    def __init__(self,appId,clean_sents,extraction_mode):
        self.appId=appId
        #self.app_description = clean_sents
        self.clean_sentences = clean_sents
        self.extraction_mode = extraction_mode
    
    def ExtractFeatures_Analyzing_Sent_POSPatterns(self):
        raw_features_sent_patterns,remaining_sents=self.Extract_AppFeatures_with_SentencePatterns()
        raw_features_pos_patterns=self.Extract_AppFeatures_with_POSPatterns(remaining_sents)
        extracted_app_features = raw_features_sent_patterns + raw_features_pos_patterns
        
        #print(extracted_app_features)
        
        #extracted_app_features=[feature for feature in extracted_app_features if 'including' not in feature.split()]
        #extracted_app_features=[feature for feature in extracted_app_features if 'providing' not in feature.split()]
        #extracted_app_features=[feature for feature in extracted_app_features if 'winning' not in feature.split()]
        extracted_app_features=[feature for feature in extracted_app_features if 'iphone' not in feature.split()]
        extracted_app_features=[feature for feature in extracted_app_features if 'more' not in feature.split()]
        extracted_app_features=[feature for feature in extracted_app_features if 'many' not in feature.split()]
        
        #remvove features that has 1 char word in them
        #clean_app_features= [feature for feature in extracted_app_features if detect(feature)=='en']
           
        list_clean_feaures=[]
        # remove noise
        for feature in extracted_app_features:
            words = feature.split()
            duplicate_words = all(x == words[0] for x in words)
            
            if duplicate_words!=True:
                list_clean_feaures.append(feature)
        
        #print("# of extracted app features (after removing noise) are %d" % (len(list_clean_feaures)))
        
        #print(list_clean_feaures)
        
        self.SaveExtractedFeatures(list_clean_feaures)
        
        #print("Extracted features saved sucessfully in a file!!!")
    
    def SaveExtractedFeatures(self,extracted_features):
        file_path = self.appId.upper() + "_EXTRACTED_APP_FEATURES_"
        if self.extraction_mode.value == EXTRACTION_MODE.APP_DESCRIPTION.value:
            file_path = file_path + "DESC.pkl"
        elif self.extraction_mode.value == EXTRACTION_MODE.USER_REVIEWS.value:
            file_path = file_path + "REVIEWS.pkl"
        
        with open(file_path, 'wb') as fp:
            pickle.dump(extracted_features, fp)
    
    def Extract_Features_with_single_POSPattern(self,pattern_1,tag_text):
        match_list = re.finditer(pattern_1,tag_text)
        
        app_features=[]
            
        for match in match_list:
            app_feature = tag_text[match.start():match.end()]
            feature_words= [w.split("/")[0] for w in app_feature.split()]
            app_features.append(' '.join(feature_words))
        
        return(app_features)
    
    def Extract_AppFeatures_with_POSPatterns(self,clean_sents):
        app_features_pos_patterns=[]
        
        # list of all POS patterns
        pos_patterns=[r"[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)", # 1
                     r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(NOUN)", # 2
                     r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)", # 3
                     r"[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/CONJ\s+[a-zA-Z-]+\/(NOUN)", # 4
                     r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN|VERB)", # 5
                     r"[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN|ADJ|VERB)\s+[a-zA-Z-]+\/(NOUN)", # 6
                     r"[a-zA-Z-]+\/(VERB|NOUN)\s+[a-zA-Z-]+\/PRON\s+[a-zA-Z-]+\/(NOUN)", # 7
                     r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)", # 8
                     r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)", # 9
                     r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)", # 10
                     r"[a-zA-Z-]+\/(NOUN|ADJ)\s+[a-zA-Z-]+\/ADP\s+[a-zA-Z-]+\/(NOUN)", # 11
                     r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(DET)\s+[a-zA-Z-]+\/(NOUN)", # 12
                     r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/ADP\s+[a-zA-Z-]+\/(NOUN)", # 13
                     r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)", # 14
                     r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/CONJ\s+[a-zA-Z-]+\/ADJ", # 15
                     r"[a-zA-Z-]+\/(VERB|NOUN)\s+[a-zA-Z-]+\/(PRON|DET)\s+[a-zA-Z-]+\/(ADJ|VERB|NOUN)\s+[a-zA-Z-]+\/(NOUN)", # 17
                     r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(ADP)\s+[a-zA-Z-]+\/(ADJ|NOUN)\s+[a-zA-Z-]+\/(NOUN)", # rule # 16
                     r"[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/CONJ\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)" # rule # 18
                     ]
    #Noun Conjunction Noun Noun

        for sent in clean_sents:
            sent_tokens= nltk.word_tokenize(sent)
            tag_tokens = nltk.pos_tag(sent_tokens,tagset='universal')
            tag_text = ' '.join([word.lower() + "/" + tag for word,tag in tag_tokens])
            #print(tag_text)
            # extract app features through by iterating through list of all POS_patterns
            for pattern in pos_patterns:
                # store extracted features in list of app features
               
                raw_features = self.Extract_Features_with_single_POSPattern(pattern,tag_text)
                if len(raw_features)!=0:
                    #print("Pattern->%s" % (pattern))
                    #print(raw_features)
                    app_features_pos_patterns.extend(raw_features)
                
                    #print("")
            
        return(app_features_pos_patterns)
    
    def SentencePattern_Case1(self,tag_text):
        raw_features=[]
        #print(tag_text)
        #print("")
        #tag_text = ' '.join([token.lower_  + "/" + token.pos_ for token in tokens])
        #print(tag_text)
        regex_case1 = r"[a-zA-Z-]+\/(VERB|NOUN)(\s+,\/.)?\s+(and)\/CONJ\s+[a-zA-Z-]+\/(VERB|ADJ|NOUN)(\s+[a-zA-Z-]+\/(NOUN|VERB))+"
        match = re.search(regex_case1,tag_text)
        if match!=None:
            matched_text= tag_text[match.start():match.end()]
            words= [w.split("/")[0] for w in matched_text.split() if w.split("/")[1] not in ['.','CONJ']]
            raw_features.append(words[0] + " " + ' '.join(words[2:]))
            raw_features.append(words[1] + " " + ' '.join(words[2:]))

        #print(raw_features)
        #print("**************")
    
        return(raw_features)
    
    def SentencePattern_Case2(self,tag_text):
        raw_features=[]
        regex_case2 = r"[a-zA-Z-]+\/(VERB|NOUN|ADJ)(\s+[a-zA-Z-]+\/PRON)?(\s+[a-zA-Z-]+\/(VERB|NOUN|ADJ)\s+,\/.)+(\s+[a-zA-Z-]+\/(VERB|NOUN|ADJ))?\s+and\/CONJ\s+[a-zA-Z-]+\/(VERB|NOUN|ADJ)"
        match=re.search(regex_case2,tag_text)
        if match!=None:
            matched_text= tag_text[match.start():match.end()]    
            words = matched_text.split()

            first_word = words[0].split("/")[0]
            last_word = words[len(words)-1].split("/")[0]

            enumeration_words = [w.split('/')[0] for index,w in enumerate(matched_text.split()) if index not in[0,len(words)-1] and w.split("/")[1] not in ['.','CONJ','PRON']]
            raw_features.append(first_word + " " + last_word)

            raw_features += [first_word + " " + w2 for w2 in enumeration_words]

        return(raw_features)
    
    def SentencePattern_Case3(self,tag_text):
        raw_features=[]
        #tag_text = ' '.join([token.lower_  + "/" + token.pos_ for token in tokens])
        regex_case3 = r"[a-zA-Z-]+\/(VERB|NOUN)\s+and\/CONJ\s+[a-zA-Z-]+\/(NOUN|VERB)\s+[a-zA-Z-]+\/(NOUN|VERB)\s+and\/CONJ\s+[a-zA-Z-]+\/(NOUN|VERB)"
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
    
    def SentencePattern_Case4(self,tag_text):
        raw_features=[]
        #tag_text = ' '.join([token.lower_  + "/" + token.pos_ for token in tokens])
        regex_case4 = r"[a-zA-Z-]+\/(VERB|NOUN|ADJ)\s+and\/CONJ\s+[a-zA-Z-]+\/(VERB|NOUN|ADJ)\s+[a-zA-Z-]+\/ADP((\s+[a-zA-Z-]+\/(NOUN|VERB))(\s+[a-zA-Z-]+\/(ADP)))?\s+[a-zA-Z-]+\/(NOUN|VERB)"
        regex_case4 += "(\s+,\/.)?\s+(including\/[a-zA-Z-]+)((\s+[a-zA-Z-]+\/(VERB|NOUN))+\s+,\/.)+\s+[a-zA-Z-]+\/(NOUN|VERB)\s+(and\/CONJ)\s+[a-zA-Z-]+\/(NOUN|VERB)"

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
    
    def SentencePattern_Case5(self,tag_text):
        raw_features=[]
        #print(tag_text)
        #tag_text = ' '.join([token.lower_  + "/" + token.pos_ for token in tokens])
        regex_case5 = r"[a-zA-Z-]+\/(VERB|NOUN|ADP)\s+,\/.\s+[a-zA-Z-]+\/(VERB|NOUN)\s+and\/CONJ\s+[a-zA-Z]+\/(VERB|NOUN|ADJ)\s+[a-zA-Z-]+\/(NOUN|VERB|ADJ)\s+(as\/ADP)\s+"
        regex_case5 += "[a-zA-Z-]+\/(ADJ|NOUN|VERB)(\s+[a-zA-Z-]+\/(NOUN|VERB)\s+,\/.)+\s+[a-zA-Z-]+\/(NOUN|VERB)\s+(and\/CONJ)"
        regex_case5 += "\s+[a-zA-Z-]+\/(NOUN|VERB)\s+[a-zA-Z-]+\/(NOUN|VERB)"
        #regex_case5 += "\s+\w+\/(NOUN|VERB)"  #\s+\w+\/(NOUN|VERB)"
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
    
    def Extract_AppFeatures_with_SentencePatterns(self):
        raw_app_features_sent_patterns=[]
        clean_sents_wo_sent_patterns=[]
        
        for sent in self.clean_sentences:
            sent_tokens= nltk.word_tokenize(sent)
            tag_tokens = nltk.pos_tag(sent_tokens,tagset='universal')
            tag_text = ' '.join([word.lower()  + "/" + tag for word,tag in tag_tokens])
            #print(tag_text)
            sent_pattern_found=False
            #case 1
            raw_features_case1 = self.SentencePattern_Case1(tag_text)

            if len(raw_features_case1)!=0:
               
                raw_app_features_sent_patterns.extend(raw_features_case1)
                #print(raw_app_features_sent_patterns)
                #print("CASE1***************************")
                #print(sent)
                #print("CASE1***************************")
                sent_pattern_found=True
            #case 2
            raw_features_case2 = self.SentencePattern_Case2(tag_text)
            
            if len(raw_features_case2)!=0:
                #print("CASE2***************************")
                #print(sent)
                raw_app_features_sent_patterns.extend(raw_features_case2)
                #print("CASE2***************************")
                sent_pattern_found=True
            #case 3
            raw_features_case3 = self.SentencePattern_Case3(tag_text)
            if len(raw_features_case3)!=0:
                raw_app_features_sent_patterns.extend(raw_features_case3)
                sent_pattern_found=True
                #print("CASE3***************************")
            #case 4
            raw_features_case4 = self.SentencePattern_Case4(tag_text)
            if len(raw_features_case4)!=0:                
                raw_app_features_sent_patterns.extend(raw_features_case4)
                print(raw_features_case4)
                #print("***************************")
                sent_pattern_found=True
            #case 5
            raw_features_case5 = self.SentencePattern_Case5(tag_text)
            if len(raw_features_case5)!=0:
                raw_app_features_sent_patterns.extend(raw_features_case5)
                #print("CASE5***************************")
                sent_pattern_found=True
#                 print(raw_features_case5)
#                 print("##########################")
            
            if sent_pattern_found==False:
                clean_sents_wo_sent_patterns.append(sent)
        
        
        return(raw_app_features_sent_patterns,clean_sents_wo_sent_patterns)


# In[292]:

# if __name__ == '__main__':
#     appName = "DROP_BOX"
#     file_path = appName.lower() + "_app_description.txt"
#     with open(file_path) as f:
#         app_desc = f.readlines()
    
#     content = [x.strip() for x in app_desc] 
#     app_description = ' '.join(content)

#     appID = "718043190"
#     api_url='http://localhost:8081/app/description?id=' + appID
#     myResponse = requests.get(api_url)
#     if(myResponse.ok):
#          app_data = json.loads((myResponse.content.decode('utf-8')))

#     app_description = app_data['description'].strip()
    
#     obj_surf = SAFE_Patterns(appID,app_description,EXTRACTION_MODE.APP_DESCRIPTION)
#     obj_surf.PreprocessData()
#     obj_surf.ExtractFeatures_Analyzing_Sent_POSPatterns()


# In[ ]:



