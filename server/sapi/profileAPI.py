import json
from model import providerProfile, queryAPI, ndb_json

def setupProfile(profileJSON):
	print 'json input is ', profileJSON
	# check if this email is already registered
	subscrList = queryAPI.findSubscriberByEmail ( profileJSON['email'] )
	if ( len(subscrList) == 0 ):

		# failure response
		print 'Subscriber email not found to setup profile', profileJSON['email']
		rs = {
		"result" : "Failure",
		"code" : 'S4001',
		"message" : 'Unrecognized Subscriber'
		}
		return rs

	else:
		# check if the profile already exists
		
		if('_id' not in profileJSON):
			# it is new case
			# create a new session entry
			profile = providerProfile.PbProfile ()
			profile.subscriber = subscrList[0].key

		else:
			# setup profile for the first time
			profileId = profileJSON['_id']
			profile = queryAPI.findProfileByID(profileId)

		profileJSON['name'] = subscrList[0].name

		profile.updateWithJSONInput(profileJSON)
		profile.put()

		return ndb_json.dumps(profile)

def getProfile(providerId):
	if(providerId == None):
		rs = {
		"result" : "Failure",
		"code" : 'S4001',
		"message" : 'Unrecognized Provider '+str(providerId)
		}
		return rs
	else:

		profileList = queryAPI.findProfileByProviderId(int(providerId))
		size = len(profileList)
		if(size == 1):
			return ndb_json.dumps(profileList[0])
		elif(size == 0):
			raise Exception('Not a valid provider', providerId)
		else:
			print 'something wrong in this provider configuration. There is more than one profile available', providerId
			raise Exception('Profile is not available', providerId) 

