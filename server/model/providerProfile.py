from google.appengine.ext import ndb
from subscriber import Subscriber
import datetime

# name, degree[], oneliner, profileSummary, specialty, location[], geocode, timing[], servicesOffered[], feeStructure[]
class PbProfile(ndb.Model):
	subscriber = ndb.KeyProperty(kind=Subscriber)
	name = ndb.StringProperty()
	degree = ndb.StringProperty(repeated=True)
	oneLiner = ndb.StringProperty()
	profileDesc = ndb.StringProperty(repeated=True)
	specialty = ndb.StringProperty(repeated=True)
	geoLocation = ndb.GeoPtProperty()
	genLocation = ndb.StringProperty(repeated=True)
	timing = ndb.StringProperty(repeated=True)
	servicesOffered = ndb.StringProperty(repeated=True)
	feeStructure = ndb.StringProperty(repeated=True)
	lastUpdatedTS = ndb.DateTimeProperty(auto_now=True)

	def updateWithJSONInput(self, argsJSON):
		self.lastUpdatedTS = datetime.datetime.now()
		self.name = argsJSON['name']
		self.degree = argsJSON['degree']
		self.oneLiner = argsJSON['oneLiner']
		self.profileDesc = argsJSON['profileDesc']
		self.specialty = argsJSON['specialty']
		self.genLocation = argsJSON['genLocation']
		self.timing = argsJSON['timing']
		self.servicesOffered = argsJSON['servicesOffered']
		self.feeStructure = argsJSON['feeStructure']
	

