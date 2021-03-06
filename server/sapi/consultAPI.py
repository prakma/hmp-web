from model import subscriber, queryAPI, ndb_json, providerProfile
from tasks import dispatcher
import platformAPI
import dateutil.parser
import datetime
import hashlib
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import sys

import hmpconstants
from collections import OrderedDict


def beginConsultWF (args):
	providerId = args['providerId']
	user = args['user']

	successResult = {'result' : 'Success', 'message' : '','reference':'' }
	failureResult = { 'result' : 'Failure', 'message' : '' }

	provider = queryAPI.findEntityByKey('Subscriber', providerId)
	if( provider == None):
		# raise Exception('Invalid provider with key', providerkey );
		failureResult['message'] = 'Invalid provider - ' + providerId
		# return Exception('Invalid user with token', sessionToken );
		return failureResult

	cwf = subscriber.ConsultationWF()
	cwf.provider = provider.key
	cwf.providerName = provider.name
	cwf.user = user.key
	# New
	cwf.overallStatus = 1

	cwf.put()
	successResult['message'] = 'Use the reference number '+str(cwf.key.id())+' for any future question or information about this consultation'
	successResult['reference'] = cwf.key.id()
	return successResult

consult_args = {
    'cref': '',
    'patientName': '',
    'age': '',
    'sex': '',
    'patientPhone': '',
    'consult_mode_pref': '',
    'requestedTS': '',
    'problemSummary': ''
}
def apptRequestWF (args):
	cref = args['cref'];
	patientName = args['patientName']

	patientAge = args['age']
	patientSex = args['sex']
	patientPhone = args['patientPhone']
	requestTSStr = args['requestedTS']
	consultationModePreference = args['consult_mode_pref']
	print 'requestTSStr received', requestTSStr
	problemSummary = args['problemSummary']
	user = args['user']

	failureResult = { 'result' : 'Failure', 'message' : '' }
	successResult = {'result' : 'Success', 'message' : '','reference':'' }

	#
	try:
		cwf = queryAPI.findConsultationWFById(cref)
	except:
		failureResult['message'] = 'Invalid Reference - ' + str(cref)
		return failureResult

	# check that cwf was initiated by this same user
	if(cwf.user.id() != user.key.id()):
		failureResult['message'] = 'Invalid Appointment Request. C-Ref belongs to another user'
		return failureResult

	cwf.apptWF = subscriber.ApptWF()
	cwf.apptWF.requestedTS = dateutil.parser.parse(requestTSStr).replace(tzinfo=None)
	print 'requestTS into python', cwf.apptWF.requestedTS
	cwf.apptWF.confirmedTS = dateutil.parser.parse(requestTSStr).replace(tzinfo=None)
	cwf.apptWF.apptStatusChain = [2]
	cwf.apptWF.apptStatus = 2


	# cwf = subscriber.ConsultationWF()
	# cwf.provider = provider.key
	# cwf.user = user.key

	cwf.patientDetailsWF = subscriber.PatientDetailsWF()
	cwf.patientDetailsWF.patientName = patientName
	cwf.patientDetailsWF.patientAge = patientAge
	cwf.patientDetailsWF.patientSex = patientSex
	cwf.patientDetailsWF.patientPhone = patientPhone
	cwf.patientDetailsWF.questionId = ['Summary']
	cwf.patientDetailsWF.answerText = [problemSummary]

	cwf.statusWF = subscriber.StatusWF()
	cwf.statusWF.overallStatusChain = [1]
	cwf.statusWF.overallStatus = 1 

	# create paymentWF and populate expected amount
	cwf.paymentWF = subscriber.PaymemtWF()
	# get the provider profile to populate expected payment
	profileList = queryAPI.findProfileByProviderId(cwf.provider.id())
	if(profileList == None or len(profileList) == 0):
		failureResult['message'] = 'Invalid Provider - ' + str(cwf.provider.id())
		return failureResult
	profile = profileList[0]

	cwf.paymentWF.prExpAmt = profile.feeStruc.regularFee
	cwf.paymentWF.plExpAmt = profile.feeStruc.platformFee # platformAPI.getPlatformFee(cwf)
	cwf.paymentWF.txExpAmt = 0
	cwf.paymentWF.expCurr = profile.feeStruc.baseCurrency
	cwf.paymentWF.deriveTotalExpectedAmount()
	cwf.paymentWF.paymentStatus = 1
	cwf.paymentWF.paymentStatusChain = [1]

	# create meetingWF and set the meeting type to consultation_mode_preference[phone, video or anything]
	cwf.meetingWF = subscriber.MeetingWF()
	cwf.meetingWF.meetingType = consultationModePreference

	
	

	# In-Progress
	cwf.overallStatus = 2

	cwf.put()

	dispatcher.sendSMSToProvider(cref, 2)
	successResult['message'] = 'Consultation request sent to Doctor. Waiting for his confirmation'
	successResult['reference'] = cwf.key.id()
	successResult['cwf'] = ndb_json.dumps(cwf)
	return successResult


