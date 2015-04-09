"""`main` is the top level module for your Bottle application."""

# import the Bottle framework
from bottle import Bottle, template, static_file, request, response
from webargs import Arg
from webargs.bottleparser import use_args

from sapi import subscriberAPI, sessionAPI, consultAPI

import os

# Create the Bottle WSGI application.
bottle = Bottle(catchall=False)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

# secret used for writing and reading session token cookie
cookie_secret = 'baltibloombuttonberg'

def ensureLogin(func):
	token = request.get_cookie("hmp_account", secret=cookie_secret)

	print 'ensureLogin called'
	# def func_unauthenticated(*args, **kwargs):
	# 	return {'result':'Failure', 'message':'Unauthenticated'}
	# def func_wrapper(*args, **kwargs):
	# 	if (token == None):
	# 		print 'returning json'
	# 		return func_unauthenticated(*args, **kwargs)
	# 	else:
	# 		print 'returning func_wrapper'
	# 		return func(*args, **kwargs)
	# return func_wrapper
	if(token != None):
		return subscriberAPI.x_querySubscriberByToken(token)
	else:
		return None



# registration methods
subscriber_args = {
	'name': Arg(str),
    'email': Arg(str),
    'passwd': Arg(str),
    'providerFlag': Arg(bool),
    'primaryLocationStr': Arg(str)
}

@bottle.route('/s/subscriber', method='PUT')
@use_args(subscriber_args)
def subscribe(args):
	print "new subscriber called", args
	return subscriberAPI.addSubscriber(args)
	#print request.body

@bottle.route('/s/subscriber', method='POST')
@use_args(subscriber_args)
def register(args):
	print "new subscriber called with post", args

	resultJson = subscriberAPI.addSubscriber(args)
	if (resultJson['result'] == "Success"):
		subscSession = sessionAPI.x_postRegistrationlogin(resultJson['result'])
		resultJson['token'] = subscSession.sessionToken
		response.set_cookie("hmp_account", subscSession.sessionToken, secret=cookie_secret, path='/')
	return resultJson
	#print request.body



#login, logout methods
session_args = {
    'email': Arg(str),
    'passwd': Arg(str),
    'pf': Arg(bool)
}
@bottle.route('/s/login', method='POST')
@use_args(session_args)

def login(args):
	resultJson = sessionAPI.login(args)
	if (resultJson['result'] == "Success"):
		response.set_cookie("hmp_account", resultJson['token'], secret=cookie_secret, path='/')
	return resultJson

@bottle.route('/s/logout', method=['GET','POST'])
def logout():
	token = request.get_cookie("hmp_account", secret=cookie_secret)
	resultJson = sessionAPI.logout({'token' : token})
	return resultJson



# subscriber query methods
subscriber_query_args = {
    'email': Arg(str)
}

@bottle.route('/s/subscriber', method='GET')
def query(args):
	print "query subscribers - ", args
	user = ensureLogin(None)
	if(user == None):
		return {'result':'Failure', 'message':'Unauthenticated'}
	return subscriberAPI.querySubscriberByEmail(args)
	#print request.body
	#return {'result':'success'}

@bottle.route('/s/subscriber/_default', method='GET')
def defaultProviders():
	print 'defaultprovider queried'
	return subscriberAPI.getDefaultSubscribers()

@bottle.route('/s/subscriber/doc/<docProfileId:int>', method='GET')
def fetchProvider(docProfileId):
	print 'fetchprovider queried', docProfileId
	return subscriberAPI.getProviderByKey(docProfileId)

# # consultation workflow methods
# consult_args = {
#     'provider': Arg(int),
#     'requestedTS': Arg(str),
#     'token': Arg(str),
#     'problemSummary': Arg(str)
# }

# @bottle.route('/s/subscriber', method='GET')
# @use_args(subscriber_query_args)
# def query(args):
# 	print "query subscribers - ", args
# 	user = ensureLogin(None)
# 	if(user == None):
# 		return {'result':'Failure', 'message':'Unauthenticated'}
# 	return subscriberAPI.querySubscriber(args)
# 	#print request.body
# 	#return {'result':'success'}

# consultation workflow methods

@bottle.route('/s/consult', method='PUT')
@use_args({'providerId':Arg(int)})
def beginConsultWF(args):
	print 'initiateConsult called with args'
	user = ensureLogin(None)
	if(user == None):
		return {'result':'Failure', 'message':'Unauthenticated'}
	args['user'] = user	
	return consultAPI.beginConsultWF(args)
	# return {'result':'Failure', 'message':'Not implemented yet'}

consult_args = {
    'cref': Arg(int),
    'patientName': Arg(str),
    'age': Arg(str),
    'sex': Arg(str),
    'requestedTS': Arg(str),
    'problemSummary': Arg(str)
}
@bottle.route('/s/consult/appt', method='POST')
@use_args(consult_args)
def consultWF_appt(args):
	print 'consultWF_appt called with args'
	user = ensureLogin(None)
	if(user == None):
		return {'result':'Failure', 'message':'Unauthenticated'}
	args['user'] = user	
	return consultAPI.apptRequestWF(args)


# consult_patientq_args = {
#     'cref': Arg(int),
#     'reference': Arg(str),
#     'qkey1': Arg(str),
#     'qkey2': Arg(str),
#     'qkey3': Arg(str),
#     'qkey4': Arg(str),
# }
@bottle.route('/s/consult/patientq', method='POST')
#@use_args(consult_patientq_args)
def consultWF_patientq():
	print 'consultWF_patientq called with args...'
	#args = {}
	user = ensureLogin(None)
	if(user == None):
		return {'result':'Failure', 'message':'Unauthenticated'}
	#args['user'] = user	
	qkeys = request.json
	#qkey1 = args['qkey1']
	args = {x:request.json.get(x) for x in request.json.keys()}
	args['user'] = user
	#print 'form decoded with gvalues', args
	return consultAPI.patientQuestionWF(args)


@bottle.route('/s/consult/user_appts', method='GET')
def consultWF_user_appts():
	print 'consultWF_user_appts called with args...'
	args = {}
	user = ensureLogin(None)
	if(user == None):
		return {'result':'Failure', 'message':'Unauthenticated'}
	args['user'] = user	
	return consultAPI.getRecentAppointmentsForUser(args)

@bottle.route('/s/consult/cwf/<cref>', method='GET')
def consultWF_get(cref):
	print 'consultWF_get called with cref-', cref
	args = {}
	user = ensureLogin(None)
	if(user == None):
		return {'result':'Failure', 'message':'Unauthenticated'}
	args['user'] = user
	args['cref'] = cref
	return consultAPI.getConsultWF(args)


@bottle.route('/s/consult/provider_appts', method='GET')
def consultWF_user_appts():
	print 'consultWF_provider_appts called with args...'
	args = {}
	user = ensureLogin(None)
	if(user == None):
		return {'result':'Failure', 'message':'Unauthenticated'}
	args['user'] = user	
	return consultAPI.getRecentAppointmentsForProvider(args)


@bottle.route('/s/<:re:.+>')
def default_index():
	return static_file('index.html', root='client/static')

# Define an handler for 404 errors.
@bottle.error(404)
def error_404(error):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.'

# Define an handler for 404 errors.
@bottle.error(500)
def error_500(error):
    """Return a custom 500 error."""
    print error
    return 'Sorry, Something went wrong.'
