from google.appengine.ext import ndb
from subscriber import Subscriber, SubscriberSession, ConsultationWF
from providerProfile import PbProfile
from feedback import GeneralFeedback

def findEntityByKey(entityName, key):
	entityKeyObj = ndb.Key(entityName, key)
	return entityKeyObj.get()

def findSubscriberByEmail(email):
	return Subscriber.query(Subscriber.email == email).order(Subscriber.lastUpdatedTS).fetch(5)

def findSubscriberSession(subscriberKey):
	return SubscriberSession.query(
				SubscriberSession.subscriber == subscriberKey,
				SubscriberSession.sessionStatus == 1,
			).order(-SubscriberSession.lastRefreshedTS).fetch(1)

def findSubscriberSessionByToken(token):
	return SubscriberSession.query(
				SubscriberSession.sessionToken == token,
				SubscriberSession.sessionStatus == 1,
			).order(-SubscriberSession.lastRefreshedTS).fetch(1)

def createKeyFromId(entity_name,key_id):
	return ndb.Key(entity_name, key_id)

def findDefaultProviders():
	return Subscriber.query(Subscriber.providerFlag == True,
		Subscriber.subscribeStatus == 1,
		).order(Subscriber.lastUpdatedTS).fetch(10)

# def findProviderById(providerId):
# 	print '******** findProviderById is called. Strange if it is working !!! **********'
# 	return findProviderById(providerId)



def findSubscriberById(subscriberId):
	subscriberKey = ndb.Key('Subscriber', subscriberId)
	return subscriberKey.get()

def findConsultationWFById(cwfRef):
	cwfKey = ndb.Key('ConsultationWF', cwfRef)
	return cwfKey.get()

def findConsultationByUserId(userId):
	print 'find consultation by user id', userId
	return ConsultationWF.query(
				ConsultationWF.user == ndb.Key('Subscriber', userId)
				
			).order(-ConsultationWF.lastRefreshedTS).fetch() 

def findConsultationByProviderId(providerId):
	return ConsultationWF.query(
				ConsultationWF.provider == ndb.Key('Subscriber', providerId),
				ConsultationWF.overallStatus < 3
			).order(ConsultationWF.overallStatus, ConsultationWF.apptWF.confirmedTS).fetch() 

def findProfileByProviderId(providerId):
	print 'findProfileByProviderId', str(providerId)
	return PbProfile.query(
		PbProfile.subscriber == ndb.Key('Subscriber', providerId),
		).fetch(1)

def getProvidersByProviderIds(providerIds):
	print 'getProvidersByProviderIds', providerIds
	providerKeys = []
	for x in providerIds:
		providerKeys.append(ndb.Key('Subscriber', x))
	list_of_entities = ndb.get_multi(providerKeys)
	return list_of_entities

def findProfilesByGivenProviderIds(providerIds):
	print 'find profiles by given provider ids', providerIds
	providerKeys = []
	for x in providerIds:
		providerKeys.append(ndb.Key('Subscriber', x))

	return PbProfile.query(PbProfile.subscriber.IN(providerKeys)).fetch()
	# providerProfiles = []
	# for pId in providerIds:
	# 	providerProfiles.append(findProfileByProviderId(pId))
	# return providerProfiles

# def findProfilesByGivenProviderIds(providerIds):
# 	return PbProfile.query(
# 		PbProfile.subscriber.IN(providerIds,
# 		).fetch()

def findFeedbackById(feedbackId):
	feedbackKey = ndb.Key('GeneralFeedback', feedbackId)
	return feedbackKey.get()
