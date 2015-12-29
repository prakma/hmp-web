'use strict';

// function debug() {
//     console.log.apply(console, arguments);
// }
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
      // debug('login method doing its work');
        Subscriber.login({}, {
            'email': givenEmail,
            'passwd': givenPassword,
            'pf': true
        }, function(value, responseHeaders) {
            //debug('login response' , value, responseHeaders);
            if(value.result && value.result !== 'Failure') {
                HMPUser.login(value);
                $scope.$emit('loginEvent', 'some junk');
                // debug('main controller emitted login event');
                //$window.location.href = '/user/index.html';
                $state.go('dashboard.current_view');
            } else {
                // debug('todo - invalid login attempt');
                $scope.loginError = "Invalid Login Credentials"
            }
            
        }, function(httpResponse) {
            console.log('login error response', httpResponse);
        });
    };

    $scope.chpass = function (oldPassword,newPassword, newPassword2) {
        if(newPassword != newPassword2){
            $scope.chPassMsg = "New Password does not match. Please confirm your new password again.";
            return;
        }
      // debug('login method doing its work');
        Subscriber.chpass({
            'oldPassword': oldPassword,
            'newPassword': newPassword,
        }, function(value, responseHeaders) {
            //debug('login response' , value, responseHeaders);
            if(value.result && value.result !== 'Failure') {
                console.log('password changed successfully');
                // reset the password form
                $scope.oldPassword="";
                $scope.newPassword="";
                $scope.newPassword2="";
                $scope.chPassMsg = "Password change completed. Please logout and log back in with your new password.";
            } else {
                // debug('todo - invalid login attempt');
                var failureMsg = value['message'];
                $scope.chPassMsg = failureMsg? failureMsg: "Password change failed";
            }
            
        }, function(httpResponse) {
            console.log('password change fail error response', httpResponse);
            $scope.chPassMsg = "Password change failed. Please try sometime later";
        });
    };

}]);