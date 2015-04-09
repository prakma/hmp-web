'use strict';

function debug() {
    console.log.apply(console, arguments);
}
angular.module('providerApp.session', ['ngRoute'])

// .config(['$routeProvider', function($routeProvider) {
//   $routeProvider.when('profile/:profileId', {
//     templateUrl: 'profile/profile.html',
//     controller: 'ProfileCtrl'
//   });
// }])

.controller('SessionCtrl', ['$scope','$state','Subscriber','HMPUser', function($scope, $state, Subscriber, HMPUser) {
    console.log('provider session controller called !');
    $scope.login = function(givenEmail, givenPassword) {
      debug('login method doing its work');
        Subscriber.login({}, {
            'email': givenEmail,
            'passwd': givenPassword,
            'pf': true
        }, function(value, responseHeaders) {
            //debug('login response' , value, responseHeaders);
            if(value.result && value.result !== 'Failure') {
                HMPUser.login(value);
                $scope.$emit('loginEvent', 'some junk');
                debug('main controller emitted login event');
                //$window.location.href = '/user/index.html';
                $state.go('dashboard');
            } else {
                debug('todo - invalid login attempt');
            }
            
        }, function(httpResponse) {
            debug('login error response', httpResponse);
        });
    };

}]);