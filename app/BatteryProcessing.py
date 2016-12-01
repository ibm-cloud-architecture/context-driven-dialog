'''
This module supports the logic to process a battery conversation
10/2016 Jerome Boyer - IBM
'''
from bmx_rs_client import RuleServiceClient
from crm_client import CRM
import json

ruleApp = {
  'name': 'DDRuleApp',
  'appArchive': 'data/ruleApp_DDRuleApp_1.0.jar',
  'appModel': 'data/dyndialog-model.zip'
}


rs=RuleServiceClient(ruleApp = ruleApp)

'''
Use first ruleset in ODM / IBM Business Rules to assess the data quality and 
load existing data from other sources as appropriate
'''
def encrichAssessmentData(assessment):
  ruleSet = 'AssessDataNeeds'

  query = {
    'assessment': assessment
  }
  
  # Query the AssessDataNeeds ruleset to see if we have all the required data available
  r=rs.queryRuleset(ruleSet, query)
  
  # Extract the assessment data from the decision
  a = r['assessment']

  ## Cycle through the recommandations until the data is deemed to be complete
  complete=False
  while not complete:
    if a['status'] == 'Uncompleted':
      
      if isRecommendationPresent(a,'Load Customer'):
        crm=CRM()
        customer=crm.loadCustomer(a['customerId'])
        a['customerContext']=customer
        
      if isRecommendationPresent(a,'Load Product'):
        products=crm.loadProducts(a['customerId'])
        a['customerContext']['ownedProducts']=products

      # Re-assess with latest data
      query['assessment'] = a
      r = rs.queryRuleset(ruleSet, query)
      a = r['assessment']
      
    elif a['status'] == 'DataCompleted':
      #a = rs.processQuestion(a)
      complete=True
  return a

'''
   Main entry point to process the logic flow of the Battery Conversation
'''
def execute(assessment):

  if assessment['status'] == 'New':
    # Run through assessDataNeed rules and populate assessment data from external sources as recommended by ruleset
    a = encrichAssessmentData(assessment)
    query = {
      'assessment': a
    }
  else:
    # This is part of an ongoing dialog
    query = {
      'assessment': assessment
    }
  
  # Process the question by running the assessment through the ManageDialog ruleset
  ruleSet = 'ManageDialog'
  r = rs.queryRuleset(ruleSet, query)
  return r['assessment']
     
               
def isRecommendationPresent(assessment,recommendation):
  for r in assessment['recommendations']:
    if recommendation in r['message']:
      return True
  return False


if __name__ == "__main__":
  a={"customerId":'bill',"status":"New","customerQuery":{"firstQueryContent":"battery","categories":[],"acceptedCategory":"battery"},"creationDate":"2016-10-28T00:00:00.000+0000"}
#       c=CRM.loadCustomer(a,'bill')
#       a['assessment']['customerContext']=c
  a=execute(a)
  print(a)
