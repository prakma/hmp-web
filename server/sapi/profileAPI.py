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
		profileList = queryAPI.findProfileByProviderId(subscrList[0].key.id())
		if(len(profileList) == 0):
			if('_id' in profileJSON):
				rs = {
					"result" : "Failure",
					"code" : 'S4002',
					"message" : '_id provided for a new profile'
					}
				return rs
			# it is new case
			# create a new session entry
			profile = providerProfile.PbProfile ()
			profile.subscriber = subscrList[0].key

		else:
			# setup profile for the first time
			# profileId = profileJSON['_id']
			# profile = queryAPI.findProfileByID(profileId)
			profile = profileList[0]

		profileJSON['name'] = subscrList[0].name
		# createDefaultProfile(profile)
		profile.updateWithJSONInput(profileJSON)
		profile.put()

		return ndb_json.dumps(profile)

def createDefaultProfile(profile):
	profile.feeStruc = providerProfile.FeeStruct()
	profile.feeStruc.baseCurrency = 'INR'
	profile.feeStruc.regularFee = 300
	profile.feeStruc.followupFee = 100
	profile.feeStruc.followupDuration = '1 month'
	profile.feeStruc.platformFee = 200

	profile.calStruc = providerProfile.CalendarStruct()
	profile.calStruc.mon = '8 AM to 5 PM'
	profile.calStruc.tue = '8 AM to 5 PM'
	profile.calStruc.wed = '8 AM to 5 PM'
	profile.calStruc.thu = '8 AM to 5 PM'
	profile.calStruc.fri = '8 AM to 5 PM'
	profile.calStruc.sat = '1 PM to 10 PM'
	profile.calStruc.sun = 'Closed'

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

