function debug () {
	console.log.apply(console, arguments);
}

angular.module('userApp', [
  'ui.router','ngResource','providerApp.version','myApp.services',/*'ui.calendar'*/'mgcrea.ngStrap','ipCookie',
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
			controller: 'CwfCtrl'
		}).
		state('consult_wf.appt',{
			url: '^/user/cwf/:cref/appt',
			templateUrl: '/user/partials/consult_wf_appt.html'
		}).
		state('consult_wf.payment',{
			url: '^/user/cwf/:cref/payment',
			templateUrl: '/user/partials/consult_wf_payment.html'
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
}).controller('MenuContainerCtrl', function($scope, $window, $timeout, $state, ipCookie, Subscriber, HMPUser){
	debug('MenuContainerCtrl called');

	$scope.$on('loginEvent', function(event, args) {
		debug('Menubar ctrl received login event');
		initializeUser ();
	});

	function initializeUser(){
		debug('initializeUser from menubar invoked. hmpuser ', HMPUser);
		$scope.authFlag = HMPUser.isLoggedId();
		$scope.userName = HMPUser.getName();
		debug('is user logged in', HMPUser.isLoggedId(), $scope.authFlag,'name',HMPUser.getName() );
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
	debug('UserMainCtrl called');
	$scope.register = function (givenName, givenEmail, givenPassword) {
		debug('register func called ', givenName, givenEmail, givenPassword);
		var newUser = new Subscriber();
		newUser.name = givenName;
		newUser.email = givenEmail;
		newUser.passwd = givenPassword;
		newUser.$register({}, function(value, responseHeaders){
			//debug('value from register', value);
			$scope.subscriptionStatus = "Thank you. We are glad to get your attention and can't wait to let you know as soon as this is ready !";
			HMPUser.login(value);
			$scope.$emit('loginEvent', {});
			$timeout(function(){
				$scope.subscriptionStatus = "";
				//$route.reload();
				//$window.location.href = '/user/index.html';
				$state.go('userLanding');
			},3000);
		}, function(responseHeaders){
			$scope.subscriptionStatus = "Thank you for your interest. Something went wrong and we could not safely store your information. Could you please try again ?"
		});
	};

	$scope.login = function (givenEmail, givenPassword) {
		$scope.loginError = '';
		Subscriber.login ( {}, {'email': givenEmail, 'passwd':givenPassword}, function (value, responseHeaders){
			//debug('login response' , value, responseHeaders);
			if(value.result=='Success'){
				HMPUser.login(value);
				$scope.$emit('loginEvent', 'some junk');
				debug('main controller emitted login event');
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
controller('HomeCtrlDefault', function($scope, $window, $timeout, $state, ipCookie, Subscriber, HMPUser, Consultation, fmoment){
	//var authUserAccount = ipCookie('hmp_account');
	//debug('authuseraccount, scope', authUserAccount, $scope);
	debug('HomeCtrlDefault invoked');
	$scope.providerList = Subscriber.getDefault();
	debug('$scope.providerList', $scope.providerList);

	var currTime = fmoment();    
    var oneDayFuture = fmoment().add(1, 'days');
    var oneDayPast = fmoment().subtract(1, 'days');
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
			console.log('unfinished appt list', $scope.unfinishedApptList);
		});
		
	}

	$scope.currApptFilterFn = function(apptObj){
		//debug('currApptFilterFn invoked' );
		if(apptObj.apptWF){
			if( [2,3,4,5].indexOf(apptObj.apptWF.apptStatus) > 0 ){
				// check if the appointment day is within +/- 1 day
				if(apptObj.apptWF.confirmedTS){
					var tmpApptTime = apptObj.apptWF.confirmedTS;
	                if(!tmpApptTime) return false;
	                
	                if ( fmoment(tmpApptTime).isBetween(oneDayPast, oneDayFuture, 'd') ){
	                    return true;
	                }
	                console.log('currtime wasnt between +/- 1 day');
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

	$scope.removeUnfinishedAppt = function (apptObj) {
		debug('removing this appt', apptObj);
		apptObj.$set_apptWFState({
	            cref: apptObj._id,
	            aptWFCd: 6
	        },
	        function(value, responseHeaders) {
	            console.log('appt deleted', value);
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
}]).
controller('ConsultationListCtrl', function($scope, Consultation, fmoment){
	//var authUserAccount = ipCookie('hmp_account');
	//debug('authuseraccount, scope', authUserAccount, $scope);
	console.log('ConsultationListCtrl invoked');
	var sortByApptTime = function(apptObjX, apptObjY){
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
			console.log('all consultation appt list', $scope.timeSortedApptList);
		});
	

	
	
}).
controller('CwfCtrl', function($scope, $window, $timeout, $state, $stateParams, Subscriber, HMPUser, Consultation){

	// first create a consultation WF instance for reference
	var cref = $stateParams.cref;
	debug('CwfCtrl called with cref', cref);
	var cwf = Consultation.get_cwf({cref:cref});
	debug('consultation object fetched', cwf);
	$scope.wf = cwf;

	$scope.saveCwfState = function(){
		console.log('saving cwf state');
		cwf.$save(function(wf){
			console.log('cwf state saved', cwf);
		});
	}

	$scope.setActiveStep = function(){
		$scope.apptStepState = "active";
		$scope.pmtStepState = "inactive";
		$scope.questStepState = "inactive";
		$scope.meetStepState = "inactive";
		$scope.prescStepState = "inactive";
		$scope.feedbStepState = "inactive";
	}

	

	

    
}).
controller('CwfPaymentReturnCtrl', function($scope, $window, $timeout, $state, $stateParams, Subscriber, HMPUser, Consultation){

	// first create a consultation WF instance for reference
	var cref = $stateParams.cref;
	debug('CwfPaymentReturnCtrl called with cref', cref);

    
}).
controller('ApptCtrl', function($scope, $window, $timeout, $state, $stateParams, Subscriber, HMPUser, Consultation){

	// first create a consultation WF instance for reference
	var providerId = $stateParams.docId;
	$scope.providerId = providerId;
	$scope.provider = HMPUser.selectedProvider();
	debug('stateparams object', $stateParams);
	var wf = new Consultation();
	wf.$begin({'providerId':providerId});

	debug("wf object", wf);
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

    $scope.requestAppt = function () {
    	wf.cref = wf.reference;
    	wf.$request_appt({}, function(){
    		debug('patient details saved !');
    		wf.cref = wf.reference;
    		HMPUser.setConsultationWF(wf.cwf);
    		//$state.go('patient_question',{'cref':wf.cref});
    		$state.go('consult_wf.payment',{'cref':wf.cref});
    		
    	})
    };



    $scope.gotoPayment = function () {
    	$state.go('register');
    };
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
    	wf.$patient_q({}, function(){
    		debug('patient questions are saved !');
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