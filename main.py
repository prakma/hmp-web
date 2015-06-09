"""`main` is the top level module for your Bottle application."""

# import the Bottle framework
from bottle import Bottle, template, static_file, request, response, redirect
from webargs import Arg
from webargs.bottleparser import use_args

from sapi import subscriberAPI, sessionAPI, consultAPI, profileAPI

import os, base64

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
		subscSession = sessionAPI.x_postRegistrationlogin(resultJson['key'])
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

apptWF_args = {
	'aptWFCd': Arg(int),
    'rescheduledDt': Arg(str),
    'reason': Arg(str)
}
@bottle.route('/s/consult/cwf/<cref>/apptwf', method='POST')
@use_args(apptWF_args)
def consultWF_setApptWF(args, cref):
	# print 'consultWF_get called with cref-', cref
	print 'args parsed', args
	user = ensureLogin(None)
	if(user == None):
		return {'result':'Failure', 'message':'Unauthenticated'}
	args['user'] = user
	args['cref'] = cref
	return consultAPI.consultWF_setApptState(args)
	return {'result': 'Success', 'message':'Todo - State not implemented'}


@bottle.route('/s/consult/provider_appts', method='GET')
def consultWF_provider_appts():
	print 'consultWF_provider_appts called with args...'
	args = {}
	user = ensureLogin(None)
	if(user == None):
		return {'result':'Failure', 'message':'Unauthenticated'}
	args['user'] = user	
	return consultAPI.getRecentAppointmentsForProvider(args)

providerProfile_args = {
	'token': Arg(int),
	'email': Arg(str),
	'degree': Arg(),
	'oneLiner': Arg(str),
	'profileDesc': Arg()
	
}
@bottle.route('/s/profile/provider', method='POST')
# @use_args(providerProfile_args)
def set_provider_profile():
	#args = {}
	#print 'setup provider profile called', args
	# print request.json
	return profileAPI.setupProfile(request.json)

@bottle.route('/s/provider/<providerId>/profile', method='GET')
def get_provider_profile(providerId):
	print 'get provider profile called', providerId
	return profileAPI.getProfile(providerId);

# def update_appt_request

paymentReturn_args = {
	'key': Arg(str),
	'order_number': Arg(str),
	'invoice_id': Arg(str),
	'credit_card_processed': Arg(str),
	'total': Arg(str),
	'li_0_product_id': Arg(str),
	'merchant_order_id': Arg(str)
	
}
@bottle.route('/s/payment/return', method='POST')
@use_args(paymentReturn_args)
def payment_processed_cb(paymentReturn_args):
	# 4358 8099 6104 9974
	# 05/19
	# 914
	# print 'payment was processed'
	print 'payment processing details received', paymentReturn_args
	cref = paymentReturn_args['li_0_product_id']
	# UPPERCASE(MD5_ENCRYPTED(Secret Word + Seller ID + 1 + Sale Total))
	# $hashSecretWord = 'tango'; //2Checkout Secret Word
	# $hashSid = 1303908; //2Checkout account number
	# $hashTotal = '1.00'; //Sale total to validate against
	# $hashOrder = $_REQUEST['order_number']; //2Checkout Order Number
	# $StringToHash = strtoupper(md5($hashSecretWord . $hashSid . $hashOrder . $hashTotal));

	consultAPI.consultWF_updatePayment(paymentReturn_args)

	redirect("/user/index.html#/user/cwf/"+cref+"/payment/return")
	# return static_file('index.html', root='client/static/user/cwf/:cref/payment/return')

@bottle.route('/s/consult/cwf/<cref>/createPrescriptionURL', method='POST')
def create_upload_url(cref):
	args = {}
	args['cref'] = cref
	args['prescription_url'] = '/s/consult/cwf/'+cref+'/prescription'
	print 'create upload url for prescription', cref
	return consultAPI.create_upload_url(args)

@bottle.route('/s/consult/cwf/<cref>/prescription', method='POST')
def prescription_uploaded(cref):
	print 'prescription uploaded for cref', cref, request.forms, request.files
	f = request.files['uploaded_files']
	print 'uploaded files data', f.name
	print 'raw_filename', f.raw_filename
	print 'filename', f.filename
	print 'content_type', f.content_type
	print 'content_length', f.content_length


	def parse_gae_blobkey(content_type_val):
		blob_key_and_val = content_type_val.split(';')[1]
		print 'blob_key_and_val', blob_key_and_val
		blobKey = blob_key_and_val.split('=',1)[1][1:-1]
		print 'blobKey', blobKey
		return blobKey

	print 'blobkey', parse_gae_blobkey(f.content_type)
	args = {}
	args['cref'] = cref;
	args['blob_key'] = parse_gae_blobkey(f.content_type)

	consultAPI.handlePrescriptionOnUpload(args)

	redirect('/provider/provider_index.html#/provider/dashboard/'+cref+'/appt_view.html')

@bottle.route('/s/consult/cwf/<cref>/prescription/<blobKey>', method='GET')
def prescription_download(cref, blobKey):
	print 'prescription uploaded for cref, blobkey', cref, blobKey[1:-1]
	response.set_header('X-AppEngine-BlobKey', blobKey) #base64.b64decode(blobKey[1:-1] ) )
	response.set_header('content-disposition', 'attachment; filename=prescription_'+cref+'.pdf')
	return response;



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
