from google.appengine.ext import ndb
import datetime
import hashlib

class Subscriber(ndb.Model):
	email = ndb.StringProperty(repeated=True)
	passwd = ndb.StringProperty()
	handle = ndb.StringProperty()
	name = ndb.StringProperty()
	phone = ndb.StringProperty(repeated=True)
	providerFlag = ndb.BooleanProperty(default=False)
	subscribeOrigCreateDate = ndb.DateTimeProperty(auto_now_add=True)
	subscribeStartDate = ndb.DateTimeProperty()
	subscribeEndDate = ndb.DateTimeProperty()
	lastUpdatedTS = ndb.DateTimeProperty(auto_now=True)
	# 1 = create, 2 = activated, 3 = suspended, 4 = terminated
	subscribeStatus = ndb.IntegerProperty(default=1)
	primaryLocation = ndb.GeoPtProperty()
	primaryLocationStr = ndb.StringProperty()
	subscriptionConfig = ndb.JsonProperty()

	# def __init__(self, *args, **kwargs):
	# 	super(Subscriber, self).__init__(**kwargs)
	# 	# self.email = []
	# 	# self.phone = []

	def __setattr__(self, name, value):
		if (name == 'email'):
				self.email.append(value)
		elif (name == 'phone'):
				if(value != None):
					self.phone.append(value)
		elif (name == 'passwd'):
			m = hashlib.sha1()
			m.update(value)
			super(Subscriber, self).__setattr__(name, m.hexdigest().upper())
		else:
			super(Subscriber, self).__setattr__(name,value)

	def checkPassword (self, p):
		m = hashlib.sha1()
		m.update(p)
		return (self.passwd == m.hexdigest().upper() )

	def isProvider(self):
		return self.providerFlag != None and self.providerFlag== True

	def clearAllPhoneValues(self):
		super(Subscriber, self).__setattr__('phone', [])


class SubscriberSession(ndb.Model):
	subscriber = ndb.KeyProperty(kind=Subscriber)
	sessionToken = ndb.StringProperty()
	sessionStartTS = ndb.DateTimeProperty()
	sessionEndTS = ndb.DateTimeProperty()
	lastRefreshedTS = ndb.DateTimeProperty(auto_now=True)
	accessCount = ndb.IntegerProperty(default=0)
	# 1 = active, 2 = loggedOut, 3 = forcedOut, 4 = abandoned
	sessionStatus = ndb.IntegerProperty(default=1)

	def incrementAccessCount (self):
		self.accessCount = self.accessCount + 1
		self.lastRefreshedTS = datetime.datetime.now()

	def retire (self, status):
		thisTimeNow = datetime.datetime.now()
		self.lastRefreshedTS = thisTimeNow
		self.sessionStatus = status
		self.sessionEndTS = thisTimeNow

	def logout (self):
		self.retire (2)

	def terminate (self):
		self.retire (3)

	def abandon (self):
		self.retire (4)






# appt_requested, appt_confirmed, appt_reschedule_requested, appt_reschedule_confirmed, appt_canceled
class ApptWF(ndb.Model):
	requestedTS = ndb.DateTimeProperty()
	proposedTS = ndb.DateTimeProperty()
	confirmedTS = ndb.DateTimeProperty()
	confirmedTS_chain = ndb.DateTimeProperty(repeated=True)
	apptStatusChain = ndb.IntegerProperty(repeated=True)
	# 1 = not started, 2 = requested, 3 = confirmed , 4 = new time rescheduled by user, 5 = new time proposed by provider, 6 = canceled by user, 7 = canceled by provider, 8 = abandoned by user
	apptStatus = ndb.IntegerProperty(default=1)
	reasonChain = ndb.StringProperty(repeated=True)

	def confirmTimeByProvider(self, *args, **kwargs):
		self.confirmedTS = self.requestedTS
		self.confirmedTS_chain.append(self.confirmedTS)
		self.apptStatus = 3
		self.apptStatusChain.append(3)

	def confirmTimeByUser(self, *args, **kwargs):
		self.confirmedTS = self.proposedTS
		self.confirmedTS_chain.append(self.confirmedTS)
		self.apptStatus = 3
		self.apptStatusChain.append(3)

	def rescheduleTimeByUser(self, reason, dt):
		self.requestedTS = dt
		self.confirmedTS = dt
		self.apptStatus = 4
		self.apptStatusChain.append(4)
		self.reasonChain.append('U: ' + reason)


	def rescheduleTimeByProvider(self, reason, dt):
		self.proposedTS = dt
		self.apptStatus = 5
		self.apptStatusChain.append(5)
		self.reasonChain.append('P: ' + reason)

	def cancelByUser(self, reason, dt_dummy):
		self.apptStatus = 6
		self.apptStatusChain.append(6)
		if(reason != None):
			self.reasonChain.append('U: ' + reason)

	def cancelByProvider(self, reason, dt_dummy):
		self.apptStatus = 7
		self.apptStatusChain.append(7)
		self.reasonChain.append('P: ' + reason)

class PaymentCouponStruc(ndb.Model):
	couponProvider = ndb.StringProperty()
	couponCode = ndb.StringProperty()
	couponValue = ndb.FloatProperty()
	couponValidUntil = ndb.DateTimeProperty()

	