patientq_args = {
    '_id': '',
    'user':'',
    # and the rest of json is cwf json object
    
}
def patientQuestionWF (args):
	print 'patientQuestionWF args', args
	cref = args['_id']
	user = args['user']
	
	failureResult = { 'result' : 'Failure', 'message' : '' }
	successResult = {'result' : 'Success', 'message' : '','reference':'' }

	#
	try:
		cwf = queryAPI.findConsultationWFById(int(cref))
	except:
		failureResult['message'] = 'Invalid Reference - ' + str(cref)
		return failureResult

	if (cwf == None):
		failureResult['message'] = 'Invalid CWF Reference - ' + str(cref)
		return failureResult

	# check that cwf was initiated by this same user
	if(cwf.user.id() != user.key.id()):
		failureResult['message'] = 'Invalid Appointment Request. C-Ref belongs to another user'
		return failureResult

	# cwf.patientDetailsWF.questionId = []
	# cwf.patientDetailsWF.answerText = []

	# for k in sorted(args.keys()):
	# 	if (k != 'cref' and k != 'reference' and k != 'user'):
	# 		cwf.patientDetailsWF.questionId.append (k)
	# 		cwf.patientDetailsWF.answerText.append (args[k])

	# reset all existing answers, if there are any, but leave the first one because it is summary of the appointment
	cwf.patientDetailsWF.answerText[1:] = []
	for i in range(len(args['patientDetailsWF']['answerText'][1:])):
		# print 'qkey'+str(i+1), args['patientDetailsWF']['answerText'][i+1]
		cwf.patientDetailsWF.questionId.append ('qkey'+str(i+1))
		cwf.patientDetailsWF.answerText.append (args['patientDetailsWF']['answerText'][i+1])		


	# In-Progress
	# cwf.overallStatus = 2

	cwf.put()

	successResult['message'] = 'Patient Questionnaire Information Stored'
	successResult['reference'] = cwf.key.id()
	successResult['cwf'] = ndb_json.dumps(cwf)
	return successResult


def getRecentAppointmentsForUser (args):

	user = args['user']


	failureResult = { 'result' : 'Failure', 'message' : '' }
	successResult = {'result' : 'Success', 'message' : '','reference':'' }

	#
	try:
		userId = user.key.id()
		appts = queryAPI.findConsultationByUserId(user.key.id())
	except Exception as ex:
		print 'exception raised is ', ex
		failureResult['message'] = 'Invalid user - ' + str(userId)
		return failureResult


	return ndb_json.dumps(appts)

