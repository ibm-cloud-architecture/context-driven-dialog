'''
Front end for NLC transparent to the NLC used
API Reference available here: https://www.ibm.com/watson/developercloud/natural-language-classifier/api/v1/
'''
# Import Watson Service SDKs
from watson_developer_cloud import NaturalLanguageClassifierV1 as NLC

class NLClassifier(object):

  def __init__(self, username, password, classifier):
    # Setup Watson SDK
    self.natural_language_classifier = NLC(username=username,password=password)

    # Classifier information
    self.classifier = {}
    self.classifier['name'] = classifier['name']
    self.classifier['training_file'] = classifier['training_file']

    c = self.natural_language_classifier.list()
    if any(d['name'] == self.classifier['name'] for d in c['classifiers'] ):
      self.classifier['id'] = [ d['classifier_id'] for d in c['classifiers'] if d['name'] == self.classifier['name'] ][0]
      print 'Found classifier id %s ' % self.classifier['id']
      self.classifier['status'] = self.natural_language_classifier.status(self.classifier['id'])['status']
    else:
      print 'No classifier found, creating new from training set'
      self.classifier['id']  = self.create_classifier()
      print 'New classifier id: %s ' % self.classifier['id']
  
  ### Method to train the Watson Natural Language Classifier    
  # The training set is delivered as a CSV file as specified in the Developer Guide
  # https://www.ibm.com/watson/developercloud/doc/nl-classifier/data_format.shtml
  def create_classifier(self):
    training_data = open(self.classifier['training_file'], 'rb')
    training_result = self.natural_language_classifier.create( training_data=training_data, name=self.classifier['name'] )
    if training_result['status'] == "Training":
      self.classifier['status'] = "Training"
      return training_result['classifier_id']
    else:
      print training_result
      return "Error"
    
  
  def classify(self,text):
    # Typically in a production system Watson NLC will be fully trained and verified by a data scientist before the system is ever 
    # exposed in production. However because this is a demo application where Watson NLC is trained at application deployment time,
    # we will need to have a check to verify that the training is completed.
    if self.classifier['status'] == "Training":
      r = self.natural_language_classifier.status(self.classifier['id'])
      if r['status'] == "Training":
        return {"error": "Classifier still in training. Please try again in a few minutes."}
      elif r['status'] == "Available":
          self.classifier['status'] = 'Available'
      else:
        return {"error": "Unknown status for classifier", "message": r['status']}

    return self.natural_language_classifier.classify(self.classifier['id'], text)   


