from model import subscriber, queryAPI, ndb_json
import dateutil.parser

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
	cwf.apptWF.requestedTS = dateutil.parser.parse(requestTSStr)
	cwf.apptWF.confirmedTS = dateutil.parser.parse(requestTSStr)
	cwf.apptWF.apptStatusChain = [2,3]
	cwf.apptWF.apptStatus = 3


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

	cwf.patientDetailsWF.questionId = []
	cwf.patientDetailsWF.answerText = []

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
	if(cwf.user.id() != user.key.id()):
		failureResult['message'] = 'Invalid Appointment Request. C-Ref belongs to another user'
		return failureResult

	successResult = ndb_json.dumps(cwf)
	#successResult['result'] = 'Success'
	return successResult




	


