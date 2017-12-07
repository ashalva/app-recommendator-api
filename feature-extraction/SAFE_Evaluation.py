
# coding: utf-8

# In[1]:

import nltk
from nltk.stem.snowball import SnowballStemmer


# In[ ]:

stemmer = SnowballStemmer("english")


# In[4]:

from enum import Enum

class EVALUATION_TYPE(Enum):
    EXACT=1
    PARTIAL=2


# In[33]:

class Evaluate:
    def __init__(self,true_features,cluster_predicted_features,evaluation_type):
        self.true_features=true_features
        self.predicted_features_cluster = cluster_predicted_features
        self.evaluation_type = evaluation_type
    
    def PerformEvaluation(self):
        if self.evaluation_type.value == EVALUATION_TYPE.EXACT.value:
            self.ExactEvaluation()
    
    def ExactEvaluation(self):
        
        tp = 0
        fp = 0
        fn = 0
        tp_features_list=[]
        fp_features_list=[]
        fn_features_list=[]
        count=0
        for feature_cluster in self.predicted_features_cluster:
            found = False
            matched_true_feature=""
            tp_count=0
            tp_feature_list=[]
            for p_feature in feature_cluster:
                p_feature_words =  nltk.word_tokenize(p_feature)
                p_feature_words_tag = nltk.pos_tag(p_feature_words)
                p_feature_clean = ' '.join([stemmer.stem(w.lower()) for w,tag in p_feature_words_tag if tag!='PRP$' and tag!='IN'])
        

                for t_feature in set(self.true_features):
                    t_feature_words =  nltk.word_tokenize(t_feature)
                    t_feature_words_tag = nltk.pos_tag(t_feature_words)
                    t_feature_clean = ' '.join([stemmer.stem(w.lower()) for w,tag in t_feature_words_tag if tag!='PRP$' and tag!='IN'])
                    #print("compare \'%s\' with \'%s\'" % (p_feature_clean,t_feature_clean))
                    if p_feature_clean==t_feature_clean and t_feature_clean not in tp_features_list:
                        found = True
                        tp_count = tp_count + 1
                        tp_feature_list.append(t_feature_clean)
                        #print("**Result is TRUE**")
                        #matched_true_feature = t_feature_clean
                        break
                
                    #print('########################################'
            
            count = count + 1
            
            if found == True:
                tp =  tp + tp_count
                tp_features_list.extend(tp_feature_list)
                #print("\'%s\' exactly matched with \'%s\'\n" % (matched_true_feature,matched_true_feature))    
            
            if found==False:
                for p_feature in feature_cluster:
                    fp_features_list.append(p_feature)
                fp =  fp + 1
        
        
        for t_feature in set(self.true_features):
            t_feature_words =  nltk.word_tokenize(t_feature)
            t_feature_words_tag = nltk.pos_tag(t_feature_words)
            t_feature_clean = ' '.join([stemmer.stem(w.lower()) for w,tag in t_feature_words_tag if tag!='PRP$' and tag!='IN'])
                
            found = False
            for feature_cluster in self.predicted_features_cluster:
                #fn_count=0
                for p_feature in feature_cluster:
                    p_feature_words =  nltk.word_tokenize(p_feature)
                    p_feature_words_tag = nltk.pos_tag(p_feature_words)
                    p_feature_clean = ' '.join([stemmer.stem(w.lower()) for w,tag in p_feature_words_tag if tag!='PRP$' and tag!='IN'])
                
                    if p_feature_clean == t_feature_clean:
                        found = True
                        #fn_count =  fn_coun + 1
                        break
            
            if found == False:
                fn_features_list.append(t_feature_clean)
                fn = fn  + 1
                
        print('TP:%d , FP:%d, FN: %d\n' % (tp,fp,fn))
        precision = tp/(tp + fp)
        recall = tp/(tp + fn)
        try:
            fscore = 2*((precision*recall)/(precision+recall))
        except ZeroDivisionError:
            fscore=0.0
        
        print("**********RESULTS******************")
        print("Precisioin : %.3f, Recall : %.3f, Fscore: %.3f" % (precision,recall,fscore))
        
        print("###########################DETAILS#############################")
        
        print('List of true positive features ->')
        print(tp_features_list)
        
        print('List of false positive features ->')
        print(set(fp_features_list))
        
        print('List of false negative features ->')
        print(fn_features_list)


# In[35]:

# if __name__ == '__main__':
#     true_features=['natural language parsing', 'reminders', 'week view', 'speak the details of your event', 'see your events', 'see your dated reminders', 'add reminders', 'set dates', 'set times', 'set geofences', 'create reminders with your voice', 'create alerts', 'show event details', "show event's location", 'repeating event options', 'background app updating', 'extended keyboard', 'TextExpander support', 'add new events', 'list events', 'find your events', 'edit reminder', 'push notifications', 'integrates iOS reminders']
#     predicted_features=['facebook events', 'allows reminders', 'new events', 'events fun', 'specific events', 'allows events', 'accessibility support', 'textexpander support', 'including peek', 'week view', 'use dictation', 'calendar services', 'iphone calendar', 'google calendar', 'john gruber', 'reminders fun', 'event show', 'managing schedule', 'stock calendar', 'beautiful week', 'reminder show', 'pure replacement', 'favorite iphone', 'including icloud', 'events reminders', 'allows alerts', 'symbols dates', 'numbers dates', 'details dictation', 'natural language', 'enjoyable way', 'efficient and enjoyable', '3d touch', 'dated reminders', 'apps works', 'handle rest', 'replacement iphone', 'use search', 'event duplicate', 'jim dalrymple', 'winning calendar', 'speak details', 'great ios', 'language parsing', 'ios reminders', 'new features']
    
#     objEvaluation=Evaluation(true_features,predicted_features,EVALUATION_TYPE.EXACT)
#     objEvaluation.PerformEvaluation()


# In[ ]:




# In[ ]:



