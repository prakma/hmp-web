'use strict';

angular.module('hmp.cwfservices', [])
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

			},
			user_appts: {
				method: 'GET',
				url: '/s/consult/user_appts',
				isArray:true

			},
			set_apptWFState: {
				method: 'POST',
				url: '/s/consult/cwf/:cref/apptwf'
			}
		});

	}])
.factory('CwfEvent', [
	'$resource', function($resource){
		return $resource('/s/consult/cwf/event',{});
	}]);	