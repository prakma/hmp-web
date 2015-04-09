from model import subscriber, queryAPI, ndb_json
import uuid
import datetime

def login (args):

	email = args['email']
	password = args['passwd']
	providerFlag = ['pf']

	failureResult = { 'result' : 'Failure', 'message' : '' }
	successResult = {'result' : 'Success', 'token' : '', 'userName':'', 'id':''}

	#check if it is valid subscriber trying to login
	userList = queryAPI.findSubscriberByEmail(email)
	if ( len(userList) > 0 ):
		user = userList[0]
		flag = user.checkPassword(password)

		if (flag):

			# check if user is trying to login as provider, if so is he really a provider
			if (providerFlag):
				genuineProvider = user.isProvider()
				if (not genuineProvider):
					failureResult['message'] = 'Not a known provider'
					return failureResult


			# check if the session object exists and has not expired
			existingSessionCursor = queryAPI.findSubscriberSession (user.key)

			# if yes, then return the token
			if ( len (existingSessionCursor) > 0 and len (existingSessionCursor[0].sessionToken) > 0 ):
				existingSession = existingSessionCursor[0]
				successResult['token'] = existingSession.sessionToken
				existingSession.incrementAccessCount() 
				existingSession.put()
			else:
				# create a new session entry
				newSubscriberSession = subscriber.SubscriberSession ()
				newSubscriberSession.subscriber = user.key
				newSubscriberSession.sessionToken = uuid.uuid4().hex
				newSubscriberSession.accessCount = 1;
				newSubscriberSession.sessionStartTS = datetime.datetime.now()

				newSubscriberSession.put()
				successResult['token'] = newSubscriberSession.sessionToken

			successResult['name'] = user.name
			successResult['id'] = user.key.id()	
			return successResult

		else:
			failureResult['message'] = 'Unknown Login Credentials'

	else:
		failureResult['message'] = 'Unknown Credentials'

	return failureResult

def x_postRegistrationlogin (subscriberKey):
	# create a new session entry
	newSubscriberSession = subscriber.SubscriberSession ()
	newSubscriberSession.subscriber = queryAPI.createKeyFromId('Subscriber',subscriberKey)
	newSubscriberSession.sessionToken = uuid.uuid4().hex
	newSubscriberSession.accessCount = 1;
	newSubscriberSession.sessionStartTS = datetime.datetime.now()

	newSubscriberSession.put()
				
	return newSubscriberSession



def logout (args):

	token = args['token']
	print 'sessionapi.logout, token', token
	failureResult = { 'result' : 'Failure', 'message' : '' }
	successResult = {'result' : 'Success', 'message' : '' }

	if (token == None):
		failureResult ['message'] = 'No token provided'
		return failureResult

	existingSessionCursor = queryAPI.findSubscriberSessionByToken (token)
	print 'logout with token', token, 'existingsessjioncurson', existingSessionCursor

	if ( len (existingSessionCursor) > 0 ):
		existingSession = existingSessionCursor[0]
		existingSession.logout()
		existingSession.put()

		successResult['message'] = 'Logged Out'
		return successResult

	else:
		failureResult ['message'] = 'No login session to logout'
		return failureResult








