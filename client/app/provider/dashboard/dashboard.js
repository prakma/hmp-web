'use strict';

angular.module('providerApp.dashboard', ['ngRoute'])

// .config(['$routeProvider', function($routeProvider) {
//   $routeProvider.when('/dashboard', {
//     templateUrl: 'dashboard/dashboard.html',
//     controller: 'DashboardCtrl'
//   });
// }])

.controller('DashboardCtrl', ['$scope', '$state','Consultation',function($scope, $state, Consultation) {
	console.log('dashboard controller called !');
	// provider_appts
  	$scope.apptList = Consultation.provider_appts();
  	$scope.gotoCRoom = function (apptObj) {
  		//console.log('goto consulting room', cid, uid, pid);
  		$state.go('croom', {appt:apptObj});
  	}


}]);