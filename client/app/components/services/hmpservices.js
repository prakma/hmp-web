'use strict';

angular.module('myApp.services', [])
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
			login: {
				method: 'POST',
				url: '/s/login/',
				params:{
					email: '@givenEmail',
					passwd: '@givenPassword'
				}
			},
			logout: {
				method: 'POST',
				url: '/s/logout/'
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
.factory('Consultation', [
	'$resource', function($resource){
		return $resource('/s/consult/',{},{
			begin: {
				method: 'PUT',
				params:{
					providerId: '@providerId'
				}
			},
			request_appt: {
				method: 'POST',
				url: '/s/consult/appt'
			},
			patient_q: {
				method: 'POST',
				url: '/s/consult/patientq'
			},
			user_appts: {
				method: 'GET',
				url: '/s/consult/user_appts',
				isArray:true

			},
			get_cwf: {
				method: 'GET',
				url: '/s/consult/cwf/:cref'
			},
			provider_appts: {
				method: 'GET',
				url: '/s/consult/provider_appts',
				isArray:true

			}
		});

	}]);
