# import the Bottle framework
from bottle import Bottle, template, static_file, request, response, redirect
from webargs import Arg
from webargs.bottleparser import use_args
from twilio.rest import TwilioRestClient
import hmpconstants
from model import subscriber, queryAPI, ndb_json, providerProfile
import sys, traceback
from dateutil import tz
from datetime import *
from dateutil.tz import *

# Create the Bottle WSGI application.
webhook = Bottle(catchall=False)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.






# registration methods
sendsms2p_args = {
	'cref': Arg(int),
	'apptWFStateCd': Arg(int)
}
@webhook.route('/s/wh/sendSMS2P', method='POST')
@use_args(sendsms2p_args)
def doSendSMS2Provider(args):
	print "doSendSMS2Provider called with post", args
	
	cref = args['cref']
	try:
		cwf = queryAPI.findConsultationWFById(cref)
	except:
		print "Error: doSendSMS2Provider: Invalid cref ", cref
		return {'result':'Failure'}

	providerId = cwf.provider.id()
	provider = queryAPI.findEntityByKey('Subscriber', providerId)
	if( provider == None):
		# raise Exception('Invalid provider with key', providerkey );
		print "Error: doSendSMS2Provider: Invalid provider ", providerId
		return {'result':'Failure'}


	providerPhone = provider.phone[-1]
	taccount_sid = hmpconstants.TwilioSetup.account_sid
	taccount_auth = hmpconstants.TwilioSetup.auth_token
	# taccount_app = hmpconstants.TwilioSetup.application_sid

	client = TwilioRestClient(taccount_sid, taccount_auth) 
 	
 	try:
 		# find provider's timezone and convert appropriately. for now, hardcoded to IST
 		requestedTimeInIndiaTZ = cwf.apptWF.requestedTS.replace(tzinfo=tzoffset("IST", +5*60*60))
 		# fmt1 = requestedTimeInIndiaTZ.strftime('%Y-%m-%d %H:%M:%S %Z')
		fmt2 = requestedTimeInIndiaTZ.strftime('%a, %b %d, %I:%M %p %Z')
 		smsbody = "Appt request for "+str(fmt2)+". Accept or reschedule at remedysquare.com" 
 		print smsbody
		client.messages.create(
			to=providerPhone, 
			from_=hmpconstants.TwilioSetup.hmp_owned_number_sms, 
			body=smsbody 
		)

		print "twilio call to send sms completed"
	except:
		e = sys.exc_info()[0]
		print "Error: doSendSMS2Provider: problem sending it to Twilio ", cref, e
		traceback.print_exc(file=sys.stdout)
		return {'result':'Failure'}

	return {'result':'Success'}


@webhook.route('/s/wh/sendSMS2U', method='POST')
@use_args(sendsms2p_args)
def doSendSMS2User(args):
	print "doSendSMS2User called with post", args
	
	cref = args['cref']
	apptWFStateCd = args['apptWFStateCd']
	try:
		cwf = queryAPI.findConsultationWFById(cref)
	except:
		print "Error: doSendSMS2User: Invalid cref ", cref
		return {'result':'Failure'}

	
	taccount_sid = hmpconstants.TwilioSetup.account_sid
	taccount_auth = hmpconstants.TwilioSetup.auth_token
	# taccount_app = hmpconstants.TwilioSetup.application_sid

	client = TwilioRestClient(taccount_sid, taccount_auth) 
 	
 	try:
 		# find user's timezone and convert appropriately. for now, hardcoded to IST
 		confirmedTimeInIndiaTZ = cwf.apptWF.confirmedTS.replace(tzinfo=tzoffset("IST", 5*60*60))
 		userPhone = cwf.patientDetailsWF.patientPhone
 		providerName = cwf.providerName

		fmt2 = confirmedTimeInIndiaTZ.strftime('%a, %b %d, %I:%M %p %Z')
		if(apptWFStateCd == 3):
 			smsbody = "Dr "+str(providerName)+" @remedysquare.com has confirmed your appointment at "+str(fmt2)+" " 
 		elif(apptWFStateCd == 5):
 			smsbody = "Dr "+str(providerName)+" @remedysquare.com has rescheduled your appointment at "+str(fmt2)+". Go to remedysquare.com to confirm or further reschedule "

 		print smsbody
		client.messages.create(
			to=userPhone, 
			from_=hmpconstants.TwilioSetup.hmp_owned_number_sms, 
			body=smsbody 
		)

		print "twilio call to send user sms completed"
	except:
		e = sys.exc_info()[0]
		print "Error: doSendSMS2User: problem sending it to Twilio ", cref, e
		traceback.print_exc(file=sys.stdout)
		return {'result':'Failure'}

	return {'result':'Success'}
