import json
from model import subscriber, queryAPI, ndb_json

def addSubscriber(subsJSON):
	print 'json input is ', subsJSON
	# check if this email is already registered
	subscrList = queryAPI.findSubscriberByEmail ( subsJSON['email'] )
	if ( len(subscrList) == 0 ):
		newSubscriber = subscriber.Subscriber () # email=[], phone=[], name='' )
		def f(x) : setattr ( newSubscriber, x, subsJSON[x] )
		map ( f,subsJSON.keys() )
		#newSubscriber.name = subsJSON['name']
		#print 'subscribers name ( before ) is', newSubscriber.name
		# newSubscriber.populate(subsJSON)
		newSubscriber.put()

		# success response
		rs = {
		"result" : "Success",
		"code" : 'S2001',
		"key" : newSubscriber.key.id(),
		"name" : newSubscriber.name
		}
		return rs

	else:
		# failure response
		print 'Subscriber name already exists', subscrList[0].name
		rs = {
		"result" : "Failure",
		"code" : 'S4001',
		"message" : 'Email Already Subscribed'
		}
		return rs

def querySubscriberByEmail(queryJSON):
	if ( queryJSON['email'] != None):
		subscrList = queryAPI.findSubscriberByEmail ( queryJSON['email'] )
		return ndb_json.dumps(subscrList)
	else:
		rs = {
		"result" : "Failure",
		"code" : 'S4001',
		"message" : 'Query not supported'
		}
		return rs

def x_querySubscriberByToken(token):
	print 'token received for authentication check', token
	sessionCursor = queryAPI.findSubscriberSessionByToken(token)
	print 'authentication check result', sessionCursor
	if ( len (sessionCursor) > 0 ):
		user = sessionCursor[0].subscriber.get()
		return user
	else:
		return None

def getDefaultSubscribers():
	providerCursor = queryAPI.findDefaultProviders()
	return ndb_json.dumps(providerCursor)

def getProviderByKey(providerId):
	providerObj = queryAPI.findProviderById(providerId)
	if(providerObj != None):
		return ndb_json.dumps(providerObj)
	else:
		rs = {
		"result" : "Failure",
		"code" : 'S4001',
		"message" : 'Unknown Provider '+providerId
		}
		return rs




	

	

