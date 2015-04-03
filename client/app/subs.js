angular.module('landingApp', [
  'ngRoute','ngResource'
]).
controller('SubscribeCtrl', function($scope, $window, $timeout, $route, $location, Subscriber){
	$scope.doSubscribe = function(doctorFlag, evt){
		console.log($scope.givenEmail," is a Doctor? ", doctorFlag, evt);
		var newUser = new Subscriber();
		newUser.givenEmail = $scope.givenEmail;
		newUser.doctorFlag = doctorFlag;
		Subscriber.add(null,newUser, function(value, responseHeaders){
			$scope.subscriptionStatus = "Thank you. We are glad to get your attention and can't wait to let you know as soon as this is ready !";
			$timeout(function(){
				$scope.subscriptionStatus = "";
				$scope.givenEmail = "";
				//$route.reload();
				$window.location.href = '/user/index.html';
			},5000);
		}, function(responseHeaders){
			$scope.subscriptionStatus = "Thank you for your interest. Something went wrong and we could not safely store your information. Could you please try again ?"
		});
		
	}
}).
factory('Subscriber', [
	'$resource', function($resource){
		return $resource('/s/subscriber/',{},{
			add: {
				method: 'PUT',
				params:{
					email: '@givenEmail',
					providerFlag: '@doctorFlag'
				}
			}
		});

	}]);