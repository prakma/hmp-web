function debug () {
	console.log.apply(console, arguments);
}

angular.module('userApp', [
  'ui.router','ngResource','providerApp.version','hmp.hmpservices','hmp.cwfservices',/*'ui.calendar'*/'mgcrea.ngStrap','ipCookie',
  'userApp.croom'
]).
config(function($stateProvider, $urlRouterProvider){
	$urlRouterProvider.otherwise("/user/index");
	$stateProvider.
		state('login',{
			url: '/user/login',
			templateUrl: '/user/partials/login.html'
		}).
		state('register',{
			url: '/user/register',
			templateUrl: '/user/partials/registration.html'
		}).
		state('userLanding',{
			url: '/user/index',
			templateUrl: '/user/partials/userLanding.html'
		}).
		state('appt',{
			url: '/user/appt/:docId',
			templateUrl: '/user/partials/appt_request.html'
		}).
		state('doc',{
			url: '/user/doc',
			templateUrl: '/user/partials/doctor.html',
			params: {searchText:{}},
			controller: 'DocCtrl'
		}).
		state('doc_profile',{
			url: '/user/doc/:docId',
			templateUrl: '/user/partials/doctor_profile.html'
		}).
		state('patient_question',{
			url: '/user/:cref/questions',
			templateUrl: '/user/partials/patient_qform1.html'
		}).
		state('consultation_list',{
			url:'/user/consultations',
			templateUrl: '/user/partials/consultation_list.html',
			controller: 'ConsultationListCtrl'
		}).
		state('consult_wf',{
			url: '/user/cwf/:cref',
			templateUrl: '/user/partials/consult_wf.html',
			controller: 'CwfCtrl',
			params: {'new_appt_flow':false}
		}).
		state('consult_wf.appt',{
			url: '^/user/cwf/:cref/appt',
			templateUrl: '/user/partials/consult_wf_appt.html'
		}).
		state('consult_wf.payment',{
			url: '^/user/cwf/:cref/payment',
			templateUrl: '/user/partials/consult_wf_payment.html',
			controller: 'CwfPaymentCtrl'
		}).
		state('consult_wf.paymentReturn',{
			url: '^/user/cwf/:cref/payment/return',
			templateUrl: '/user/partials/consult_wf_payment_return.html',
			controller:'CwfPaymentReturnCtrl'
		}).
		state('consult_wf.questions',{
			url: '^/user/cwf/:cref/questions',
			templateUrl: '/user/partials/consult_wf_questions.html'
		}).
		state('consult_wf.prescription',{
			url: '^/user/cwf/:cref/prescription',
			templateUrl: '/user/partials/consult_wf_prescription.html'
		}).
		state('croom',{
			templateUrl: '/user/partials/croom/croom.html',
			params: {appt:{}}
		}).
		state('account',{
			url: '/user/account',
			templateUrl: '/user/partials/account.html'
		}).
		state('userHelp',{
			url: '/user/help',
			templateUrl: '/user/partials/help.html'
		});
}).controller('MenuContainerCtrl', function($scope, $window, $timeout, $interval, $state, ipCookie, Subscriber, HMPUser, fmoment){
	//debug('MenuContainerCtrl called');
	$scope.actionEventTime = fmoment();
	$scope.$on('loginEvent', function(event, args) {
		// debug('Menubar ctrl received login event');
		initializeUser ();
	});
	$scope.$on('actionEvent', function(event, args) {
		// debug('Menubar ctrl received login event');
		$scope.actionEventTime = fmoment();
		$scope.actionEventText = args;
	});

	

	$interval(function refreshStatus(){
		var currTime = fmoment();
		var diffInSeconds = currTime.diff($scope.actionEventTime, 'seconds');
		$scope.hourDiff = diffInSeconds/3600|0;
		$scope.minDiff = ((diffInSeconds%3600)/60) | 0;
		$scope.secondsDiff = (diffInSeconds%3600)%60;
		//console.log('refresh status',$scope.hourDiff, $scope.minDiff, $scope.secondsDiff );
		$scope.actionEventMomentText = $scope.hourDiff+'h: '+ $scope.minDiff+'m: '+ $scope.secondsDiff+' seconds ago';
		

	}, 5000);



	function initializeUser(){
		//debug('initializeUser from menubar invoked. hmpuser ', HMPUser);
		$scope.authFlag = HMPUser.isLoggedId();
		$scope.userName = HMPUser.getName();
		//debug('is user logged in', HMPUser.isLoggedId(), $scope.authFlag,'name',HMPUser.getName() );
	}

	initializeUser();

	$scope.logout = function () {

		function resetUser (){
			HMPUser.logout();
			initializeUser();
		}

		$timeout (function() {
			Subscriber.logout({},{},function (){
				resetUser();
			}, function () {
				resetUser();
			});
			
			//$route.reload();
			//$window.location.href = '/user/index.html';
			$state.go('userLanding');
		},2000);

	}

}).
controller('UserMainCtrl', function($scope, $window, $timeout, $state, ipCookie, Subscriber, HMPUser){
	//$scope.user = {name:'Manoj Fixme'};
	// $scope.givenName = "blah";
	// $scope.givenEmail = "";
	// $scope.givenPassword = "";
	//debug('UserMainCtrl called');
	if (HMPUser.isLoggedId()){
		$state.go('userLanding');
	}
	$scope.register = function (givenName, givenEmail, givenPassword) {
		debug('register func called ', givenName, givenEmail, givenPassword);
		var newUser = new Subscriber();
		newUser.name = givenName;
		newUser.email = givenEmail;
		newUser.passwd = givenPassword;
		newUser.$register({}, function(value, responseHeaders){
			//debug('value from register', value);
			if(value.result != "Success"){
				$scope.subscriptionStatus = "Registration Failed - " + value.message + ". Please fix the problem and try again.";
				return;
			}
			$scope.subscriptionStatus = "Registration is successful. Please wait as we do auto-login for you!";
			HMPUser.login(value);
			$scope.$emit('loginEvent', {});
			$timeout(function(){
				$scope.subscriptionStatus = "";
				//$route.reload();
				//$window.location.href = '/user/index.html';
				$state.go('userLanding');
			},3000);
		}, function(responseHeaders){
			$scope.subscriptionStatus = "We are sorry. Something went wrong. Could you please try again ?";
		});
	};

	$scope.login = function (givenEmail, givenPassword) {
		$scope.loginError = '';
		Subscriber.login ( {}, {'email': givenEmail, 'passwd':givenPassword}, function (value, responseHeaders){
			//debug('login response' , value, responseHeaders);
			if(value.result=='Success'){
				HMPUser.login(value);
				$scope.$emit('loginEvent', 'some junk');
				//debug('main controller emitted login event');
				//$window.location.href = '/user/index.html';
				$state.go('userLanding');
			} else{
				// something was wrong. login was not successful
				$scope.loginError = value.message;
			}
			
		}, function (httpResponse){
			debug ('login error response', httpResponse);
			$scope.loginError = "Something went wrong. Please try agian.";
		});
	};

}).
controller('HomeCtrlDefault', function($scope, $window, $timeout, $state, ipCookie, Subscriber, HMPUser, Consultation, CwfEvent, fmoment){
	//var authUserAccount = ipCookie('hmp_account');
	//debug('authuseraccount, scope', authUserAccount, $scope);
	// debug('HomeCtrlDefault invoked');
	$scope.providerList = Subscriber.getDefault();
	// debug('$scope.providerList', $scope.providerList);

	var currTime = fmoment();    
    var oneDayFuture = fmoment().add(1, 'days');
    var oneDayPast = fmoment().subtract(2, 'days');
    console.log('currtime',currTime.format(),'onedaypast',oneDayPast.format(),'onedayfuture',oneDayFuture.format() );
	if (HMPUser.isLoggedId()){
		// $scope.apptList = Subscriber.getAppointments(function(){
		// 	$scope.unfinishedApptList = $scope.apptList.filter(function(apptObj){
		// 		debug('currApptFilterFn invoked', apptObj.apptWF);
		// 		if(apptObj.apptWF){
		// 			return apptObj.apptWF.apptStatus == 1;
		// 		} else{
		// 			return true;
		// 		}
		// 	});
		// 	console.log('unfinished appt list', $scope.unfinishedApptList);
		// });
		
		refreshDashboard();

		
		
	}

	function refreshDashboard(){
		$scope.apptList = Consultation.user_appts(function(){
			$scope.lastRefreshedTS = fmoment().format("[today] ddd, h:mm:ss A"); ;
			$scope.unfinishedApptList = $scope.apptList.filter(function(apptObj){
				//debug('currApptFilterFn invoked', apptObj.apptWF);
				if(apptObj.apptWF){
					return apptObj.apptWF.apptStatus == 1;
				} else{
					return true;
				}
			});
			// console.log('unfinished appt list', $scope.unfinishedApptList);
		});
	}

	$scope.currApptFilterFn = function(apptObj){
		//debug('currApptFilterFn0 invoked');
		// if(apptObj.apptWF && apptObj.apptWF.requestedTS)
		// 	debug('currApptFilterFn1 invoked, requestedTS is', apptObj.apptWF );
		if(apptObj.apptWF){
			if( [2,3,4,5].indexOf(apptObj.apptWF.apptStatus) >= 0 ){
				// check if the appointment day is within +/- 1 day
				if(apptObj.apptWF.requestedTS){
					var tmpApptTime = apptObj.apptWF.requestedTS;
					//debug('currApptFilterFn1.5 invoked, requestedTS is', tmpApptTime );
	                if(!tmpApptTime) return false;
	                //debug('currApptFilterFn2 invoked, requestedTS is', tmpApptTime );
	                if ( fmoment(tmpApptTime).isBetween(oneDayPast, oneDayFuture, 'd') ){
	                    return true;
	                }

	                // if payment is not complete, we should try to show in main page
	                if(!apptObj.paymentWF || apptObj.paymentWF.paymentStatus != 3){

	                	// see if it is very recent old or in future then show. don't show if it is older than 2 days
	                	if(fmoment(tmpApptTime).isAfter(oneDayPast)) return true;

	                } 

	                // otherwise don't show
	                return false;
				} else{
					return false;
				}
				
			} else{
				return false;
			}
		} else{
			return false;
		}
	}

	// $scope.unfinishedApptFilterFn = function(apptObj){
	// 	//debug('currApptFilterFn invoked' );
	// 	if(apptObj.apptWF){
	// 		return apptObj.apptWF.apptStatus == 1;
	// 	} else{
	// 		return true;
	// 	}
	// }

	$scope.gotoCRoom = function (apptObj) {
		debug('appt obj for gotoCRoom', apptObj);
		$state.go('croom', {appt:apptObj});
	}

	$scope.confirmApptAtProposedTime = function (apptObj) {
		console.log("appt will be confirmed at proposed time");
			var newCwfEvent = new CwfEvent();
            newCwfEvent.cref = apptObj._id;
            newCwfEvent.eventName = 'ConfirmByUser';
            

            newCwfEvent.$save(function(result){
                console.log('event saved', result);
                $scope.$emit('actionEvent', 'Confirming changed appointment time');
                //apptObj.apptWF.apptStatus = 3;
                if(result.result=="Success"){
                	console.log('refreshing the dashboard after confirming');
	                setTimeout(function(){
	                    refreshDashboard();
	                },2000);
                } else {
                	console.log("Failed");
                	$scope.$emit('actionEvent', 'Could not confirm appointment. Please try again.');
                }
                
                
            });
	}

	$scope.removeUnfinishedAppt = function (apptObj) {
		debug('removing this appt', apptObj);

		apptObj.$set_apptWFState({
	            cref: apptObj._id,
	            aptWFCd: 6
	        },
	        function(value, responseHeaders) {
	            console.log('appt deleted', value);
	            $scope.$emit('actionEvent', 'Unfinished Appointment Deleted');
	            newUnfinishedList = $scope.unfinishedApptList.filter(function(oneApptObj){
					//console.log('will remove it later');
					return apptObj._id != oneApptObj._id;
				});
				$scope.unfinishedApptList = newUnfinishedList;
	        },
	        function(httpResponse) {
	            console.log('appt not deleted. something wrong with the server', httpResponse);
	        });
		

	}
	
}).
controller('DocProfileCtrl', ['$scope', '$window', '$timeout', '$state', 'Subscriber', 'HMPUser','ProviderProfile',function($scope, $window, $timeout, $state, Subscriber, HMPUser, ProviderProfile){
	//var authUserAccount = ipCookie('hmp_account');
	//debug('authuseraccount, scope', authUserAccount, $scope);
	debug('DocProfileCtrl invoked', $state.params.docId);
	//var provider = Subscriber.getProvider({providerId:$state.params.docId});

	$scope.userIsProvider = false;
	$scope.provider = ProviderProfile.get({providerId:$state.params.docId});

	//$scope.provider = provider;
	HMPUser.setProvider($scope.provider);
	//debug('provider information', $scope.provider);
	$scope.beginWF = function (){
		if ( HMPUser.isLoggedId() ) {
			$state.go ('appt', {'docId':$state.params.docId});
			
		} else {
			$state.go('login');
		}
		
	}

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
}]).
controller('ConsultationListCtrl', function($scope, Consultation, fmoment){
	//var authUserAccount = ipCookie('hmp_account');
	//debug('authuseraccount, scope', authUserAccount, $scope);
	// console.log('ConsultationListCtrl invoked');
	var sortByApptTime = function(apptObjX, apptObjY){
		if(! apptObjX.apptWF ){
			// when apptWF object is not yet set, for ex, when user did not save the first page of appointment
			return -1;
		}

		if(! apptObjY.apptWF ){
			// when apptWF object is not yet set, for ex, when user did not save the first page of appointment
			return 1;
		}
        if (apptObjX.apptWF.confirmedTS){
            if(apptObjY.apptWF.confirmedTS){
                // we are good to proceed with time checks
                var timeX = fmoment(apptObjX.apptWF.confirmedTS);
                var timeY = fmoment(apptObjY.apptWF.confirmedTS);
                if(timeX.isBefore(timeY))
                    return 1;
                else if(timeX.isAfter(timeY))
                    return -1;
                else return 0;
                
            } else return 1;
        } else
            return -1;
    }
	$scope.apptList = Consultation.user_appts(function(){
			$scope.lastRefreshedTS = fmoment();
			$scope.timeSortedApptList = $scope.apptList.sort(sortByApptTime);
			// console.log('all consultation appt list', $scope.timeSortedApptList);
		});
	

	
	
}).
controller('CwfCtrl', function($scope, $window, $timeout, $state, $stateParams, Subscriber, HMPUser, SubscriberDoc, Consultation, CwfEvent, fmoment){

	console.log('cwfctrl invoked');
	var cref = $stateParams.cref;
	var newApptFlow = $stateParams.new_appt_flow;
	var providerId = $stateParams.docId;
	var cwf;
	if(cref){
		// consultation wf instance already exists, load it
		cwf = Consultation.get_cwf({cref:cref});
		// debug('consultation object fetched', cwf);
		$scope.wf = cwf;
		$scope.newApptFlow = newApptFlow;
		$scope.wf.$promise.then(function(){
			$scope.wf.requestedTS = fmoment().add(1, 'days').format();
		});

	} else{
		// // first create a consultation WF instance for reference
		// var wf = new Consultation();
		// var initialConsultation = wf.$begin({'providerId':providerId});
		// initialConsultation.$promise.then(function(cwfObj){
		// 	cwf = cwfObj;
		// 	$scope.wf = cwf;

		// })

	}
	
	console.log('new appt flow stateparams',$stateParams, $state );

	function refresh(){
		cwf = Consultation.get_cwf({cref:cref});
		// debug('consultation object fetched', cwf);
		$scope.wf = cwf;
	}

	// max date on the datepicker
    
    var threeMonthsFuture = fmoment().add(3, 'months');
    $scope.untilDate = threeMonthsFuture.format();
    

	// debug('CwfCtrl called with cref', cref);
	

	// $scope.saveCwfState = function(){
	// 	console.log('saving cwf state');
	// 	if(cwf){
	// 		$scope.$emit('actionEvent', 'Saving Appointment details changes');
	// 		cwf.$save(function(wf){
	// 			console.log('cwf state saved', cwf);
	// 			$scope.$emit('actionEvent', 'Appointment changes saved');
	// 		});
	// 	} else{
	// 		// this is 
	// 	}
		
	// };

	$scope.confirmCwf = function(thisWf){
		console.log("appt will be confirmed at proposed time");
		var newCwfEvent = new CwfEvent();
        newCwfEvent.cref = thisWf._id;
        newCwfEvent.eventName = 'ConfirmByUser';
        newCwfEvent.$save(function(result){
            console.log('confirm appt event saved', result);
            $scope.$emit('actionEvent', 'Confirming changed appointment time');
            //apptObj.apptWF.apptStatus = 3;
            if(result.result=="Success"){
            	console.log('refreshing the consultation');
                setTimeout(function(){
                    refresh();
                },2000);
            } else {
            	console.log("Failed");
            	$scope.$emit('actionEvent', 'Could not confirm appointment. Please try again.');
            }
        });

	};

	$scope.cancelCwf = function(){

		console.log(" implement appt cancel later");
		$timeout(function(){
	       $window.alert("Cancel Appointment feature is coming soon");
	    });


	};
	
	$scope.rescheduleCwf = function(thisWf){
		console.log("appt will be rescheduled to ", thisWf.apptWF.requestedTS);
		// var newCwfEvent = new CwfEvent();
  //       newCwfEvent.cref = thisWf._id;
        //var rescheduledDate = fmoment(thisWf.apptWf.requestedTS);
        //var rescheduledTime = fmoment(thisWf.apptWf.requestedTS);
        //rescheduledDate.hours(rescheduledTime.hours()).minutes(rescheduledTime.minutes());
        var newCwfEvent = new CwfEvent();
        newCwfEvent.cref = thisWf._id;
        newCwfEvent.reschedDT = thisWf.apptWF.confirmedTS;
        newCwfEvent.reschedMsg = "No Reason Provided";
        newCwfEvent.eventName = 'RescheduleByUser';
        console.log("Rescheduling...");
        newCwfEvent.$save(function(result){
            console.log('reschedule appt event saved', result);
            
            //apptObj.apptWF.apptStatus = 3;
            if(result.result=="Success"){
            	console.log('Rescheduling was successful.');
            	$scope.$emit('actionEvent', 'Changed appointment time');
                setTimeout(function(){
                    refresh();
                },2000);
            } else {
            	console.log("Rescheduling Failed");
            	$scope.$emit('actionEvent', 'Could not reschedule appointment. Please try again.');
            }
        });
	};

	$scope.changeOtherInfo = function(thisWf){
		console.log('saving other patient information');
		var newCwfEvent = new CwfEvent();
        newCwfEvent.cref = thisWf._id;
        newCwfEvent.consult_mode_pref = thisWf.meetingWF.meetingType;
        newCwfEvent.patientName = thisWf.patientDetailsWF.patientName;
        newCwfEvent.patientAge = thisWf.patientDetailsWF.patientAge;
        newCwfEvent.patientSex = thisWf.patientDetailsWF.patientSex;
        newCwfEvent.patientPhone = thisWf.patientDetailsWF.patientPhone;
        newCwfEvent.problemSummary = thisWf.patientDetailsWF.answerText[0];
        newCwfEvent.eventName = 'changePatientInfo';
        // console.log("Rescheduling...");
        newCwfEvent.$save(function(result){
            console.log('Patient Info Change sent to server', result);
            
            //apptObj.apptWF.apptStatus = 3;
            if(result.result=="Success"){
            	console.log('Patient Info change was successful.');
            	$scope.$emit('actionEvent', 'Changed patient information');
                setTimeout(function(){
                    refresh();
                },2000);
            } else {
            	console.log("Patient Info change Failed");
            	$scope.$emit('actionEvent', 'Could not change patient information. Please try again.');
            }
        });
		
	};

	$scope.setActiveStep = function(){
		$scope.apptStepState = "active";
		$scope.pmtStepState = "inactive";
		$scope.questStepState = "inactive";
		$scope.meetStepState = "inactive";
		$scope.prescStepState = "inactive";
		$scope.feedbStepState = "inactive";
	};

	$scope.patientQ = function () {
    	cwf.$patient_q({}, function(updatedCwfMsg){
    		console.log('patient questions are saved !');
    		if(updatedCwfMsg.result=="Success"){
    			$scope.$emit('actionEvent', 'Questionnaire Responses Saved');
    			setTimeout(function(){
                    refresh();
                },2000);
    			//$scope.wf = updatedCwfMsg.cwf;
    		}else{
    			$scope.$emit('actionEvent', 'Failed to save questionnaire responses. Please try again');
    		}
    		
    		// $state.go('userLanding');
    	})
    };

    $scope.generateUploadURL = function() {
        setTimeout(function() {
            console.log('generateUploadURL called ! generating upload url....');
            SubscriberDoc.getUploadURL({
                    cref: cwf._id,
                    documentNo:1
                },
                null,
                function(value, responseHeaders) {
                	console.log("upload url for patient doc", value.upload_url);
                    $scope.uploadURL = value.upload_url;
                },
                function(errorHttpResponse) {
                    console.log('error in preparing the file upload');
                });
        });
    };

    $scope.gotoCRoom = function (apptObj) {
		// debug('appt obj for gotoCRoom', apptObj);
		$state.go('croom', {appt:apptObj});
	};

	

	

    
}).
controller('CwfPaymentReturnCtrl', function($scope, $window, $timeout, $state, $stateParams, Subscriber, HMPUser, Consultation){

	// first create a consultation WF instance for reference
	var cref = $stateParams.cref;
	debug('CwfPaymentReturnCtrl called with cref', cref);
	$scope.$emit('actionEvent', 'Appointment '+cref+' payment completed. Proceed to questionnaire.');

    
}).
controller('ApptCtrl', function($scope, $window, $timeout, $state, $stateParams, Subscriber, HMPUser, Consultation, fmoment){

	// first create a consultation WF instance for reference
	var providerId = $stateParams.docId;
	$scope.providerId = providerId;
	$scope.provider = HMPUser.selectedProvider();
	$scope.$emit('actionEvent', 'New Appointment');


	function docTimingPrettyPrint(calStruc){
		var prettyPrintedStr = '';
		var timingVsDays = {}; // for ex, '8 Am to 5 pm': ['mon', 'tue', 'wed'], '10 Am to 2 pm': ['thu', 'fri']
		var days = ['mon','tue','wed','thu','fri','sat','sun'];
		var dayTiming;
		days.forEach(function(entry) {
		    console.log(entry);
		    var dayTiming = calStruc[entry]; // for ex, '8AM to 5 PM'
		    var daysWithSameTiming = timingVsDays[dayTiming]; // for ex, ['mon', 'tue']
		    if(!daysWithSameTiming){
		    	// console.log('new entry', dayTiming);
				timingVsDays[dayTiming] = [entry]; // first entry,'8 Am to 5 pm': ['mon']
			} else{
				// console.log('existing entry push', dayTiming, entry, timingVsDays[dayTiming]);
				timingVsDays[dayTiming].push(entry);
			}

		});

		console.log('timingVsDays', timingVsDays);

		// enumerate and add to prettyPrintedStr
		for (var t in timingVsDays) {

		    if (timingVsDays.hasOwnProperty(t)) {

		        prettyPrintedStr += timingVsDays[t] + " - " + t  + "\n";
		    }
		}

		// console.log('prettyPrintedStr = ', prettyPrintedStr);

		$scope.prettyPrintedDocTiming = prettyPrintedStr;
		    
		 
		
		
	}

	docTimingPrettyPrint($scope.provider.calStruc);
	//$scope.docTiming
	//debug('stateparams object', $stateParams);
	var wf = new Consultation();
	wf.$begin({'providerId':providerId});

	//$scope.$emit('actionEvent', 'New Appointment Ref '+wf.reference);

	//debug("wf object", wf);
	$scope.wf = wf;
	$scope.eventSources = [];
	/* config object */
    $scope.uiConfig = {
      calendar:{
        /*height: 450,
        editable: true,
        header:{
          left: 'title',
          center: '',
          right: 'today prev,next'
        },*/
        defaultView: "agendaWeek"
      }
    };

    // max date on the datepicker
    var currTime = fmoment();
    var oneDay2HourFuture = fmoment().add(1,'days').add(2,'hours').minute(0);    
    var threeMonthsFuture = fmoment().add(3, 'months');
    $scope.untilDate = threeMonthsFuture.format();
    $scope.wf.requestedTS = oneDay2HourFuture.toJSON();
    $scope.wf.requestedT = oneDay2HourFuture.toJSON();
    $scope.wf.requestedD = oneDay2HourFuture.toJSON();
    // $scope.wf.requestedTS = oneDay2HourFuture;
    // $scope.wf.requestedT = oneDay2HourFuture.format("h:mm A");
    // $scope.wf.requestedD = oneDay2HourFuture;

    $scope.wf.consult_mode_pref = 'video';
    console.log("wf.requestedT is ", $scope.wf.requestedT);
    


    $scope.requestAppt = function () {
    	wf.cref = wf.reference;
    	console.log('request appt d and t', $scope.wf.requestedD, $scope.wf.requestedT,'consultation mode',$scope.wf.consult_mode_pref );
    	var requestedDate = fmoment($scope.wf.requestedD);
    	var requestedTime = fmoment($scope.wf.requestedT);
    	requestedDate.hours(requestedTime.hours()).minutes(requestedTime.minutes());
    	$scope.wf.requestedTS = requestedDate;
    	//console.log('composed requstedTS ',requestedDate.toJSON() );
    	//console.log('scopewf', $scope.wf, wf);

    	if( !$scope.wf.patientName 
    		|| !$scope.wf.patientPhone 
    		|| !$scope.wf.consult_mode_pref
    		|| !$scope.wf.age 
    		|| !$scope.wf.sex 
    		|| !$scope.wf.problemSummary ){
    		$scope.errMsg = "Appointment Form is not valid. Please provide all information";
    		console.log("Appointment Form is not valid. Please provide all information");
    		return;
    	}
    	// check that patient's phone number is in correct format

    	PHONE_REGEX = /^\+\d\d?\d{10}?$/; // +, followed by first one or two digit for country code and rest 10 digits for the phone number
    	//PHONE_REGEX.test($scope.wf.patientPhone);
    	if(! PHONE_REGEX.test($scope.wf.patientPhone)){
    		$scope.errMsg = "PhoneNumber must be in this format: +CountryCode 10DigitPhoneNumber. Example +919885566778";
    		return;
    	}

    	$scope.$emit('actionEvent', 'Creating new appointment');
    	wf.$request_appt({}, function(){
    		// debug('patient details saved !');
    		wf.cref = wf.reference;
    		HMPUser.setConsultationWF(wf.cwf);
    		//$state.go('patient_question',{'cref':wf.cref});
    		var mapVal = {'cref':wf.cref,
    			'new_appt_flow':true};
    		console.log('passing the params to consult_wf.payment page', mapVal);
    		$scope.$emit('actionEvent', 'Appointment '+wf.cref+' Created. Proceed to Payment');
    		$state.go('consult_wf.payment',mapVal);
    		
    	});
    };



    $scope.gotoPayment = function () {
    	$state.go('register');
    };
}).
controller('CwfPaymentCtrl', function($scope, $window, $timeout, $state, $stateParams, Subscriber, HMPUser, Consultation, ProviderProfile){

	// cwf payment ctrl - get the provider's fees
	var wfcref = $stateParams.cref;
	console.log('CwfPaymentCtrl invoked', $stateParams);
	$scope.cref = wfcref;
	// $scope.provider = HMPUser.selectedProvider();
	// $scope.providerId = $scope.provider._id;
	// console.log('provider id is', $scope.wf);
	if($scope.wf.$resolved){
		// do nothing, because we have the object now
		console.log('existing wf for payment is resolved ', $scope.wf);
		setupFees($scope.wf.paymentWF);
	} else{
		$scope.wf.$promise.then(function(wf) {
      		$scope.freshWf = wf;
      		// console.log('fresh wf for payment is ', wf);
      		// console.log('fresh provider id is ', wf.provider[0][1]);

      		// $scope.providerProfile = ProviderProfile.get({providerId:wf.provider[0][1]});
      		// $scope.providerProfile.$promise.then(function(profile){
      		// 	$scope.consultationFee = profile.feeStruc.regularFee + profile.feeStruc.platformFee;
      		// 	$scope.discount = - 0;
      		// 	$scope.totalFee = $scope.consultationFee + $scope.discount;
      		// });
			setupFees($scope.freshWf.paymentWF);
      		
    	});
	}

	function setupFees(paymentWf){
		if(paymentWf){
			$scope.consultationFee = paymentWf.ttlExpAmt;
			$scope.discount = - 0;
			$scope.totalFee = $scope.consultationFee + $scope.discount;
		}else{

		}
		// get the user subscriber detail to pre-fill email/address etc on checkout form
		$scope.userSubscriber = Subscriber.getUserSubscriber({userSubscriberId:HMPUser.getId()});
		$scope.userSubscriber.$promise.then(function(){
			console.log('usersubscriber object is ',$scope.userSubscriber );
		});
		
	}

	

	
	// var wf = new Consultation();
	// wf.reference = wfcref;
	// wf.cref = wfcref;
	// $scope.wf = wf;
	
 //    $scope.patientQ = function () {
 //    	wf.$patient_q({}, function(){
 //    		debug('patient questions are saved !');
 //    		$state.go('userLanding');
 //    	})
 //    };
    
}).
controller('PatientQCtrl', function($scope, $window, $timeout, $state, $stateParams, Subscriber, HMPUser, Consultation){

	// first create a consultation WF instance for reference
	var wfcref = $stateParams.cref;
	debug('PatientQCtrl invoked', $stateParams);
	$scope.cref = wfcref;
	$scope.provider = HMPUser.selectedProvider();
	$scope.providerId = $scope.provider._id;
	
	var wf = new Consultation();
	wf.reference = wfcref;
	wf.cref = wfcref;
	$scope.wf = wf;
	
    $scope.patientQ = function () {
    	// $scope.$emit('actionEvent', 'Saving Questionnaire Responses');
    	wf.$patient_q({}, function(){
    		// debug('patient questions are saved !');
    		// $scope.$emit('actionEvent', 'Saving Questionnaire Responses');
    		$state.go('userLanding');
    	})
    };
    
}).
controller('DocCtrl', function($scope, $window, $timeout, $state, $stateParams, Subscriber){
	$scope.docSearchText = $stateParams.searchText;
	$scope.docSearch = function(){
		console.log("todo - do a doc free text search with this text - ", $state.searchText);
	}
});