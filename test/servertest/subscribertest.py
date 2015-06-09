import random
import unittest
import requests


class TestRegistration(unittest.TestCase):

    @unittest.skip('donotregister')
    def test_agoodRegistration(self):
        r = requests.post('http://localhost:8080/s/subscriber', data = {'name':'mp1','email':'mp1@m.p', 'passwd':'password'})
        rp = r.json()
        self.assertEqual('Success', rp['result'])
        print "first time registration - ", rp

    # @unittest.skip('skip test_duplicateRegistration')
    def test_duplicateRegistration(self):
        r = requests.post('http://localhost:8080/s/subscriber', data = {'name':'mp1', 'email':'mp1@m.p', 'passwd':'password'})
        rp = r.json()
        print "duplicate registration - ",rp
        self.assertEqual('Failure', rp['result'])
        self.assertEqual('S4001', rp['code'])
        
        
    @unittest.skip('todo - write user query by email test')    
    def test_queryRegistration(self):
        r = requests.get('http://localhost:8080/s/subscriber', params = {'email':'mp1@m.p'})
        print "query registration - ", r.json()

class TestLogin(unittest.TestCase):
    @unittest.skip('skip failedlogin')
    def test_failedLogin(self):
        r = requests.post('http://localhost:8080/s/login', data = {'email':'mp1@m.p', 'passwd':'password2'})
        rp = r.json()
        print 'failedlogin', rp
        self.assertEqual('Failure', rp['result'])
        # self.account = r.cookies['hmp_account']
        # print self.account
    @unittest.skip('skip test_freshLogin')
    def test_freshLogin(self):
        r = requests.post('http://localhost:8080/s/login', data = {'email':'mp1@m.p', 'passwd':'password'})
        rp = r.json()
        self.assertEqual('Success', rp['result'])
        self.assertTrue(r.cookies['hmp_account'] != None)
        self.account = r.cookies['hmp_account']
        print self.account

class TestLogout(unittest.TestCase):

    def doLogin(self):
        r = requests.post('http://localhost:8080/s/login', data = {'email':'mp1@m.p', 'passwd':'password'})
        rp = r.json()
        print 'Testlogout.dologin helper', rp
        self.assertEqual('Success', rp['result'])
        self.account = r.cookies['hmp_account']
        # print self.account

    @unittest.skip('skip logout test')    
    def test_logout(self):
        self.doLogin()
        cookies = dict(hmp_account=self.account)
        # print 'cookies', cookies, 'self.account-', self.account,'xx'
        r = requests.post('http://localhost:8080/s/logout', cookies=cookies)
        rp = r.json()
        print 'test_logout', rp
        self.assertEqual('Success', rp['result'])

class TestWithLogin(unittest.TestCase):

    def setUp(self):
        r = requests.post('http://localhost:8080/s/login', data = {'email':'mp1@m.p', 'passwd':'password'})
        self.account = r.cookies['hmp_account']

    def tearDown(self):
        cookies = dict(hmp_account=self.account)
        # print 'cookies', cookies, 'self.account-', self.account,'xx'
        r = requests.post('http://localhost:8080/s/logout', cookies=cookies)
        rp = r.json()
        print 'teardown', rp
        self.assertEqual('Success', rp['result'])




class TestSubscriberAPI(TestWithLogin):
    # @unittest.skip('skip unauthenticated query test')
    def test_unauthenticatedQueryByEmail(self):
        r = requests.get('http://localhost:8080/s/subscriber', params = {'email':'mp1@m.p'})
        rp = r.json()
        print 'unauthenticated query by email', rp

    # @unittest.skip('skip authenticated query test')
    def test_authenticatedQueryByEmail(self):
        cookies = dict(hmp_account=self.account)
        r = requests.get('http://localhost:8080/s/subscriber', params = {'email':'mp1@m.p'}, cookies=cookies)
        rp = r.json()
        print 'authenticated query by email', rp

    

    # def test_choice(self):
    #     element = random.choice(self.seq)
    #     self.assertTrue(element in self.seq)

    # def test_sample(self):
    #     with self.assertRaises(ValueError):
    #         random.sample(self.seq, 20)
    #     for element in random.sample(self.seq, 5):
    #         self.assertTrue(element in self.seq)

if __name__ == '__main__':
    unittest.main()