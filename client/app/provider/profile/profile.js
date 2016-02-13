'use strict';

angular.module('providerApp.profile', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('profile/:profileId', {
    templateUrl: 'profile/profile.html',
    controller: 'ProfileCtrl'
  });
}])
.config(function($stateProvider, $urlRouterProvider) {
    $stateProvider.
    state('provider_profile', {
        url: '/provider/profile',
        templateUrl: '/provider/profile/profile.html'
    }).
    state('doc_profile',{
		url: '/user/doc/:docId',
		templateUrl: '/user/partials/doctor_profile.html'
	})
})
.controller('ProfileCtrl', ['$scope', function($scope) {
	console.log('profile controller called !');
	//$scope.testData = "test data";

}])
.controller('DocProfileCtrl', ['$scope', '$window', '$timeout', '$state', 'ProviderProfile', function($scope, $window, $timeout, $state, ProviderProfile){
	//var authUserAccount = ipCookie('hmp_account');
	//debug('authuseraccount, scope', authUserAccount, $scope);
	debug('DocProfileCtrl invoked', $state.params.docId);
	// var provider = Subscriber.getProvider({providerId:$state.params.docProfileId});
	// $scope.provider = provider;
	// HMPUser.setProvider(provider);
	// debug('provider information', $scope.provider);
	// $scope.beginWF = function (){
	// 	$state.go ('appt', {'docProfileId':$state.params.docProfileId});
	// }

	$scope.userIsProvider = true;
	$scope.provider = ProviderProfile.get({providerId:$state.params.docId});
	
	$scope.showMoreFlag = false,$scope.more_less_text = "More..."; // default
	console.log('current more/less text is',$scope.more_less_text);
	$scope.showMoreOrLess = function (){
		// toggle the div ... if current val is "more", show the div now, but toggle the text to "less"
		console.log('toggle more or less');
		if($scope.showMoreFlag){
			$scope.showMoreFlag = false;
			$scope.more_less_text = "More...";

		} else{
			$scope.showMoreFlag = true;
			$scope.more_less_text = "Less...";
		}

	}
	
	
}])
;