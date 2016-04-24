import requests

localbox = "localhost:8081"

targetbox = localbox

subscriberUrl = 'http://'+targetbox+'/s/subscriber'
profileUrl = 'http://'+targetbox+'/s/profile/provider'

def seedDoctor():
	doctor1 = {'name':'Dr. Jane Doe','email':'jdoe@m.p','phone':'+18323494988', 'passwd':'pass96word', 'providerFlag':'true', 'primaryLocationStr':'Domlur, Bangalore'}
	r = requests.post(subscriberUrl, data = doctor1)
	print 'seed doctor response - ',r.json()
	print 'Doctor created'

def seedProfileFull():
    r = requests.post(profileUrl, json = {
            'degree':['MD (A.M)', 'BHMS', 'CCH'],
            'email':'jdoe@m.p', 
            'oneLiner':'BHMS, XYZ Homeo Hall',
            'profileDesc':[
                'Jane Doe is a master Classical Homeopath with over a decade of experience helping clients heal from an array of Acute and Chronic conditions through the natural, non-toxic application of Classical Homeopathy.', 
                'Ms. Doe has been practicing Homeopathy in India for five years prior to moving to California.  She has observed her patients recover from such conditions as menstrual disorders, menopause, diabetes, hypertension, asthma, allergies, nightmares, migraines, and various skin disorders.  Her confidence arises from experience both as a patient and a practioner.', 
                'She is trusted by hundreds of clients because of her holistic approach and proven results. Jane graduated from a traditional medical school with a specialization in Classical Homeopathy.'
                ],
            'specialty':['Hair Loss', 'Skin Diseases', 'Cold/Flu'],
            'genLocation': ['Domlur, Bangalore', 'Karnataka, India'],
            'timing': ['Monday - Friday 9am to 7 pm', 'Saturday 9am to 1 pm', 'Sunday closed'],
            'servicesOffered': ['Consultation', 'Medicine', 'Emergency'],
            'feeStructure': ['First Consultation: Rs 500', 'Followup consultation: Rs 200'],
            'feeStruc':{
                        'baseCurrency':'INR',
                        'regularFee': 200,
                        'followupFee': 100,
                        'followupDuration':'2 weeks',
                        'platformFee':300,
                        'firstTimeFee': 600

                        },
            'calStruc':{
                        'mon':'9 AM to 2 PM, 5 PM to 10 PM',
                        'tue':'9 AM to 2 PM, 5 PM to 10 PM',
                        'wed':'9 AM to 2 PM, 5 PM to 10 PM',
                        'thu':'9 AM to 2 PM, 5 PM to 10 PM',
                        'fri':'5 PM to 10 PM',
                        'sat':'2 PM to 10 PM',
                        'sun':'000',
                        'exc':'000'

                        },
            'education':{'strucKeyword':'Education','strucValues':['MD (A.M)', 'BHMS', 'CCH']},
            'registration':{'strucKeyword':'Registration','strucHead':'3082 A - Tamilnadu Medical Council, 2005'},
            'membership':{'strucKeyword':'Membership','strucHead':'Tamilnadu Medical Council','strucValues':['Indian Homoepathic Physicians', 'PETA', 'Homeo Medicines Group']},
            'awardsRecognitions':{'strucKeyword':'Awards','strucDesc':'Presidents Medal'},
            'experience':{'strucKeyword':'Experience','strucHead':'15 years in providing homeopathic remedies','strucValues':['2004-2006 : Shanti Home Hall, Bangalore', '2006-209: Homeopathic Consultant at ABC Homeo Hospital, Bangalore', '2009-2015 : My Homeo Clinic']}
        })
        # , headers={'Content-type': 'application/json'}
    rp = r.json()
    #self.assertEqual('Success', rp['result'])
    print "profile setup response - ", rp

    print 'Profile Seeded'



seedDoctor()
#seedProfileFull()