## payment_info_provided, sent_to_bank, bank_confirmed
class PaymemtWF(ndb.Model):
	# provider expected amount
	prExpAmt = ndb.FloatProperty()

	# platform expected amount
	plExpAmt = ndb.FloatProperty()

	# taxes expected
	txExpAmt = ndb.FloatProperty()

	# total expected
	ttlExpAmt = ndb.FloatProperty()
	additionalPendingCharges = ndb.FloatProperty(repeated=True)

	# coupon code and value
	paymentCoupon = ndb.StructuredProperty(PaymentCouponStruc)


	# expected currency
	expCurr = ndb.StringProperty(default="INR")

	# total paid amount
	totalPaidAmount = ndb.FloatProperty()

	# paid in currency
	paidCurrency = ndb.StringProperty(default="INR")

	paymentProviderId = ndb.StringProperty()
	paymentToken = ndb.StringProperty(repeated=True)
	paymentBeginTS = ndb.DateTimeProperty(repeated=True)
	paymentConfirmToken = ndb.StringProperty(repeated=True)
	paymentConfirmTS = ndb.DateTimeProperty(repeated=True)

	#1=not_initiated, #2 payment_in_process, #3 payment_processed, #4 payment_denied
	paymentStatusChain = ndb.IntegerProperty(repeated=True)
	paymentStatus = ndb.IntegerProperty(default=1)

	def deriveTotalExpectedAmount(self):
		self.ttlExpAmt = self.prExpAmt + self.plExpAmt + self.txExpAmt

	def applyCoupon(self, couponObj):
		self.paymentCoupon = couponObj
		adjustedTotalAmount = self.ttlExpAmt - couponObj.couponValue
		if(adjustedTotalAmount <= 0):
			adjustedTotalAmount = 0
		return adjustedTotalAmount

		# self.ttlExpAmt = adjustedTotalAmount


# docs uploaded by doctor
class PrescriptionDoc(ndb.Model):
	fileName = ndb.StringProperty()
	fileSummary = ndb.StringProperty()
	fileBlobKey = ndb.StringProperty()

# docs uploaded by Patient
class SubscriberDoc(ndb.Model):
	fileName = ndb.StringProperty()
	fileSummary = ndb.StringProperty()
	fileBlobKey = ndb.StringProperty()



## no_info, partial_info, nearly_complete, complete
class PatientDetailsWF(ndb.Model):
	patientName = ndb.StringProperty()
	patientAge = ndb.StringProperty()
	patientSex = ndb.StringProperty()
	patientPhone = ndb.StringProperty()
	#[Summary,]
	questionId = ndb.StringProperty(repeated=True)
	answerText = ndb.StringProperty(repeated=True)
	userDetailsStatus = ndb.IntegerProperty()

	# references of documents uploaded by patients
	patientDocuments = ndb.StructuredProperty(SubscriberDoc, repeated=True)

	def getDocument(self, blobKey):
		if (self.patientDocuments == None):
			return None
		for doc in self.patientDocuments:
			if(blobKey == doc.fileBlobKey):
				return doc
		return None


# checkin, waiting_for_connection, connected, meeting_in_progress, completed, abandoned, no_show, disconnected 
class MeetingWF(ndb.Model):
	# phone, video
	meetingType = ndb.StringProperty()
	userDevice = ndb.StringProperty()
	providerDevice = ndb.StringProperty()
	# meeting_pending, meeting_in_progress, completed, abandoned, no_show, disconnected
	meetingStatus = ndb.IntegerProperty(default=1)
	meetingDelayMinutes = ndb.IntegerProperty()
	meetingDurationMinutes = ndb.IntegerProperty()
	meetingInterruptionMinutes = ndb.IntegerProperty()
	meetingStatusChain = ndb.IntegerProperty(repeated=True)
	

# prescription_sent, prescription_received
class FulfillmentWF(ndb.Model):
	prescription_ref = ndb.StringProperty()
	prescriptionTS = ndb.DateTimeProperty()
	prescriptionDocuments = ndb.StructuredProperty(PrescriptionDoc, repeated=True)
	#1 = prescription uploaded, #3 = fulfillment complete
	fulfillmentStatus = ndb.IntegerProperty()

	def getDocument(self, blobKey):
		if (self.prescriptionDocuments == None):
			return None
		for doc in self.prescriptionDocuments:
			if(blobKey == doc.fileBlobKey):
				return doc
		return None


class StatusWF(ndb.Model):
	# apptStatus = ndb.IntegerProperty()
	# paymentStatus = ndb.IntegerProperty()
	# userDetailsStatus = ndb.IntegerProperty()
	# meetingStatus = ndb.IntegerProperty()
	# fulfillmentStatus = ndb.IntegerProperty()
	overallStatusChain = ndb.IntegerProperty(repeated=True)
	overallStatus = ndb.IntegerProperty()


class ConsultationWF(ndb.Model):
	provider = ndb.KeyProperty(kind=Subscriber)
	providerName = ndb.StringProperty()
	user = ndb.KeyProperty(kind=Subscriber)
	parentConsultation = ndb.KeyProperty(kind='ConsultationWF')
	apptWF = ndb.StructuredProperty(ApptWF)
	paymentWF = ndb.StructuredProperty(PaymemtWF)
	patientDetailsWF = ndb.StructuredProperty(PatientDetailsWF)
	meetingWF = ndb.StructuredProperty(MeetingWF)
	fullfillmentWF = ndb.StructuredProperty(FulfillmentWF)
	statusWF = ndb.StructuredProperty(StatusWF)

	#1. New, 2. In-Progress, 3. Completed, 4. Canceled, 5.Disputed, 6.Closed
	overallStatus = ndb.IntegerProperty()
	lastRefreshedTS = ndb.DateTimeProperty(auto_now=True)




