from model import subscriber, queryAPI, ndb_json
import dateutil.parser
import datetime
import hashlib
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

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
    'requestedTS': '',
    'problemSummary': ''
}
def apptRequestWF (args):
	cref = args['cref'];
	patientName = args['patientName']
	patientAge = args['age']
	patientSex = args['sex']
	requestTSStr = args['requestedTS']
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
	cwf.patientDetailsWF.questionId = ['Summary']
	cwf.patientDetailsWF.answerText = [problemSummary]

	cwf.statusWF = subscriber.StatusWF()
	cwf.statusWF.overallStatusChain = [1]
	cwf.statusWF.overallStatus = 1 

	# In-Progress
	cwf.overallStatus = 2

	cwf.put()
	successResult['message'] = 'Consultation request sent to Doctor. Waiting for his confirmation'
	successResult['reference'] = cwf.key.id()
	successResult['cwf'] = ndb_json.dumps(cwf)
	return successResult


patientq_args = {
    'cref': '',
    'qkey':'',
    'qtext':''
}
def patientQuestionWF (args):
	cref = args['cref'];
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

	for k in sorted(args.keys()):
		if (k != 'cref' and k != 'reference' and k != 'user'):
			cwf.patientDetailsWF.questionId.append (k)
			cwf.patientDetailsWF.answerText.append (args[k])		


	# In-Progress
	cwf.overallStatus = 2

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


	stateMap = {3:"confirmTimeByProvider", 4: "rescheduleByUser", 5: "rescheduleTimeByProvider", 6: "cancelByUser", 7: "cancelByProvider"}

	if(aptWFCd not in stateMap):
		failureResult['message'] = 'Invalid workflow state - '+ str(aptWFCd)
		return failureResult

	rescheduleDtIfProvided = args['rescheduledDt'] 
	reasonIfProvided = args['reason']
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

	successResult = ndb_json.dumps(cwf)
	#successResult['result'] = 'Success'
	return successResult

def consultWF_updatePayment(args):
	secretWord = 'MjRiZmYxZjQtZjcwZi00NDE3LWIzOWEtODUwMGFmOWFkYWJj'
	accountNo = '901274976'
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

	calculatedKey = m.digest()

	print 'payment key', key, 'calculatedKey', calculatedKey

	failureResult = { 'result' : 'Failure', 'message' : '' }
	successResult = {'result' : 'Success', 'message' : '','reference':'' }

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

	cwf.paymentWF.basicAmount = float(total)

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
		cwf.paymentWF.paymentStatusChain.append( datetime.datetime.now() )
	else:
		cwf.paymentWF.paymentStatusChain = [cwf.paymentWF.paymentStatus]

	cwf.put()

	successResult = {'result' : 'Success', 'message' : 'Payment Processed Recorded','reference': cref }

	return successResult

def create_upload_url(args):
	prescription_url = args['prescription_url']
	if not args:
		return {'result': 'Failure', 'message': 'Could not create upload url. Required parameters unavailable'}
	cref = args['cref']	
	upload_url = blobstore.create_upload_url(prescription_url)
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

	if not cwf.fullfillmentWF:
		cwf.fullfillmentWF = subscriber.FulfillmentWF()

	cwf.fullfillmentWF.prescription_ref = blobKey
	cwf.fullfillmentWF.prescriptionTS = datetime.datetime.now()
	cwf.fullfillmentWF.fulfillmentStatus = 1

	cwf.put()
	
	successResult['reference'] = cref
	return successResult	



	




	


