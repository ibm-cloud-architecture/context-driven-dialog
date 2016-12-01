import os,requests,json

'''

'''
class RuleServiceClient(object):

  def __init__(self, ruleApp):
    # Get the credentials from Bluemix VCAP_SERVICES, assuming there's only one connected rule service
    if os.environ.get('VCAP_SERVICES'):
      rulesservice = json.loads(os.environ.get('VCAP_SERVICES'))['businessrules']
      self.user    = str(rulesservice[0]['credentials']['user'])
      self.pwd     = str(rulesservice[0]['credentials']['password'])
      self.url     = str(rulesservice[0]['credentials']['executionRestUrl']) + '/v1'
      self.adminUrl= str(rulesservice[0]['credentials']['executionAdminRestUrl']) + '/v1'
    else:
      exit('Please run this application from Bluemix, binding the relevant Watson services')

    # Some common request settings
    acceptJson={'Accept': 'application/json'}
    contentJson={'Content-Type': 'application/json', 'Accept': 'application/json'}
    contentOctet={'Content-Type': 'application/octet-stream', 'Accept': 'application/json'}
    auth=(self.user, self.pwd)
    
    
    self.ruleApp = ruleApp['name']

    # Check if the requested ruleApp is available, and upload if necessary
    r = requests.get(self.adminUrl + '/ruleapps/' + self.ruleApp, 
          auth=auth, 
          headers=acceptJson)
    if r.status_code == 200:
      if len(r.json()) == 0:
        # We must upload the rulesApp
        print 'Uploading ruleApp: ' + self.ruleApp + ' from file: ' + ruleApp['appArchive']
        data = open(ruleApp['appArchive'], 'rb').read()
        u = requests.post(self.adminUrl + '/ruleapps', 
              auth=auth, 
              data=data, 
              headers=contentOctet)
              
        if u.status_code == 200:
          print 'Upload successful'
        else:
          print 'Upload failed with error: ' + u.text
          print 'Status code was ' + str(u.status_code)
      else:
        print 'Found ruleApp.'

      # Construct the URL for the rulesets
      self.dataNeedRuleSet  = 'DDRuleApp/AssessDataNeeds'
      self.dialogRuleSet    = 'DDRuleApp/ManageDialog'
    else:
      print 'Status code was ' + str(r.status_code)

      
    # Check if the Model is available
    r = requests.get(self.adminUrl + '/xoms/' + os.path.basename(ruleApp['appModel']), 
            auth=auth, 
            headers=acceptJson)
            
    if r.status_code == 200:
      if len(r.json()) == 0:
        # We must upload the model
        print 'Uploading model file ' + ruleApp['appModel']
        data = open(ruleApp['appModel'], 'rb').read()
        u = requests.post(self.adminUrl + '/xoms/'+os.path.basename(ruleApp['appModel']), 
              auth=auth, 
              data=data, 
              headers=contentOctet)
        if u.status_code == 201:
          print 'Upload successful'
        else:
          print 'Upload failed with error: ' + u.text
          print 'Status code was ' + str(u.status_code)
          
        resUri = u.json()['resource']['uri']
        l = requests.post(self.adminUrl + '/libraries/' + self.ruleApp + '_1.0/1.0', 
              auth=(self.user, self.pwd), 
              data=resUri, 
              headers={'Content-Type': 'text/plain', 'Accept': 'application/json'})
        if l.status_code != 201:
          print 'Failed'
          print l.status_code
          print l.text

  def queryRuleset(self, ruleSet, query):
    url = self.url + '/' + self.ruleApp + '/' + ruleSet 
    print 'Request>>' + str(query)
    r = requests.post(url,
          json    = query,
          auth    = (self.user, self.pwd),
          headers = {'Content-Type': 'application/json', 'Accept': 'application/json'} )
        
    if r.status_code == 200:
      print r.text
      return r.json()
    else:
      print 'Error querying ruleset ' + ruleSet
      print url
      print query
      print r.status_code
      print r.text
      return r.json()
      
  def assessDataNeed(self,assessment):
    request={}
    request['assessment']=assessment
    reqStr=json.dumps(request)
    print("Request>>"+reqStr)
    response=requests.post(self.url+"/"+self.dataNeedRuleSet, data=reqStr, auth=(self.user, self.pwd), headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
    aOut=json.loads(response.text)
    print(aOut)
    return aOut['assessment']

  def processQuestion(self,assessment):
    request={}
    request['assessment']=assessment
    reqStr=json.dumps(request)
    print("Request>>"+reqStr)
    response=requests.post(self.url+"/"+self.dialogRuleSet,reqStr,auth=(self.user, self.pwd), headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
    aOut=json.loads(response.text)
    print(aOut)
    return aOut['assessment']
                      
# To upload rulesapp:
# files = {'file': open('report.xls', 'rb')} 
# request.post(url +'/rulesapp', files=files)
if __name__ =='__main__':
  a={'uid': 'string', 'customerQuery': {'firstQueryContent': 'my battery is draining', 'userId': 'bob',
    'acceptedCategory': 'battery'},
      'status': 'NEW',
      'creationDate': '2016-09-29T01:49:45.000+0000'
      }
  rs=RuleServiceClient();
  print(rs.assessDataNeed(a))
