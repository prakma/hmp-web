import random
import unittest
import requests
import json


class TestProviderProfileUpdate(unittest.TestCase):


    def test_createProfile(self):
        r = requests.post('http://localhost:8081/s/profile/provider', json = {
            'degree':['BHMS', 'MS', 'PhD'],
            'email':'akapoor@m.p', 
            'oneLiner':'BHMS, XYZ Homeo Hall',
            'profileDesc':['profile desc1', 'profileDesc2', 'profileDesc3'],
            'specialty':['heart diseases', 'kids', 'hair loss'],
            'genLocation': ['Domlur, Bangalore', 'Karnataka, India'],
            'timing': ['Monday - Friday 9am to 7 pm', 'Saturday 9am to 1 pm', 'Sunday closed'],
            'servicesOffered': ['Consultation', 'Medicine', 'Emergency'],
            'feeStructure': ['First Consultation: Rs 500', 'Followup consultation: Rs 200']
            })
        # , headers={'Content-type': 'application/json'}
        rp = r.json()
        #self.assertEqual('Success', rp['result'])
        print "first time profile setup - ", rp

    
if __name__ == '__main__':
    unittest.main()