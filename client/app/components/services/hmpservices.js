'use strict';

angular.module('hmp.hmpservices', [])
.factory('Subscriber', [
	'$resource', function($resource){
		return $resource('/s/subscriber/',{},{
			add: {
				method: 'PUT',
				params:{
					email: '@givenEmail',
					providerFlag: '@doctorFlag'
				}
			},
			register: {
				method: 'POST'

			},
			getDefault: {
				method: 'GET',
				url: '/s/subscriber/_default',
				isArray:true
			},
			getAppointments: {
				method: 'GET',
				url: '/s/consult/user_appts',
				isArray:true
			},
			getProvider: {
				method: 'GET',
				url: '/s/subscriber/doc/:providerId',
				params:{
					providerId: '@providerId'
				}
			},
			getFavoriteProviders: {
				method: 'GET',
				url: '/s/subscriber/favoritedocs',
				isArray:true
			},
			getUserSubscriber: {
				method: 'GET',
				url: '/s/subscriber/user/:userSubscriberId',
				params:{
					userSubscriberId: '@userSubscriberId'
				}
			},
			login: {
				method: 'POST',
				url: '/s/login/',
				params:{
					email: '@givenEmail',
					passwd: '@givenPassword',
					/* pf = provider flag */
					pf: '@pf'
				}
			},
			logout: {
				method: 'POST',
				url: '/s/logout/'
			},
			chpass: {
				method: 'POST',
				url: '/s/subscriber/credentials'
			}
		});

	}])
.factory('HMPUser', [
	'Subscriber', 'ipCookie', function(Subscriber, ipCookie) {
		var user = {};
		user.isLoggedId = function () {
			if(user.loggedUser)
				return true;
			else {
				var authUserAccount = ipCookie('hmp_account');
				if (authUserAccount) {
					var cachedValue = ipCookie('browserCache');
					if (cachedValue) {
						this.login(cachedValue, true);
						return true;
					} else
						return false
					
				} else
					return false;
			}
				
		};

		user.getSessionToken = function () {
			return user.loggedUser.sessionToken;
		};

		user.getName = function (){
			if (user.loggedUser) {
				return user.loggedUser.name;
			} else {
				return "Guest";
			}
			
		};


		user.getId = function (){
			if (user.loggedUser) {
				return user.loggedUser._id;
			} else {
				return "X00";
			}
			
		};

		user.getConsultationWF = function () {
			return user.cwf;
		}
		user.setConsultationWF = function (cwf) {
			user.cwf = cwf
		}

		user.setProvider = function (provider) {
			user.provider = provider;
		}
		user.selectedProvider = function () {
			return user.provider;
		}



		user.login = function (value, doNotStoreFlag) {
			console.log('user automatic login', value);
			if (value.result == 'Success') {
				if (! doNotStoreFlag)
					ipCookie('browserCache', value);
				var loggedUser = {};
				loggedUser.sessionToken = value.token;
				loggedUser.name = value.name;
				loggedUser._id = value.id;
				this.loggedUser = loggedUser;
			}
		};
		user.logout = function () {
			user.loggedUser = undefined;
			ipCookie.remove('hmp_account',{ path: '/' });
			ipCookie.remove('browserCache');
		};

		return user;

	}])
.factory('fPatientQBank', [
	function(){
		return function (qKeyVar){
			var qBank = {
				Summary: 'Summary...',
				qkey1: 'Describe your problem',
				qkey2: 'When did the symptoms begin? Can you suggest some factors that helped create these symptoms?',
				qkey3: 'Please describe anything that you feel is associated with the current symptoms that is unusual, rare and/or peculiar or any other information which you wish to add.',
				qkey4: 'If this is not the first occurrence please describe any previous problems of this kind.',
				qkey5: 'qkey5 is not populated or used'
			}

			if(qBank[qKeyVar])
				return qBank[qKeyVar];
			else
				return qKeyVar + ' - '+'Unknown Question';
		}

	}])
.factory('ProviderProfile', [
	'$resource', function($resource){
		return $resource('/s/provider/:providerId/profile',{},{
			
			getProvider: {
				method: 'GET',
				url: '/s/subscriber/doc/:providerId',
				params:{
					providerId: '@providerId'
				}
			}
		});

	}])
.factory('Prescription', [
	'$resource', function($resource){
		return $resource('/s/consult/cwf/:cref/createPrescriptionURL',{},{
			getUploadURL: {
				method: 'POST',
				params:{
					cref: '@cref'
				}
			}
		});

	}])
.factory('SubscriberDoc', [
	'$resource', function($resource){
		return $resource('/s/consult/cwf/:cref/createDocument2URL/:documentNo',{},{
			getUploadURL: {
				method: 'POST',
				params:{
					cref: '@cref',
					documentNo: '@documentNo'
				}
			}
		});

	}])
.factory('Feedback', [
	'$resource', function($resource){
		return $resource('/s/feedback/',{},{
			docAccountInterest: {
				method: 'PUT',
				params:{
					cref: '@cref',
					name:'@name',
					subject:'@subject',
					body:'@body'
				}
			}
		});

	}])
.factory('TwilioToken', [
	'$resource', function($resource){
		return $resource('/s/voicetoken',{});
	}])
.factory('fmoment', [
	function(){
		return moment;

	}]);
