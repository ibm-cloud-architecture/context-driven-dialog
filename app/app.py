'''
Python Web App using Flask to offer a set of RESTful apis so the angularjs
client can get the dialog running.

The end user enters a query like: my battery is not holding charge
The UI will use a POST request to /dd/api/a/classify with a query json
that may look like:
{'firstQueryContent': "my battery is not holding charge",
'


This example is based on battery issue reporting.

10/2016 Jerome Boyer - IBM -  boyerje@us.ibm.com

Natural Language Classifier: https://www.ibm.com/watson/developercloud/doc/nl-classifier/
IBM Bluemix Business Rules: https://console.ng.bluemix.net/docs/services/rules/rules.html

'''
import os, json, requests
from flask import Flask,request,jsonify
from datetime import date
# Business logic is separated in its own module
import BatteryProcessing
# Watson Natural Language Classifier wrapper
from  NLCclient import NLClassifier

# When deploying to Bluemix Watson Service Credentials of bound services are available in VCAP_SERVICES
if os.environ.get('VCAP_SERVICES'):
  services = json.loads(os.environ.get('VCAP_SERVICES'))
  nlc_user = str(services['natural_language_classifier'][0]['credentials']['username'])
  nlc_pwd = str(services['natural_language_classifier'][0]['credentials']['password'])
else:
  exit('Please run this application from Bluemix, binding the relevant Watson services')

# Setup Flask
port = int(os.getenv('VCAP_APP_PORT', 8080))
app = Flask(__name__, static_url_path='')

# The NLC training data is typically not included in a production system, as the training is normally
# done by a data scientist. Customer facing applications will therefore typically not include
# code to load training sets
battery_classifier = {
  'name': 'battery',
  'training_file': 'data/device-trainSet.csv' 
}

# setup dependant component
nlc= NLClassifier(nlc_user, nlc_pwd, battery_classifier)


@app.route("/")
def root():
  return app.send_static_file('home.html')

# TODO this is a scafolding code
def buildAssessment(userid):
	assessment={'uid': 'string','status':'New'}
	assessment['customerId']=userid
	d=date.today()
	assessment['creationDate']=d.isoformat()
	return assessment

def assessClasse():
    pass
    
# Process the first user query: The payload is a user query json object
@app.route("/dd/api/a/classify",methods=['POST'])
def classifyFirstUserQuery():
  userQuery=request.get_json()
  print userQuery
  aQuery=userQuery['firstQueryContent']
  userId = userQuery['userId']
  
  # Pass the query to the Natural Language Classifier. 
  # The natural language classifier returns a collection of classifications ordered by confidence. 
  # The top class is returned in "top_class".
  # Details here: https://www.ibm.com/watson/developercloud/natural-language-classifier/api/v1/?python#classify
  categories=nlc.classify(aQuery)

  # In a typical setup the system is fully trained and verified by a data scientist before exposing data to a front end. 
  # However, in this demo application the Watson NLC system is trained at application push time, so there is a chance that 
  # users attempt to use the system before the Watson NLC system is fully trained.
  # If the classifier is still in training we'll receive an error here. Pass the error to AngularJS so the user knows the system is still in training.
  if 'error' in categories:
    return jsonify(categories)

  userQuery['acceptedCategory']=categories['top_class']

  # Create an assessment object that holds all the information we have gathered so far
  assessment=buildAssessment(userId)
  assessment['customerQuery']=userQuery

  # Each potential category may have a different flow. 
  # This demo has implemented logic related to device batteries using IBM Business Rules (IBM Operational Decidison Manager)
  if (userQuery['acceptedCategory'] == 'battery'):
    aOut=BatteryProcessing.execute(assessment)
  else:
    #TODO add logic for processing other classes
    aOut=assessment
  return jsonify(aOut)

'''
API to support the question and answer interaction
'''
@app.route("/dd/api/a",methods=['POST'])
def dialog():
        assessment=request.get_json()
        if (assessment['lastResponse']):
            assessment['responses'].append(assessment['lastResponse'])
        if (assessment['customerQuery']['acceptedCategory'] == 'battery'):
            aOut=BatteryProcessing.execute(assessment)
            return jsonify(aOut)
        else:
            return jsonify({"error":"Logic not implemented"})
 	   	
if __name__ == "__main__":
	print("Server v0.0.3 10/31")
	app.run(host='0.0.0.0', port=port)
