from google.appengine.ext import ndb
from subscriber import Subscriber
import datetime


class FeeStruct(ndb.Model):
	baseCurrency = ndb.StringProperty()
	regularFee = ndb.IntegerProperty()
	followupFee = ndb.IntegerProperty()
	followupDuration = ndb.StringProperty()
	firstTimeFee = ndb.IntegerProperty()
	platformFee = ndb.IntegerProperty()

	def updateWithJSONInput(self, argsJSON):
		temp = argsJSON # ['feeStruc']
		self.baseCurrency = temp['baseCurrency']
		self.regularFee = temp['regularFee']
		self.followupFee = temp['followupFee']
		self.followupDuration = temp['followupDuration']
		# self.firstTimeFee = temp['firstTimeFee']
		self.platformFee = temp['platformFee']


class CalendarStruct(ndb.Model):
	mon = ndb.StringProperty()
	tue = ndb.StringProperty()
	wed = ndb.StringProperty()
	thu = ndb.StringProperty()
	fri = ndb.StringProperty()
	sat = ndb.StringProperty()
	sun = ndb.StringProperty()
	exc = ndb.StringProperty() # exceptions

	def updateWithJSONInput(self, argsJSON):
		temp = argsJSON #['calStruc']
		self.mon = temp['mon']
		self.tue = temp['tue']
		self.wed = temp['wed']
		self.thu = temp['thu']
		self.fri = temp['fri']
		self.sat = temp['sat']
		self.sun = temp['sun']
		if 'exc' in argsJSON:
			self.exc = temp['exc']
		

class GenericStruct(ndb.Model):
	strucKeyword = ndb.StringProperty()
	strucHead = ndb.StringProperty()
	strucDesc = ndb.StringProperty()
	strucFoot = ndb.StringProperty()
	strucValues = ndb.StringProperty(repeated=True)

	def updateWithJSONInput(self, argsJSON):
		self.strucKeyword = argsJSON['strucKeyword']
		if 'strucHead' in argsJSON:
			self.strucHead = argsJSON['strucHead']

		if 'strucDesc' in argsJSON:
			self.strucDesc = argsJSON['strucDesc']

		if 'strucFoot' in argsJSON:
			self.strucFoot = argsJSON['strucFoot']

		if 'strucValues' in argsJSON:
			self.strucValues = argsJSON['strucValues']



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
	calStruc = ndb.StructuredProperty(CalendarStruct)
	servicesOffered = ndb.StringProperty(repeated=True)
	feeStructure = ndb.StringProperty(repeated=True)
	feeStruc = ndb.StructuredProperty(FeeStruct)

	education = ndb.StructuredProperty(GenericStruct)
	registration = ndb.StructuredProperty(GenericStruct)
	membership = ndb.StructuredProperty(GenericStruct)
	awardsRecognitions = ndb.StructuredProperty(GenericStruct)
	experience = ndb.StructuredProperty(GenericStruct)

	lastUpdatedTS = ndb.DateTimeProperty(auto_now=True)

	def updateWithJSONInput(self, argsJSON):
		self.lastUpdatedTS = datetime.datetime.now()
		self.name = argsJSON['name']
		# self.degree = argsJSON['degree']
		self.oneLiner = argsJSON['oneLiner']
		self.profileDesc = argsJSON['profileDesc']
		self.specialty = argsJSON['specialty']
		self.genLocation = argsJSON['genLocation']
		# self.timing = argsJSON['timing']
		self.servicesOffered = argsJSON['servicesOffered']
		# self.feeStructure = argsJSON['feeStructure']

		# calendar structure
		if('calStruc' in argsJSON):
			self.calStruc = CalendarStruct()
			self.calStruc.updateWithJSONInput(argsJSON['calStruc'])

		# fee structure
		if('feeStruc' in argsJSON):
			self.feeStruc = FeeStruct()
			self.feeStruc.updateWithJSONInput(argsJSON['feeStruc'])

		# education
		if('education' in argsJSON):
			self.education = GenericStruct()
			self.education.updateWithJSONInput(argsJSON['education'])

		# registration
		if('registration' in argsJSON):
			self.registration = GenericStruct()
			self.registration.updateWithJSONInput(argsJSON['registration'])

		# membership
		if('membership' in argsJSON):
			self.membership = GenericStruct()
			self.membership.updateWithJSONInput(argsJSON['membership'])

		# awardsRecognitions
		if('awardsRecognitions' in argsJSON):
			self.awardsRecognitions = GenericStruct()
			self.awardsRecognitions.updateWithJSONInput(argsJSON['awardsRecognitions'])

		# experience
		if('experience' in argsJSON):
			self.experience = GenericStruct()
			self.experience.updateWithJSONInput(argsJSON['experience'])

	

