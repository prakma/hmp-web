
from sapi import subscriberAPI
import hmpconstants

# secret used for writing and reading session token cookie
cookie_secret = hmpconstants.RemedySquareCookie.cookie_secret

def ensureLogin(func):
	token = request.get_cookie("hmp_account", secret=cookie_secret)

	print 'ensureLogin of authenticator called'
	# def func_unauthenticated(*args, **kwargs):
	# 	return {'result':'Failure', 'message':'Unauthenticated'}
	# def func_wrapper(*args, **kwargs):
	# 	if (token == None):
	# 		print 'returning json'
	# 		return func_unauthenticated(*args, **kwargs)
	# 	else:
	# 		print 'returning func_wrapper'
	# 		return func(*args, **kwargs)
	# return func_wrapper
	if(token != None):
		return subscriberAPI.x_querySubscriberByToken(token)
	else:
		return None