def getFavoriteProviderProfilesForUser (args):

	user = args['user']


	failureResult = { 'result' : 'Failure', 'message' : '' }
	successResult = {'result' : 'Success', 'message' : '','reference':'' }

	#
	try:
		userId = user.key.id()
		appts = queryAPI.findConsultationByUserId(user.key.id())
		allProviderIds = []
		for x in appts:
			allProviderIds.append(x.provider.id())
		# remove the duplicates
		seen = set()
		seen_add = seen.add
		uniqueProviderIds =  [x for x in allProviderIds if not (x in seen or seen_add(x))]
		# uniqueProviderIds = allProviderIds # list(OrderedDict.fromkeys(allProviderIds))
		# favoriteProfiles = queryAPI.findProfilesByGivenProviderIds(uniqueProviderIds)
		favoriteProviders = queryAPI.getProvidersByProviderIds(uniqueProviderIds)
		print ' favorites profiles fetched in a dumb synchronous way. fix it'
		return ndb_json.dumps(favoriteProviders)

	except Exception as ex:
		print 'exception raised is ', ex
		failureResult['message'] = 'Invalid user - ' + str(userId)
		return failureResult

	
	

	

def getRecentAppointmentsForProvider (args):

	provider = args['user']


	failureResult = { 'result' : 'Failure', 'message' : '' }
	successResult = {'result' : 'Success', 'message' : '','reference':'' }

	#
	try:
		providerId = provider.key.id()
		appts = queryAPI.findConsultationByProviderId(provider.key.id())
	except Exception as ex:
		print 'exception raised is ', ex
		failureResult['message'] = 'Invalid provider - ' + str(providerId)
		return failureResult


	return ndb_json.dumps(appts)


def getConsultWF (args):
	cref = args['cref'];
	user = args['user']

	failureResult = { 'result' : 'Failure', 'message' : '' }
	#successResult = {'result' : 'Success', 'message' : '','reference':'' }

	#
	try:
		cwf = queryAPI.findConsultationWFById(int(cref))
	except:
		failureResult['message'] = 'Invalid Reference - ' + str(cref)
		return failureResult

	if (cwf == None):
		failureResult['message'] = 'Invalid CWF Reference - ' + str(cref)
		return failureResult

	# check that cwf was initiated by this same user
	if(cwf.user.id() != user.key.id() and cwf.provider.id() != user.key.id()):
		failureResult['message'] = 'Invalid Appointment Request. C-Ref belongs to another user'
		return failureResult

	successResult = ndb_json.dumps(cwf)
	#successResult['result'] = 'Success'
	return successResult


def consultWF_setApptState(args):
	cref = args['cref']
	user = args['user']
	aptWFCd = args['aptWFCd']

	failureResult = { 'result' : 'Failure', 'message' : '' }
	#successResult = {'result' : 'Success', 'message' : '','reference':'' }

	#
	try:
		cwf = queryAPI.findConsultationWFById(int(cref))
	except:
		failureResult['message'] = 'Invalid Reference - ' + str(cref)
		return failureResult

	if (cwf == None):
		failureResult['message'] = 'Invalid CWF Reference - ' + str(cref)
		return failureResult

	# check that cwf was initiated by this same user
	if(cwf.user.id() != user.key.id() and cwf.provider.id() != user.key.id() ):
		failureResult['message'] = 'Invalid Appointment Request. C-Ref belongs to another user/provider'
		return failureResult


	# def rescheduleByProvider():
	# 	rescheduleDt = args['rescheduleDt']
	# 	reason = args['reason']
	# 	cwf.apptWF.rescheduleTimeByProvider(rescheduleDt, reason)


	stateMap = {3:"confirmTimeByProvider",30:"confirmTimeByUser", 4: "rescheduleTimeByUser", 5: "rescheduleTimeByProvider", 6: "cancelByUser", 7: "cancelByProvider"}

	if(aptWFCd not in stateMap):
		failureResult['message'] = 'Invalid workflow state - '+ str(aptWFCd)
		return failureResult

	# rescheduleDtIfProvided = args['rescheduledDt'] 
	# reasonIfProvided = args['reason']
	rescheduleDtIfProvided = args.get('rescheduledDt', None) 
	reasonIfProvided = args.get('reason', None)

	print 'statemap/aptWFCd', aptWFCd, stateMap[aptWFCd], cwf

	if(cwf.apptWF == None):
		# delete this junk(unfinished) appointment
		cwf.key.delete()
		return {'result' : 'Success', 'message' : 'Unfinished Appointment Deleted','reference':cref }

	statusAction = getattr(cwf.apptWF, stateMap[aptWFCd])

	
	
	if(statusAction != None):
		getattr(cwf.apptWF, stateMap[aptWFCd])(reasonIfProvided, rescheduleDtIfProvided )
	else:
		# appt wf object does not exist so we just junk it now.
		pass
	cwf.put()

	if(aptWFCd == 3 or aptWFCd == 5):
		dispatcher.sendSMSToUser(cref, aptWFCd)
	elif(aptWFCd == 4):
		dispatcher.sendSMSToProvider(cref, aptWFCd)


	successResult = ndb_json.dumps(cwf)
	#successResult['result'] = 'Success'
	return successResult

