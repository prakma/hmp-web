import json
from model import feedback, queryAPI, ndb_json

def createFeedbackEntry(feedbackJSON):
	print 'json input is ', feedbackJSON
	failure_rs = {
		"result" : "Failure",
		"code" : 'S4001',
		"message" : 'Unrecognized Subscriber'
		}
	success_rs = {
		"result" : "Success",
		"code" : 'S2001',
		"message" : 'Feedback Created',
		"_id" : ''
		}
	
		
	fbObj = feedback.GeneralFeedback ()
	fbObj.name = feedbackJSON['name']
	fbObj.subject = feedbackJSON['subject']
	fbObj.body = feedbackJSON['body']
	if('_id' in feedbackJSON):
		# it is some reply feedback
		fbObj.setParent(feedbackJSON['_id'])
	
	pk = fbObj.put()
	success_rs['_id'] = pk.id()

	return success_rs

def getFeedback(feedbackId):
	if(feedbackId == None):
		rs = {
		"result" : "Failure",
		"code" : 'S4001',
		"message" : 'No known feedback '+str(feedbackId)
		}
		return rs
	else:

		feedback = queryAPI.findFeedbackById(int(feedbackId))
		return ndb_json.dumps(feedback)
		

