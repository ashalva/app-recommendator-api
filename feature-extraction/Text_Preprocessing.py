
# coding: utf-8

# In[8]:

import re
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction import stop_words
import spacy
import json
from urllib.request import urlopen
from unidecode import unidecode
import requests
import html


# In[9]:

#nlp = spacy.load('en')


# In[ ]:

class TextProcessing:
    def __init__(self,appName,data):
        self.appName = appName
        self.data = data

    # segment description into sentences
    def SegmemtintoSentences(self,sents_already_segmented=False):
        self.sents=[]
        #print(self.data)
        if sents_already_segmented == True:     
            list_lines = [line for line in self.data if line.strip()!='']
            for line in list_lines:
                u_line = unidecode(line)
                pattern=r'".*"(\s+-.*)?'
                u_line = re.sub(pattern, '', u_line)
                pattern1 = r'\'s'
                u_line= re.sub(pattern1,"",u_line)
                #sentences = nltk.word_tokenize(u_line)
                #print(u_line)
                self.sents.append(u_line)
        elif sents_already_segmented==False:
            self.sents = nltk.sent_tokenize(self.data)
            self.sents = [sent for sent in self.sents if sent.strip()!='']
        
        return(self.sents)
        
    # clean sentences
    def  GetCleanSentences(self):
        sentences=[]
        clean_sentences=[]
        sent_id=0
        # remove explanations text with-in brackets
        for sent in self.sents:
            sent = html.unescape(sent.strip())
            sent = sent.lstrip('-')
            regex = r"(\(|\[).*?(\)|\])"
            urls = re.findall('(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?',sent)
            #urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', sent)
            emails = re.findall("[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*", sent) 
            url_regex = r'(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?'
            email_regex = r"[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*"
            #quotations = re.findall('"([^"]*)"', sent)
            match_list = re.finditer(regex,sent)
            match_list_email = re.finditer(email_regex,sent)
            match_list_url = re.finditer(url_regex,sent)
            new_sent=sent
            
            #print(match)
            # filter sentences containg urls, emails, and quotations
            if len(urls)==0 and len(emails)==0 :
                if match_list:
                    for match in match_list:
                        txt_to_be_removed = sent[match.start():match.end()]
                        new_sent=new_sent.replace(txt_to_be_removed,"")
                    
                    clean_sentences.append(new_sent)
                else:
                    clean_sentences.append(sent)
            else:
                if match_list_url:
                    for match in match_list_url:
                        txt_to_be_removed = sent[match.start()-1:match.end()]
                        new_sent=new_sent.replace(txt_to_be_removed,"")
                    
                    clean_sentences.append(new_sent)
                
                elif match_list_email:
                    for match in match_list_email:
                        txt_to_be_removed = sent[match.start()-1:match.end()]
                        new_sent=new_sent.replace(txt_to_be_removed,"")
                    
                    clean_sentences.append(new_sent)
                
        
        
        # replace bullet points and symbols # ,-, and * (use for delineate)        
        pattern = r'\*|\u2022|#'
        
        app_names=[]
        
        app_words = self.appName.split(' ')
        
        if len(app_words)>1:
            app_names.append(' '.join(app_words))
            app_names.append(''.join(app_words))
        else:
            app_names.append(self.appName)
        
        #list_stop_words = list(stop_words.ENGLISH_STOP_WORDS) + list(stopwords.words('english')) + list(['anything','beautiful','efficient','enjoyable','way','quick','greeting','features','elegant','instant','fun']) 
                
        #NON_STOP_WORDS=['see','out','thick','call','top','put','bill','under','get','next','all','cry','fill','found','interest','detail','empty','part','go','made','show','move','fire','up','find','keep'\
                                        #'toward','again','full','name','describe','back','amount','give','front','off','take','system','up','on','over','off','on','in','through','from','an','your','of','or','use','and']
        
        #final_stop_words = set(list_stop_words) - set(NON_STOP_WORDS)
        custom_stop_words = ['anything','beautiful','efficient','enjoyable','way','quick','greeting','features','elegant','instant','fun','price','dropbox','iphone','total','is','in-app','apps','quickly','easily','lovely','others','other','own','the','interesting','addiction','following','featured','best','phone','sense','fantastical','fantastic','better',
                            'award-winning','include','including','winning','improvements','improvement','significant','app','mac','pc','ipad','approach','application','applications','lets','several','safari','pro','google','matter','embarrassing','faster','mistakes','gmail','official','out','results','those','them','have','internet','anymore','are','provide','partial','useful','twitter','facebook','need','lose','it','yahoo','be','swiss','say','makes','make','local','button','will','vary','was','were','cloudapp','everything','straightforward','seamless','mundane','convenience','based','whatever','d','trials','trial','stuff','same','responsibility','love','great','would','good','only','might','strange','thing','nice','has','had','have','various','poor','stupid','could','did','does','do','doesn\'t','didn\'t','don\'t','didnt','dont','doesnt','can','cant','couldn\'t','couldnt','lot','alot','m','\'ve','\'ll','etc','am','lots','did','does','most','frightening','frighten','crash','crashes','bad','awesome','wonderful','simplistic','im','sometimes','should','shouldn\'t','guys','me','enjoy','m','glitch','cute','having','em','i','this','bcoz','n','y','very','but','bt','cud','b','its','itz','it','good','goood','no','none','fine','plz','anyone','tell','problem','bug','issue','crash','please','fix','nd','awsme','juz','just','bugs','ur','dis','v','cnt','cool','c','bcz','fulfills','error','dat','canot','nthng','jst',"\'s","anyways","anywayz","anyway","thiz","different","things","much","wid","about","bore","being","excellent","p","plz","whole","allow","allowed","bein","been","confusion","fixes","wish","hope","needs","brought","ever","worrying","worry","\'s","t","s" ,"who","whom","whose","which","ll","someone",'certain','hate','company','everyone','first','few','issues','terrible','corrupted']
        
        
        custom_stop_words = custom_stop_words + app_names
        
        for index,sent in enumerate(clean_sentences):
            clean_sent= re.sub(pattern,"",sent)
            # removing sub-ordinate clauses from a sentence
            sent_wo_clause = self.Remove_SubOrdinateClause(clean_sent)
        
            clean_sentences[index] = sent_wo_clause
            
            tokens = nltk.word_tokenize(clean_sentences[index])
                
            #sent_tokens = [w.lower() for w in tokens if w.lower()]
            sent_tokens = [w for w in tokens if w.lower() not in custom_stop_words]
            #print(' '.join(sent_tokens))
            #print("+++++++++++++++++++++++++++++++++++++++++++++++")
            sentences.append(' '.join(sent_tokens))
        
        
                
        return sentences
    
    def Remove_SubOrdinateClause(self,sentence):
        sub_ordinate_words= ['when','after','although','because','before','if','rather','since',                            'though','unless','until','whenever','where','whereas','wherever','whether','while','why','which'
                            ]
        
        sub_ordinate_clause = False
        words=[]
        tokens = nltk.word_tokenize(sentence)
        for token in tokens:
            if token.lower() in sub_ordinate_words: #and clause_has_obj==False and clause_has_sub==False:
                sub_ordinate_clause = True
    
            if sub_ordinate_clause == False:
                    words.append(token)
                    #print(token.orth_,token.dep_)
            elif sub_ordinate_clause == True:
                break
            
        return(' '.join(words).strip())


# In[ ]:

#if __name__ == '__main__':
#     appName = "test_app"
#     file_path = appName.lower() + ".txt"
#     with open(file_path) as f:
#         app_desc = f.readlines()
    
#     #print(app_desc)
#     content = [x.strip() for x in app_desc] 
#     app_description = ' '.join(content)

#     appID = "718043190"
#     api_url='http://localhost:8081/app/description?id=' + appID
#     myResponse = requests.get(api_url)
#     if(myResponse.ok):
#          app_data = json.loads((myResponse.content.decode('utf-8')))

#     app_description = app_data['description'].strip()

    #app_description = unidecode(app_description)
    
#     textProcessor = TextProcessing(appID,app_description)
#     textProcessor.SegmemtintoSentences(sents_already_segmented=True)
#     clean_sentence=textProcessor.GetCleanSentences()
    
    #for sent in clean_sentence:
        #print(sent)
        #print("")
    #textProcessor.PrintCleanandPOSTagSentences()


# In[ ]:



