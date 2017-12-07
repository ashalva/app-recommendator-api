
# coding: utf-8

# In[16]:

from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.dom import minidom
import html
import re


# In[17]:

from enum import Enum

class ANNOTATORS:
    CODER1 = 1 
    CODER2 = 2 

class MOBILE_APPS(Enum):
    WHATSAPP = 1

class DATASETS(Enum):
    GUZMAN=1


# In[20]:

class XML_REVIEW_DATASET(object):
    
    def __init__(self,dataset,app_name,coder):
        self.dataset = dataset
        self.app_name = app_name
        self.annotator = coder
    
    def ReadReviewWithAspectTerms(self):
        if self.annotator==ANNOTATORS.CODER1:
            app_data_path='./Datasets/' + self.dataset.name + "/CODER1/" +  self.app_name.name + "/" + self.app_name.name + "_TEST.xml"
        elif self.annotator ==ANNOTATORS.CODER2:
            app_data_path= './Datasets/' + self.dataset.name + "/CODER2/" +  self.app_name.name + "/" + self.app_name.name + "_TEST.xml"

        tree = ElementTree.parse(app_data_path)
        corpus = tree.getroot()
        reviews = corpus.findall('.//sentence')
        
        reviews_with_aspect_terms={}
        
        reviews_node = Element('sentences')
        
        for review in reviews:
            review_id = review.attrib['id']
            review_text = re.sub(r'\s+'," ",review.find('text').text)
            
            aspectTerms = review.find('aspectTerms')
            
            list_aspect_terms=[]
            
            if aspectTerms is not None:
                aspectTerm = aspectTerms.findall('aspectTerm')
               
                for aspect_term in aspectTerm:
                    app_feature = aspect_term.attrib['term'].strip()
                    list_aspect_terms.append(app_feature)
            
            reviews_with_aspect_terms[review_id]={'review_text':review_text,'true_features':list_aspect_terms,'predicted_features':[]}
        
        return(reviews_with_aspect_terms)


# In[29]:

# if __name__== '__main__':
#     objXML_DS = XML_REVIEW_DATASET(DATASETS.GUZMAN,MOBILE_APPS.WHATSAPP,ANNOTATORS.CODER1)
#     review_with_true_features = objXML_DS.ReadReviewWithAspectTerms()
#     reviews_list = [review_with_true_features[review_id]['review_text'] for review_id in review_with_true_features.keys()]
#     print(reviews_list)


# In[ ]:



