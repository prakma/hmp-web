
from bottle import Bottle, template, static_file, request, response, redirect
from webargs import Arg
from webargs.bottleparser import use_args
from sapi import consultAPI

docHandlerApp = Bottle()

@docHandlerApp.route('/s/consult/cwf/<cref>/createPrescriptionURL', method='POST')
def create_upload_url(cref):
	args = {}
	args['cref'] = cref
	args['upload_callback_url'] = '/s/consult/cwf/'+cref+'/prescription'
	print 'create upload url for prescription', cref
	return consultAPI.create_upload_url(args)

# @route('/s/consult/cwf/<cref>/createDocument2URL/<docnumber>', method='POST')
# def create_uploaddoc_url(cref, docnumber):
# 	print 'create upload url for document', cref, docnumber
# 	args = {}
# 	args['cref'] = cref
# 	args['document_url'] = '/s/consult/cwf/'+cref+'/document'
# 	print 'create upload url for prescription', cref, docnumber
# 	return {'result':'Success'}

def parse_gae_blobkey_deprecated(content_type_val):
	blob_key_and_val = content_type_val.split(';')[1]
	print 'blob_key_and_val', blob_key_and_val
	blobKey = blob_key_and_val.split('=',1)[1][1:-1]
	print 'blobKey', blobKey
	return blobKey



def parse_gae_blobkey2(content_type_val):
	# content_type in production message/external-body; charset=UTF-8; blob-key=AMIfv97fmatuLK6mt5R
	# content_type in dev message/external-body; blob-key="ptfcYef6qLAtTacQoG4JiQ=="; access-type="X-AppEngine-BlobKey"

	content_type_split_arr = content_type_val.split(';')
	# blob_key_and_val = content_type_val.split(';')[1]
	for x in content_type_split_arr:
		blob_key_part = x.split('=',1)
		blob_key_part_keyname = blob_key_part[0].strip()
		
		if(blob_key_part_keyname == 'blob-key'):
			blob_key_part_value = blob_key_part[1]
			print 'blob_key_part_value',blob_key_part_value
			blobKeyValue = blob_key_part_value #[1:-1]
			print 'blob-key', blobKeyValue
			# remove the leading and trailing doublequote characters if present. there is difference in blob-key value in dev vs production instance of app engine
			blobKeyValue = blobKeyValue.strip('"')
			print 'trimmed blob-key'
			return blobKeyValue

	# we should never reach here.... it means we were unable to parse the blobkey
	return "blob_unrecognized"

@docHandlerApp.route('/s/consult/cwf/<cref>/prescription', method='POST')
def prescription_uploaded(cref):
	print 'prescription uploaded for cref', cref, request.forms, request.files
	f = request.files['uploaded_files']
	print 'uploaded files data', f.name
	print 'raw_filename', f.raw_filename
	print 'filename', f.filename
	print 'content_type', f.content_type
	print 'content_length', f.content_length

	parsedBlobKey = parse_gae_blobkey2(f.content_type)

	print 'blobkey', parsedBlobKey
	args = {}
	args['cref'] = cref;
	args['filename'] = f.filename
	args['blob_key'] = parsedBlobKey

	consultAPI.handlePrescriptionOnUpload(args)

	redirect('/provider/provider_index.html#/provider/dashboard/'+cref+'/appt_view.html')

@docHandlerApp.route('/s/consult/cwf/<cref>/prescription/<blobKey>', method='GET')
def prescription_download(cref, blobKey):
	print 'prescription download requested for cref, blobkey', cref, blobKey
	# response.set_header('X-AppEngine-BlobKey', blobKey) #base64.b64decode(blobKey[1:-1] ) )
	# response.set_header('content-disposition', 'attachment; filename=prescription_'+cref+'.pdf')
	# return response;

	subscriberDoc = consultAPI.getPrescriptionDocByBlobKey(cref,blobKey)
	response.set_header('X-AppEngine-BlobKey', blobKey) #base64.b64decode(blobKey[1:-1] ) )
	response.set_header('content-disposition', 'attachment; filename='+subscriberDoc.fileName)
	return response;



@docHandlerApp.route('/s/consult/cwf/<cref>/createDocument2URL/<documentNo>', method='POST')
def create_uploaddoc_url(cref, documentNo):
	print 'create upload url for document', cref, documentNo
	args = {}
	args['cref'] = cref
	args['upload_callback_url'] = '/s/consult/cwf/'+cref+'/document/'+documentNo
	print 'create upload url for subscriber documents', cref, documentNo
	return consultAPI.create_upload_url(args)

@docHandlerApp.route('/s/consult/cwf/<cref>/document/<documentNo>', method='POST')
def document_uploaded_callback(cref, documentNo):
	print 'document uploaded for cref in documenthandler', cref, request.forms, request.files
	f = request.files['uploaded_files']
	print 'uploaded files data', f.name
	print 'raw_filename', f.raw_filename
	print 'filename', f.filename
	print 'content_type', f.content_type
	print 'content_length', f.content_length


	
	
	parsedBlobKey = parse_gae_blobkey2(f.content_type)
	print 'blobkey', parsedBlobKey
	args = {}
	args['cref'] = cref;
	args['blob_key'] = parsedBlobKey
	args['documentNo'] = documentNo
	args['filename'] = f.filename
	args['filesummary'] = "Description Not available"

	consultAPI.handleSubscriberDocumentOnUpload(args)

	redirect('/user/index.html#/user/cwf/'+cref+'/questions')

@docHandlerApp.route('/s/consult/cwf/<cref>/document/<blobKey>', method='GET')
def subscriber_document_download(cref, blobKey):
	print 'subscriber document download requested for cref, blobkey', cref, blobKey
	subscriberDoc = consultAPI.getSubscriptionDocByBlobKey(cref,blobKey)
	response.set_header('X-AppEngine-BlobKey', blobKey) #base64.b64decode(blobKey[1:-1] ) )
	response.set_header('content-disposition', 'attachment; filename='+subscriberDoc.fileName)
	return response;