def consultWF_updatePayment(args):
	# secretWord = 'MjRiZmYxZjQtZjcwZi00NDE3LWIzOWEtODUwMGFmOWFkYWJj'
	secretWord = 'MDdlOWJlZmYtOTUzMS00OTRhLTgzOGMtYmIzZDFiMzlkZjU1'
	# accountNo = '901274976'
	accountNo = '901307406'
	key = args['key']
	order_number = args['order_number']
	demo_order_no =  '1'
	invoice_id = args['invoice_id']
	paymentProcessed = args['credit_card_processed']
	total = args['total']
	cref = args['li_0_product_id']

	m = hashlib.md5()
	m.update(secretWord)
	m.update(accountNo)
	# change it to use actual order number
	m.update(demo_order_no)
	m.update(total)

	# calculatedKey = m.digest()
	calculatedKey2 = m.hexdigest().upper()

	print 'payment key', key, 'calculatedKey as digest', calculatedKey2

	failureResult = { 'result' : 'Failure', 'message' : '' }
	successResult = {'result' : 'Success', 'message' : '','reference':'' }

	if(key != calculatedKey2):
		failureResult['message'] = 'Invalid payment update for cref ' + str(cref) +', order no '+ str(order_number)+ ', invoice_id '+ str(invoice_id)
		return failureResult

	#
	try:
		cwf = queryAPI.findConsultationWFById(int(cref))
	except:
		failureResult['message'] = 'Invalid Cref on receiving payment confirmation - ' + str(cref)
		# todo - log the payment handback errors
		return failureResult

	if (cwf == None):
		failureResult['message'] = 'Invalid CWF Reference in payment processing handback - ' + str(cref)
		return failureResult

	if not cwf.paymentWF:
		cwf.paymentWF = subscriber.PaymemtWF()	

	cwf.paymentWF.totalPaidAmount = float(total)

	if not cwf.paymentWF.paymentConfirmToken:
		cwf.paymentWF.paymentConfirmToken = [invoice_id]
	else:
		cwf.paymentWF.paymentConfirmToken.append(invoice_id)

	if cwf.paymentWF.paymentConfirmTS:
		cwf.paymentWF.paymentConfirmTS.append( datetime.datetime.now() )
	else:
		cwf.paymentWF.paymentConfirmTS = [datetime.datetime.now()]

	# 3 = payment_successful, #4 = payment_rejected	
	cwf.paymentWF.paymentStatus = 3 if paymentProcessed == 'Y' else 4	
	paymentProcessed
	if cwf.paymentWF.paymentStatusChain:
		cwf.paymentWF.paymentStatusChain.append( cwf.paymentWF.paymentStatus )
	else:
		cwf.paymentWF.paymentStatusChain = [cwf.paymentWF.paymentStatus]

	cwf.put()

	successResult = {'result' : 'Success', 'message' : 'Payment Processed Recorded','reference': cref }

	return successResult

