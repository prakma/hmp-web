function debug () {
	console.log.apply(console, arguments);
}

angular.module('userApp', [
  'ui.router','ngResource','providerApp.version','myApp.services','ui.calendar','ipCookie',
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
			url: '/user/appt/:docProfileId',
			templateUrl: '/user/partials/appt_request.html'
		}).
		state('doc',{
			url: '/user/doc',
			templateUrl: '/user/partials/doctor.html',
			params: {searchText:{}},
			controller: 'DocCtrl'
		}).
		state('doc_profile',{
			url: '/user/doc/:docProfileId',
			templateUrl: '/user/partials/doctor_profile.html'
		}).
		state('patient_question',{
			url: '/user/:cref/questions',
			templateUrl: '/user/partials/patient_qform1.html'
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
		Subscriber.login ( {}, {'email': givenEmail, 'passwd':givenPassword}, function (value, responseHeaders){
			//debug('login response' , value, responseHeaders);
			HMPUser.login(value);
			$scope.$emit('loginEvent', 'some junk');
			debug('main controller emitted login event');
			//$window.location.href = '/user/index.html';
			$state.go('userLanding');
		}, function (httpResponse){
			debug ('login error response', httpResponse);
		});
	};

}).
controller('HomeCtrlDefault', function($scope, $window, $timeout, $state, ipCookie, Subscriber, HMPUser){
	//var authUserAccount = ipCookie('hmp_account');
	//debug('authuseraccount, scope', authUserAccount, $scope);
	debug('HomeCtrlDefault invoked');
	$scope.providerList = Subscriber.getDefault();
	debug('$scope.providerList', $scope.providerList);
	if (HMPUser.isLoggedId()){
		$scope.apptList = Subscriber.getAppointments();
	}

	$scope.gotoCRoom = function (apptObj) {
		debug('appt obj for gotoCRoom', apptObj);
		$state.go('croom', {appt:apptObj});
	}
	
}).
controller('DocProfileCtrl', function($scope, $window, $timeout, $state, Subscriber, HMPUser){
	//var authUserAccount = ipCookie('hmp_account');
	//debug('authuseraccount, scope', authUserAccount, $scope);
	debug('DocProfileCtrl invoked', $state.params.docProfileId);
	var provider = Subscriber.getProvider({providerId:$state.params.docProfileId});
	$scope.provider = provider;
	HMPUser.setProvider(provider);
	debug('provider information', $scope.provider);
	$scope.beginWF = function (){
		$state.go ('appt', {'docProfileId':$state.params.docProfileId});
	}
	
	
}).
/*controller('HomeCtrl4', function($scope, $window, $timeout, $state, ipCookie, Subscriber, HMPUser){
	//var authUserAccount = ipCookie('hmp_account');
	//debug('authuseraccount, scope', authUserAccount, $scope);
	debug('homectrl invoked');
	function initializeUser(){
		debug('initializeUser invoked');
		$scope.authFlag = HMPUser.isLoggedId();
		$scope.userName = HMPUser.getName();
		debug('is user logged in', HMPUser.isLoggedId(), $scope.authFlag,'name',HMPUser.getName() );
	}

	initializeUser();
	

	
	$scope.docSearch = function(){
		console.log("redirect to do a doc free text search with ", $scope.docSearchText);
		$state.go('doc',{searchText:$scope.docSearchText});
	}
	$scope.logout = function () {
		ipCookie.remove('hmp_account',{ path: '/' });
		HMPUser.logout();
		initializeUser();
		$timeout(function(){
			//$route.reload();
			//$window.location.href = '/user/index.html';
			$state.go('userLanding');
		},5000);

	}
}).*/
controller('CwfCtrl', function($scope, $window, $timeout, $state, $stateParams, Subscriber, HMPUser, Consultation){

	// first create a consultation WF instance for reference
	var cref = $stateParams.cref;
	debug('CwfCtrl called with cref', cref);
	var cwf = Consultation.get_cwf({cref:cref});
	debug('consultation object fetched', cwf);
	$scope.wf = cwf;

	

    
}).
controller('ApptCtrl', function($scope, $window, $timeout, $state, $stateParams, Subscriber, HMPUser, Consultation){

	// first create a consultation WF instance for reference
	var providerId = $stateParams.docProfileId;
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
    		$state.go('patient_question',{'cref':wf.cref});
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