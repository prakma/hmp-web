'use strict';


angular.module('providerApp.feedback', ['ngRoute'])

// .config(['$routeProvider', function($routeProvider) {
//   $routeProvider.when('profile/:profileId', {
//     templateUrl: 'profile/profile.html',
//     controller: 'ProfileCtrl'
//   });
// }])

.controller('FeedbackCtrl', ['$scope','$state','Feedback','HMPUser', function($scope, $state, FeedbackSvc, HMPUser) {
    console.log('feedback controller called !');
    $scope.s_initial = true;
    $scope.s_feedback_done = false;

    $scope.send_feedback = function() {
      
        FeedbackSvc.docAccountInterest({}, {
            'name': $scope.name,
            'subject': $scope.subject,
            'body': $scope.body
        }, function(value, responseHeaders) {
            //debug('login response' , value, responseHeaders);
            if(value.result && value.result !== 'Failure') {
                
                //$state.go('login');
                $scope.s_initial = false;
                $scope.s_feedback_done = true;
                $scope.status = "Your comment is recorded. We will contact you as soon as possible.";
            } else {
                console.log('todo - feedback creation problem');
            }
            
        }, function(httpResponse) {
            console.log('login error response', httpResponse);
        });
    };

}]);