def create_upload_url(args):
	upload_callback_url = args['upload_callback_url']
	if not args:
		return {'result': 'Failure', 'message': 'Could not create upload url. Required parameters unavailable'}
	cref = args['cref']	
	upload_url = blobstore.create_upload_url(upload_callback_url)
	return {'result' : 'Success', 'message' : 'Upload Url Created','upload_url': upload_url } 


class PrescriptionUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
	def post(self):
		try:
			upload = self.get_uploads()[0]
			user_photo = UserPhoto(user=users.get_current_user().user_id(), blob_key=upload.key())
			user_photo.put()

			self.redirect('/view_photo/%s' % upload.key())

		except:
			self.redirect('/upload_failure.html')

def handlePrescriptionOnUpload(args):
	print 'todo - handle prescription on upload'
	cref = args['cref']
	blobKey = args['blob_key']
	fileName = args['filename']
	

	failureResult = { 'result' : 'Failure', 'message' : '' }
	successResult = {'result' : 'Success', 'message' : '','reference':'' }

	#
	try:
		cwf = queryAPI.findConsultationWFById(int(cref))
	except:
		failureResult['message'] = 'Invalid Cref - ' + str(cref)
		# todo - log the payment handback errors
		return failureResult

	if (cwf == None):
		failureResult['message'] = 'Invalid CWF Reference in prescription upload - ' + str(cref)
		return failureResult

	prescriptionDocument = subscriber.PrescriptionDoc()	
	prescriptionDocument.fileBlobKey = blobKey
	prescriptionDocument.fileName = fileName
	if not cwf.fullfillmentWF:
		cwf.fullfillmentWF = subscriber.FulfillmentWF()

	if not cwf.fullfillmentWF.prescriptionDocuments:
		cwf.fullfillmentWF.prescriptionDocuments = [prescriptionDocument]
	else:
		cwf.fullfillmentWF.prescriptionDocuments.append(prescriptionDocument)	

	cwf.fullfillmentWF.prescription_ref = blobKey
	cwf.fullfillmentWF.prescriptionTS = datetime.datetime.now()
	cwf.fullfillmentWF.fulfillmentStatus = 3

	cwf.put()
	
	successResult['reference'] = cref
	return successResult

def handleSubscriberDocumentOnUpload(args):
	print 'handle subscriber on upload', args
	cref = args['cref']
	blobKey = args['blob_key']
	documentNo = args['documentNo']
	filename = args['filename']
	filesummary = args['filesummary']

	failureResult = { 'result' : 'Failure', 'message' : '' }
	successResult = {'result' : 'Success', 'message' : '','reference':'' }

	#
	try:
		cwf = queryAPI.findConsultationWFById(int(cref))
	except:
		failureResult['message'] = 'Invalid Cref - ' + str(cref)
		# todo - log the payment handback errors
		return failureResult

	if (cwf == None):
		failureResult['message'] = 'Invalid CWF Reference in prescription upload - ' + str(cref)
		return failureResult

	patientDocument = subscriber.SubscriberDoc()
	patientDocument.fileBlobKey = blobKey
	patientDocument.fileName = filename
	patientDocument.fileSummary = filesummary
	if not cwf.patientDetailsWF.patientDocuments:
		cwf.patientDetailsWF.patientDocuments = [patientDocument]
	else:
		cwf.patientDetailsWF.patientDocuments.append(patientDocument)	
	
	cwf.put()
	
	successResult['reference'] = cref
	return successResult

def getSubscriptionDocByBlobKey(cref, blobkey):
	failureResult = { 'result' : 'Failure', 'message' : '' }
	successResult = {'result' : 'Success', 'message' : '','reference':'' }

	#
	try:
		cwf = queryAPI.findConsultationWFById(int(cref))
	except:
		failureResult['message'] = 'Invalid Cref - ' + str(cref)
		# todo - log the payment handback errors
		return failureResult

	if (cwf == None):
		failureResult['message'] = 'Invalid CWF Reference in prescription upload - ' + str(cref)
		return failureResult

	return cwf.patientDetailsWF.getDocument(blobkey)

