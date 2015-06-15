'use strict';

angular.module('providerApp.dashboard', ['ngRoute'])

// .config(['$routeProvider', function($routeProvider) {
//   $routeProvider.when('/dashboard', {
//     templateUrl: 'dashboard/dashboard.html',
//     controller: 'DashboardCtrl'
//   });
// }])

.controller('DashboardCtrl', ['$scope', '$state', 'Consultation', 'fmoment', function($scope, $state, Consultation, fmoment) {
        console.log('dashboard controller called !');
        // provider_appts
        $scope.apptList = Consultation.provider_appts();
        //console.log('current time from moment', moment());
        $scope.currApptFilter = function(apptObj, index) {
            if (apptObj.apptWF.status == 3)
                return true;
            else
                return false;

        }
        $scope.gotoCRoom = function(apptObj) {
            //console.log('goto consulting room', cid, uid, pid);
            $state.go('croom', {
                appt: apptObj
            });
        };

        $scope.gotoApptDetails = function(apptObj) {
            console.log('show patient details info');
            $state.go('dashboard.appt_view', {
                appt: apptObj,
                'cref': apptObj._id
            });
        }

        $scope.confirmAppt = function(apptObj) {
            console.log('confirm appointment clicked');
            setTimeout(function() {
                apptObj.$set_apptWFState({
                        cref: apptObj._id,
                        aptWFCd: 3
                    },
                    function(value, responseHeaders) {
                        console.log('appt confirmed', value);
                    },
                    function(httpResponse) {
                        console.log('appt not confirmed. something wrong with the server', httpResponse);
                    });
            });
        };

        $scope.rescheduleAppt = function(apptObj) {
            console.log('reschedule appointment clicked');
            setTimeout(function() {

            });
        };


    }])
    .controller('PatientApptCtrl', ['$scope', '$state', '$stateParams', '$q', 'Consultation', 'fPatientQBank', 'Prescription',
        function($scope, $state, $stateParams, $q, Consultation, fPatientQBank, Prescription) {
            console.log('PatientApptCtrl controller called !');
            //$scope.appt = $stateParams.appt;
            console.log('cref in appt detail view', $stateParams.cref);

            var promise = (function() {
                return $q(function(resolve, reject) {

                    if (false/*$stateParams.appt*/ ) {
                      setTimeout(function(){
                        resolve($stateParams.appt);
                      });
                    } else if ($stateParams.cref){
                      // fetch appt details of this appt
                      var freshCwfObj = Consultation.get_cwf({
                          'cref': $stateParams.cref
                      });
                      freshCwfObj.$promise.then(function(){
                        resolve(freshCwfObj);
                      }, function(){
                        reject($stateParams.cref);
                      });
                    } else {
                      setTimeout(function(){
                        reject('Unknown cref');
                      });
                    }
                        
                });
            })();

            promise.then(function(cwf) {
              console.log(' promise fulfilled ! cwf is', cwf);
                $scope.appt = cwf;
                var questionSize, questionSizeArray = [];
                questionSize = 0 || $scope.appt.patientDetailsWF.questionId.length;
                for (var i = 0; i < questionSize; i++) {
                    questionSizeArray.push(i);
                }

                $scope.qLoopHelper = questionSizeArray;
                // console.log('question size array', questionSizeArray);
                // console.log('qid 1', $stateParams.appt.patientDetailsWF.questionId[0]);
                $scope.qbank = fPatientQBank;
            }, function(failedCref) {
                console.log('appt with cref', failedCref, ' could not be loaded');
            });




            $scope.generateUploadURL = function() {
                setTimeout(function() {
                    console.log('generateUploadURL called ! generating upload url....');
                    Prescription.getUploadURL({
                            cref: $scope.appt._id
                        },
                        null,
                        function(value, responseHeaders) {
                            $scope.uploadURL = value.upload_url;
                        },
                        function(errorHttpResponse) {
                            console.log('error in preparing the file upload');
                        });
                });
            }

        }
    ]);