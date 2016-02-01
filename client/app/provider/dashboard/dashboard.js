'use strict';

angular.module('providerApp.dashboard', ['ngRoute'])

// .config(['$routeProvider', function($routeProvider) {
//   $routeProvider.when('/dashboard', {
//     templateUrl: 'dashboard/dashboard.html',
//     controller: 'DashboardCtrl'
//   });
// }])

.controller('DashboardCtrl', ['$scope', '$state', 'Consultation', 'CwfEvent','fmoment', function($scope, $state, Consultation, CwfEvent, fmoment) {
        console.log('dashboard controller called !');
        var currTime = fmoment();
        var fourHrBefore = fmoment().subtract(4, 'h');
        var fourHrLater = fmoment().add(4, 'h');
        var oneDayFuture = fmoment().add(1, 'd');
        var oneDayPast = fmoment().subtract(1, 'd');
        // provider_appts
        

        

        
        //console.log('current time from moment', moment());

        $scope.$on('$stateChangeSuccess', 
            function(event, toState, toParams, fromState, fromParams){
                console.log('state change happened', fromState, toState);
                setActiveView(toState.name);
            });

        var confirmedApptFilter = function(apptObj, index) {
            if (apptObj.apptWF.apptStatus == 3)
                return true;
            else
                return false;

        }
        var pendingApptFilter = function(apptObj, index) {
            if (apptObj.apptWF.apptStatus == 2 || apptObj.apptWF.apptStatus == 4)
                return true;
            else
                return false;

        }
        var olderApptFilter = function(apptObj, index) {
            // check for appointments that were scheduled yesterday or before
            //console.log('filtering for older appointments');
            if (apptObj.apptWF.apptStatus){
                var tmpApptTime = apptObj.apptWF.confirmedTS;
                if(!tmpApptTime){
                    // may be it was never confirmed so check for requested time
                    return false;
                } 
                if ( fmoment(tmpApptTime).isBefore(currTime, 'day') ){
                    return true;
                }
                return false;
            }
            else
                return false;

        }
        var futureApptFilter = function(apptObj, index) {
            // check for confirmed appointments of future ie, scheduled tomorrow or after
            console.log('filtering for future confirmed appointments');
            
            if (apptObj.apptWF.apptStatus){

                // if it is not confirmed, no need to show under today's appointments
                if (apptObj.apptWF.apptStatus < 3)
                    return false;

                var tmpApptTime = apptObj.apptWF.confirmedTS;
                if(!tmpApptTime){
                    // may be it was never confirmed so check for requested time
                    return false;
                } 
                if ( fmoment(tmpApptTime).isAfter(currTime, 'day') ){
                    return true;
                }
                return false;
            }
            else
                return false;

        }
        var todaysApptFilter = function(apptObj, index) {
            // check for appointments that were scheduled yesterday or before
            //console.log('filtering for today\'s confirmed appointments only');
            
            if (apptObj.apptWF.apptStatus){

                // if it is not confirmed, no need to show under today's appointments
                if (apptObj.apptWF.apptStatus < 3)
                    return false;

                var tmpApptTime = apptObj.apptWF.confirmedTS;
                if(!tmpApptTime){
                    // may be it was never confirmed so check for requested time
                    return false;
                } 
                if ( fmoment(tmpApptTime).isSame(currTime, 'day') ){
                    return true;
                }
                return false;
            }
            else
                return false;

        }
        var dashboardApptFilter = function(apptObj, index) {
            // check if the appointment is both confirmed and within the next 4 hour window
            //console.log('filtering for dashboard');
            if (apptObj.apptWF.apptStatus == 3){
                var tmpApptTime = apptObj.apptWF.confirmedTS;
                if(!tmpApptTime) return false;
                if ( fmoment(tmpApptTime).isBetween(fourHrBefore, fourHrLater, 'minute') ){
                    return true;
                }
                return false;
            }
            else
                return false;
        }

        // var sortByApptTime = function(apptObjX, apptObjY){
        //     if (apptObjX.apptWF.confirmedTS){
        //         if(apptObjY.apptWF.confirmedTS){
        //             // we are good to proceed with time checks
        //             var timeX = fmoment(apptObjX.apptWF.confirmedTS);
        //             var timeY = fmoment(apptObjY.apptWF.confirmedTS);
        //             if(timeX.isBefore(timeY))
        //                 return -1;
        //             else if(timeX.isAfter(timeY))
        //                 return 1;
        //             else return 0;
                    
        //         } else return 1;
        //     } else
        //         return -1;
        // }

        function refreshData(resolve){
            var fullApptList = Consultation.provider_appts();
            fullApptList.$promise.then(function(values){
                $scope.fullApptList = values;
                resolve();
            }, function(response){
                console.log('failed to get appointments', response);
                //reject();
            });
            
        }
        

        function setActiveView(viewName){
            if(viewName == 'dashboard.current_view'){
                //$scope.apptList = $scope.fullApptList.filter($scope.dashboardApptFilter);
                $scope.currview_active = "active";
                $scope.pastview_active = "inactive";
                $scope.todayview_active = "inactive";
                $scope.futureview_active = "inactive";
                refreshData(
                    function(){
                        // on success
                        // $scope.fullApptList is already set by refreshData so we can directly use it now
                        $scope.pendingApptList = $scope.fullApptList.filter(pendingApptFilter);
                        $scope.dashboardApptList = $scope.fullApptList.filter(dashboardApptFilter);
                    });
            } else if(viewName == 'dashboard.pastappt_view'){
                //$scope.apptList = Consultation.provider_appts();
                $scope.currview_active = "inactive";
                $scope.pastview_active = "active";
                $scope.todayview_active = "inactive";
                $scope.futureview_active = "inactive";
                refreshData(
                    function(){
                        // on success
                        // $scope.fullApptList is already set by refreshData so we can directly use it now
                        var olderApptList = $scope.fullApptList.filter(olderApptFilter);
                        // now sort by on appt time
                        //olderApptList.sort(sortByApptTime);
                        $scope.olderApptList = olderApptList.reverse();
                    });

            } else if(viewName == 'dashboard.todayappt_view'){
                //$scope.apptList = Consultation.provider_appts();
                $scope.currview_active = "inactive";
                $scope.pastview_active = "inactive";
                $scope.todayview_active = "active";
                $scope.futureview_active = "inactive";
                //console.log('refresh data for todays appt view');
                refreshData(
                    
                    function(){
                        // on success
                        // $scope.fullApptList is already set by refreshData so we can directly use it now
                        //console.log('refreshing data for todays appt view');
                        $scope.todaysApptList = $scope.fullApptList.filter(todaysApptFilter);
                    });
                

            } else if(viewName == 'dashboard.futureappt_view'){
                //$scope.apptList = Consultation.provider_appts();
                $scope.currview_active = "inactive";
                $scope.pastview_active = "inactive";
                $scope.todayview_active = "inactive";
                $scope.futureview_active = "active";
                //console.log('refresh data for todays appt view');
                refreshData(
                    
                    function(){
                        // on success
                        // $scope.fullApptList is already set by refreshData so we can directly use it now
                        console.log('refreshing data for future appt view');
                        $scope.futureApptList = $scope.fullApptList.filter(futureApptFilter);
                    });
                

            } else {
                $scope.currview_active = "active";
                $scope.pastview_active = "inactive";
                $scope.todayview_active = "inactive";
                $scope.futureview_active = "inactive";
            }
            
            
        }

        //setActiveView("default");
        //refreshData();
        $scope.gotoCRoom = function(apptObj) {
            //console.log('goto consulting room', cid, uid, pid);
            if(apptObj.meetingWF && apptObj.meetingWF.meetingType){
                if(apptObj.meetingWF.meetingType == 'phone'){
                    $state.go('croom_audio', {
                        appt: apptObj
                    });
                    return;
                }
            }

            // default is video mode of consultation
            $state.go('croom', {
                appt: apptObj
            });
        };

        $scope.gotoAudioRoom = function(apptObj) {
            //console.log('goto consulting room', cid, uid, pid);
            $state.go('croom_audio', {
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
            $scope.feedbackStr = "Confirming..."
            setTimeout(function() {
                apptObj.$set_apptWFState({
                        cref: apptObj._id,
                        aptWFCd: 3
                    },
                    function(value, responseHeaders) {
                        console.log('appt confirmed', value);
                        $scope.feedbackStr = "Confirmed"
                        setTimeout(function(){
                            refreshData(
                                function(){
                                    // on success
                                    // $scope.fullApptList is already set by refreshData so we can directly use it now
                                    $scope.feedbackStr = "";
                                    $scope.pendingApptList = $scope.fullApptList.filter(pendingApptFilter);
                                    $scope.dashboardApptList = $scope.fullApptList.filter(dashboardApptFilter);
                                });
                        }, 2000);
                        
                    },
                    function(httpResponse) {
                        console.log('appt not confirmed. something wrong with the server', httpResponse);
                    });
            });
        };

        $scope.rescheduleAppt = function(apptObj, reschedD, reschedT, reschedMsg, successCallbkFn) {
            console.log('reschedule appointment clicked', apptObj, reschedD, reschedT, reschedMsg );
            var rescheduledDate = fmoment(reschedD);
            var rescheduledTime = fmoment(reschedT);
            rescheduledDate.hours(rescheduledTime.hours()).minutes(rescheduledTime.minutes());
            var newCwfEvent = new CwfEvent();
            newCwfEvent.cref = apptObj._id;
            newCwfEvent.eventName = 'RescheduleByProvider';
            newCwfEvent.reschedDT = rescheduledDate;
            newCwfEvent.reschedMsg = reschedMsg;

            newCwfEvent.$save(function(result){
                console.log('event saved', result);
                //apptObj.apptWF.apptStatus = 5;
                console.log('refreshing the dashboard after rescheduling');
                setTimeout(function(){
                    if(successCallbkFn){
                        console.log('calling callback after rescheduling');
                        successCallbkFn();
                    } else{
                        console.log('refreshing the dashboard after rescheduling');
                        refreshData(function(){
                            console.log('refreshing the pending appt list');
                            // on success
                            // $scope.fullApptList is already set by refreshData so we can directly use it now
                            $scope.pendingApptList = $scope.fullApptList.filter(pendingApptFilter);
                            $scope.dashboardApptList = $scope.fullApptList.filter(dashboardApptFilter);
                        });
                    }
                    
                },2000);
                
            });
            
        };

    }])
    .controller('PatientApptCtrl', ['$scope', '$state', '$stateParams', '$q', 'Consultation', 'fPatientQBank', 'Prescription',
        function($scope, $state, $stateParams, $q, Consultation, fPatientQBank, Prescription) {
            console.log('PatientApptCtrl controller called !');
            //$scope.appt = $stateParams.appt;
            console.log('cref in appt detail view', $stateParams.cref);

            function refreshCwfDetails(){
                var promise = (function() {
                    return $q(function(resolve, reject) {
                        if (false/*$stateParams.appt*/) {
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


            }

            $scope.refreshAction = refreshCwfDetails;

            $scope.refreshAction();
            

            

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

            console.log('PatientApptCtrl controller finished !');

        }
    ]);