def getPrescriptionDocByBlobKey(cref, blobkey):
	failureResult = { 'result' : 'Failure', 'message' : '' }
	successResult = {'result' : 'Success', 'message' : '','reference':'' }

	#
	try:
		cwf = queryAPI.findConsultationWFById(int(cref))
	except:
		failureResult['message'] = 'Invalid Cref - ' + str(cref)
		# todo - log the payment handback errors
		return failureResult

	if (cwf == None):
		failureResult['message'] = 'Invalid CWF Reference in prescription download - ' + str(cref)
		return failureResult

	return cwf.fullfillmentWF.getDocument(blobkey)	



def processCwfEvent(args):
	eventName = args['eventName']
	# eventBody = args['eventBody']
	user = args['user']

	if(eventName == 'RescheduleByProvider'):
		args['rescheduledDt'] = dateutil.parser.parse(args['reschedDT']).replace(tzinfo=None)
		args['reason'] = args['reschedMsg']
		args['aptWFCd'] = 5
		consultWF_setApptState(args)
		return { 'result' : 'Success', 'message' : 'Reschedule request completed ', 'cref' : args['cref'] }
	elif(eventName == 'RescheduleByUser'):
		args['rescheduledDt'] = dateutil.parser.parse(args['reschedDT']).replace(tzinfo=None)
		args['reason'] = args['reschedMsg']
		args['aptWFCd'] = 4
		consultWF_setApptState(args)
		return { 'result' : 'Success', 'message' : 'Reschedule request completed ', 'cref' : args['cref'] }
	elif(eventName == 'ConfirmByUser'):
		args['aptWFCd'] = 30
		consultWF_setApptState(args)
		return { 'result' : 'Success', 'message' : 'Appointment Confirmation completed ', 'cref' : args['cref'] }
	else:
		# see if we have a method in this module matching the eventName. if yes, invoke it
		handlerFn = getattr(sys.modules[__name__], eventName, None)
		if(handlerFn):
			return handlerFn(args)
		else:
			return { 'result' : 'Failure', 'message' : 'Unknown Event - '+eventName }

	return { 'result' : 'Failure', 'message' : 'Unknown Event - '+eventName }


def changePatientInfo(args):
	# print 'todo - implement change patient info'
	# return { 'result' : 'Failure', 'message' : 'implementing change patient info shortly' }	

	cref = args['cref'];
	patientName = args['patientName']
	patientAge = args['patientAge']
	patientSex = args['patientSex']
	patientPhone = args['patientPhone']
	consultationModePreference = args['consult_mode_pref']
	problemSummary = args['problemSummary']
	user = args['user']

	failureResult = { 'result' : 'Failure', 'message' : '' }
	successResult = {'result' : 'Success', 'message' : '','reference':'' }

	#
	try:
		cwf = queryAPI.findConsultationWFById(cref)
	except:
		failureResult['message'] = 'Invalid Reference - ' + str(cref)
		return failureResult

	# check that cwf was initiated by this same user
	if(cwf.user.id() != user.key.id()):
		failureResult['message'] = 'Invalid Appointment Request. C-Ref belongs to another user'
		return failureResult

	# allow the patient info change only before the meeting, not after the meeting
	if(cwf.meetingWF == None):
		failureResult['message'] = 'Invalid CWF/Meeting State '+str(cref)
		return failureResult

	if(cwf.patientDetailsWF == None):
		failureResult['message'] = 'Invalid CWF/PatientDetails State '+str(cref)
		return failureResult

	if(cwf.meetingWF.meetingStatus >= 3):
		failureResult['message'] = 'Cannot change patient details after the meeting '+str(cref)
		return failureResult

	if(cwf.overallStatus >= 3):
		failureResult['message'] = 'Cannot change patient details after the consultation is complete '+str(cref)
		return failureResult


	
	cwf.patientDetailsWF.patientName = patientName
	cwf.patientDetailsWF.patientAge = patientAge
	cwf.patientDetailsWF.patientSex = patientSex
	cwf.patientDetailsWF.patientPhone = patientPhone
	cwf.patientDetailsWF.answerText[0] = problemSummary

	cwf.meetingWF.meetingType = consultationModePreference
	cwf.put()
	return { 'result' : 'Success', 'message' : 'Patient info change completed ', 'cref' : cref }


