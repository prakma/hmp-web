from google.appengine.api import taskqueue

def sendSMSToUser(cref, apptWFStateCd):
	# taskqueue.add(url='/s/wh/sendSMS2U', params={'cref': cref, 'apptWFStateCd':apptWFStateCd}, countdown=1)
	return

def sendSMSToProvider(cref, apptWFStateCd):
	# taskqueue.add(url='/s/wh/sendSMS2P', params={'cref': cref, 'apptWFStateCd':apptWFStateCd}, countdown=1)
	return

