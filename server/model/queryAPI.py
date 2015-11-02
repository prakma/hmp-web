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
		).order(Subscriber.lastUpdatedTS).fetch(5)

def findProviderById(providerId):
	providerKey = ndb.Key('Subscriber', providerId)
	return providerKey.get()

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
	return PbProfile.query(
		PbProfile.subscriber == ndb.Key('Subscriber', providerId),
		).fetch(1);
	
def findFeedbackById(feedbackId):
	feedbackKey = ndb.Key('GeneralFeedback', feedbackId)
	return feedbackKey.get()
