
from bottle import Bottle, template, static_file, request, response, redirect
from webargs import Arg
from webargs.bottleparser import use_args
from sapi import consultAPI

docHandlerApp = Bottle()

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
	print 'document uploaded for cref', cref, request.forms, request.files
	f = request.files['uploaded_files']
	print 'uploaded files data', f.name
	print 'raw_filename', f.raw_filename
	print 'filename', f.filename
	print 'content_type', f.content_type
	print 'content_length', f.content_length


	def parse_gae_blobkey(content_type_val):
		blob_key_and_val = content_type_val.split(';')[1]
		print 'blob_key_and_val', blob_key_and_val
		blobKey = blob_key_and_val.split('=',1)[1][1:-1]
		print 'blobKey', blobKey
		return blobKey

	print 'blobkey', parse_gae_blobkey(f.content_type)
	args = {}
	args['cref'] = cref;
	args['blob_key'] = parse_gae_blobkey(f.content_type)
	args['documentNo'] = documentNo
	args['filename'] = f.filename
	args['filesummary'] = "Description Not available"

	consultAPI.handleSubscriberDocumentOnUpload(args)

	redirect('/user/index.html#/user/cwf/'+cref+'/questions')

@docHandlerApp.route('/s/consult/cwf/<cref>/document/<blobKey>', method='GET')
def subscriber_document_download(cref, blobKey):
	print 'subscriber document download requested for cref, blobkey', cref, blobKey[1:-1]
	subscriberDoc = consultAPI.getSubscriptionDocByBlobKey(cref,blobKey)
	response.set_header('X-AppEngine-BlobKey', blobKey) #base64.b64decode(blobKey[1:-1] ) )
	response.set_header('content-disposition', 'attachment; filename='+subscriberDoc.fileName)
	return response;