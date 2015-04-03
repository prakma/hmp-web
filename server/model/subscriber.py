from google.appengine.ext import ndb
import datetime

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
				self.phone.append(value)
		else:
			super(Subscriber, self).__setattr__(name,value)

	def checkPassword (self, p):
		return (self.passwd == p )


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
	# 1 = not started, 2 = requested, 3 = confirmed , 4 = new time rescheduled by user, 5 = new time proposed by provider, 6 = canceled
	apptStatus = ndb.IntegerProperty(default=1)

## payment_info_provided, sent_to_bank, bank_confirmed
class PaymemtWF(ndb.Model):
	paymentToken = ndb.StringProperty(repeated=True)
	paymentBeginTS = ndb.DateTimeProperty(repeated=True)
	paymentConfirmToken = ndb.StringProperty(repeated=True)
	paymentConfirmTS = ndb.StringProperty(repeated=True)

	#default=not_initiated,
	paymentStatusChain = ndb.IntegerProperty(repeated=True)
	paymentStatus = ndb.IntegerProperty()


## no_info, partial_info, nearly_complete, complete
class PatientDetailsWF(ndb.Model):
	patientName = ndb.StringProperty()
	patientAge = ndb.StringProperty()
	patientSex = ndb.StringProperty()
	#[Summary,]
	questionId = ndb.StringProperty(repeated=True)
	answerText = ndb.StringProperty(repeated=True)
	userDetailsStatus = ndb.IntegerProperty()


# checkin, waiting_for_connection, connected, meeting_in_progress, completed, abandoned, no_show, disconnected 
class MeetingWF(ndb.Model):
	# phone, video
	meetingType = ndb.StringProperty()
	userDevice = ndb.StringProperty()
	providerDevice = ndb.StringProperty()
	meetingStatus = ndb.IntegerProperty()
	meetingDelayMinutes = ndb.IntegerProperty()
	meetingDurationMinutes = ndb.IntegerProperty()
	meetingInterruptionMinutes = ndb.IntegerProperty()
	meetingStatusChain = ndb.IntegerProperty(repeated=True)
	meetingStatus = ndb.IntegerProperty()

# prescription_sent, prescription_received
class FulfillmentWF(ndb.Model):
	prescription_ref = ndb.StringProperty()
	prescriptionTS = ndb.DateTimeProperty()
	fulfillmentStatus = ndb.IntegerProperty()


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




