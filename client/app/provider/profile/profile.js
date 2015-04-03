'use strict';

angular.module('providerApp.profile', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('profile/:profileId', {
    templateUrl: 'profile/profile.html',
    controller: 'ProfileCtrl'
  });
}])

.controller('ProfileCtrl', ['$scope', function($scope) {
	console.log('profile controller called !');
	$scope.testData = "test data";

}])

.directive('myHolder2', function() {
	console.log('myholder2 directive invoked');
  return {
    link: function(scope, element, attrs) {
      attrs.$set('data-src', attrs.myHolder2);
      Holder.run({images:element[0]});
    }
  };
});