def forcePaymentComplete(args):
	cref = args['cref'];
	paidAmount = args['paidAmount']
	paymentRef = args['paymentRef']

	try:
		cwf = queryAPI.findConsultationWFById(int(cref))
	except:
		failureResult['message'] = 'Invalid Cref to force payment - ' + str(cref)
		# todo - log the payment handback errors
		return failureResult

	if (cwf == None):
		failureResult['message'] = 'Invalid CWF Reference in force payment processing - ' + str(cref)
		return failureResult


	if not cwf.paymentWF:
		cwf.paymentWF = subscriber.PaymemtWF()	

	cwf.paymentWF.totalPaidAmount = float(paidAmount)

	if not cwf.paymentWF.paymentConfirmToken:
		cwf.paymentWF.paymentConfirmToken = [paymentRef]
	else:
		cwf.paymentWF.paymentConfirmToken.append(paymentRef)

	if cwf.paymentWF.paymentConfirmTS:
		cwf.paymentWF.paymentConfirmTS.append( datetime.datetime.now() )
	else:
		cwf.paymentWF.paymentConfirmTS = [datetime.datetime.now()]

	# 3 = payment_successful, #4 = payment_rejected	
	cwf.paymentWF.paymentStatus = 3 
	if cwf.paymentWF.paymentStatusChain:
		cwf.paymentWF.paymentStatusChain.append( cwf.paymentWF.paymentStatus )
	else:
		cwf.paymentWF.paymentStatusChain = [cwf.paymentWF.paymentStatus]

	cwf.put()
	return { 'result' : 'Success', 'message' : 'Payment force completed', 'cref' : cref }


def applyPaymentCoupon(args):
	cref = args['cref'];
	couponCode = args['couponCode']

	failureResult = { 'result' : 'Failure', 'message' : '' }

	try:
		cwf = queryAPI.findConsultationWFById(int(cref))
	except:
		failureResult['message'] = 'Invalid Cref. Unable to apply coupon. ' + str(cref)
		# todo - log the payment handback errors
		return failureResult

	if (cwf == None):
		failureResult['message'] = 'Invalid CWF Reference. Cannot apply coupon - ' + str(cref)
		return failureResult

	# for now, I am hardcoding the payment to be completed on any coupon value, but...
	# todo - first fetch the coupon object
	# check that the coupon is valid and has not expired
	# also fetch what is the value of the coupon
	# now subtract the expected money with the coupon value
	# if the expected money is now zero or less than zero, update the 
	# payment status as successful and return appropriate response
	# so that the browser can take the user past the payment page
	# 
	couponObj = subscriber.PaymentCouponStruc()
	couponObj.couponProvider = "RemedySquare"
	couponObj.couponCode = "PRE-LAUNCH"
	couponObj.couponValue = 500.0
	until30Days = datetime.timedelta(days=30)
	couponObj.couponValidUntil = datetime.datetime.now() + until30Days
	
	if not couponCode=='PRE-LAUNCH':
		failureResult['message'] = 'Invalid Coupon Code. Cannot apply coupon - ' + str(couponCode)
		return failureResult



	if not cwf.paymentWF:
		cwf.paymentWF = subscriber.PaymemtWF()	

	adjustedExpectedAmount = cwf.paymentWF.applyCoupon(couponObj)
	# check the expected amount now, after applying coupon
	if(adjustedExpectedAmount > 0.0):
		pass
	else:
		cwf.paymentWF.paymentProviderId = hmpconstants.PaymentProvider.REMEDY_SQUARE
		cwf.paymentWF.totalPaidAmount = 0.0
		if not cwf.paymentWF.paymentConfirmToken:
			cwf.paymentWF.paymentConfirmToken = [couponObj.couponCode]
		else:
			cwf.paymentWF.paymentConfirmToken.append(couponObj.couponCode)

		if cwf.paymentWF.paymentConfirmTS:
			cwf.paymentWF.paymentConfirmTS.append( datetime.datetime.now() )
		else:
			cwf.paymentWF.paymentConfirmTS = [datetime.datetime.now()]

		# 3 = payment_successful, #4 = payment_rejected	
		cwf.paymentWF.paymentStatus = 3 
		if cwf.paymentWF.paymentStatusChain:
			cwf.paymentWF.paymentStatusChain.append( cwf.paymentWF.paymentStatus )
		else:
			cwf.paymentWF.paymentStatusChain = [cwf.paymentWF.paymentStatus]

	cwf.put()
	return { 'result' : 'Success', 'message' : 'Coupon applied', 'cref' : cref, 'expected_payment' : adjustedExpectedAmount }


