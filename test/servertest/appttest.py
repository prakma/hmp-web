import unittest
import requests

class TestNewAppt(unittest.TestCase):

    # def setUp(self):
    #     r = requests.post('http://localhost:8080/s/login', data = {'email':'mp1@m.p', 'passwd':'password'})
    #     self.account = r.cookies['hmp_account']

    # def tearDown(self):
    #     cookies = dict(hmp_account=self.account)
    #     # print 'cookies', cookies, 'self.account-', self.account,'xx'
    #     r = requests.post('http://localhost:8080/s/logout', cookies=cookies)
    #     rp = r.json()
    #     print 'teardown', rp
    #     self.assertEqual('Success', rp['result'])


    def test_newAppt(self):
        apptInput = {'provider':'5629499534213120','requestedTS':'01-03-2015T12:30:00Z+5:30', 
        'token':'e8adb1491a3b4a52a28d9f20cb58aa4a',
        'problemSummary':'I have lots of problem but you can attempt only one'}
        r = requests.put('http://localhost:8080/s/consult', data = apptInput)
        print r.json()

if __name__ == '__main__':
    unittest.main()