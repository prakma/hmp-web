from model import subscriber, queryAPI, ndb_json, providerProfile
import dateutil.parser
import datetime
import hashlib
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

def getPlatformFee (args):
	return 200