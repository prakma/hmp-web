from google.appengine.ext import ndb
from subscriber import Subscriber
import datetime

# name, degree[], oneliner, profileSummary, specialty, location[], geocode, timing[], servicesOffered[], feeStructure[]
class GeneralFeedback(ndb.Model):
	subscriber = ndb.KeyProperty(kind=Subscriber)
	subject = ndb.StringProperty()
	name = ndb.StringProperty()
	body = ndb.StringProperty()	
	lastUpdatedTS = ndb.DateTimeProperty(auto_now=True)
	parent = ndb.KeyProperty(kind='GeneralFeedback')

	def setParent(self, parentFeedbackId):
		parentKey = ndb.Key('GeneralFeedback', parentFeedbackId)
		self.parent = parentKey