def markMeetingAsComplete(args):
	print 'markConsultationAsComplete impl method'
	# return { 'result' : 'Failure', 'message' : 'implementing change patient info shortly' }	

	cref = args['cref']
	user = args['user']

	failureResult = { 'result' : 'Failure', 'message' : '' }
	successResult = {'result' : 'Success', 'message' : '','reference':'' }

	#
	try:
		cwf = queryAPI.findConsultationWFById(cref)
	except:
		failureResult['message'] = 'Invalid Reference - ' + str(cref)
		return failureResult

	# check that cwf was initiated by this same user
	if(cwf.provider.id() != user.key.id()):
		failureResult['message'] = 'Invalid Meeting Complete Request. C-Ref belongs to another doctor'
		return failureResult

	# allow the completion only if meetingWF exists
	if(cwf.meetingWF == None):
		failureResult['message'] = 'Invalid CWF/Meeting State '+str(cref)
		return failureResult

	# set meetingWF status to complete
	cwf.meetingWF.meetingStatus = 3
	cwf.put()

	return { 'result' : 'Success', 'message' : 'Meeting Completed ', 'cref' : cref }

def markConsultationAsComplete(args):
	print 'markConsultationAsComplete impl method'
	# return { 'result' : 'Failure', 'message' : 'implementing change patient info shortly' }	

	cref = args['cref']
	user = args['user']

	failureResult = { 'result' : 'Failure', 'message' : '' }
	successResult = {'result' : 'Success', 'message' : '','reference':'' }

	#
	try:
		print 'cref is', cref
		cwf = queryAPI.findConsultationWFById(int(cref))
		print 'cwf with cref', cwf
	except:
		failureResult['message'] = 'Invalid Reference - ' + str(cref)
		return failureResult

	# check that cwf was initiated by this same user
	if(cwf.user.id() != user.key.id()):
		failureResult['message'] = 'Invalid Consultation Complete Request. C-Ref belongs to another doctor'
		return failureResult

	# delete this consultation if apptWF, paymentWF, meetingWF etc does not exist
	if(cwf.meetingWF == None and cwf.apptWF == None and cwf.paymentWF == None and cwf.patientDetailsWF == None):
		cwf.key.delete()
		return {'result' : 'Success', 'message' : 'Unfinished Appointment Deleted','reference':cref }

	
	# set overall status to complete
	cwf.overallStatus = 3
	cwf.put()

	return { 'result' : 'Success', 'message' : 'Consultation Completed ', 'cref' : cref }



