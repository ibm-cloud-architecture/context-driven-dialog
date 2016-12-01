import os,requests,json

'''

'''
from datetime import date
class CRM(object):

        def __init__(self):
                pass
        
        def loadCustomer(self,customerId):
                customer={'vipPoints':100}
                customer['customerID']=customerId
                customer['impactedProduct']=None
                customer['ownedProducts']=None
                return customer

        def loadProducts(self,customerId):
                d=date(2016,10,20)
                list=[]
                p={'name':'iphone','type':'SmartPhone','brand':'Apple','partNumber':'123','eligibleForUpgrade':False}
                p['acquisitionDate']=d.isoformat()
                p['deviceProtection']=False
                list.append(p)
                d=date(2014,10,20)
                p={'name':'ipad','type':'Tablet','brand':'Apple','partNumber':'123456','eligibleForUpgrade':False}
                p['acquisitionDate']=d.isoformat()
                p['deviceProtection']=False
                list.append(p)
                return list
        

                      
