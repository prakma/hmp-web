import random
import unittest
import requests
import json


class TestProviderProfileUpdate(unittest.TestCase):


    def test_paymentProcessed(self):

        payment_args = {
            'key': Arg(str),
            'order_number': Arg(str),
            'invoice_id': Arg(str),
            'credit_card_processed': Arg(str),
            'total': Arg(str),
            'li_0_product_id': Arg(str)
            
        }
        r = requests.post('http://localhost:8081/s/payment/return', data = payment_args)
        # , headers={'Content-type': 'application/json'}
        rp = r.json()
        #self.assertEqual('Success', rp['result'])
        print "payment posted - ", rp

    
if __name__ == '__main__':
    unittest.main()