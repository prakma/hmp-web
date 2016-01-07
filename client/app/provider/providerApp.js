'use strict';

// Declare app level module which depends on views, and components

function debug() {
    console.log.apply(console, arguments);
}



angular.module('providerApp', [
    'ngRoute',
    'ui.router',
    'ngResource',
    'mgcrea.ngStrap',
    'myApp.services',
    'providerApp.version',
    'ipCookie',
    'providerApp.session',
    'providerApp.feedback',
    'providerApp.dashboard',
    'providerApp.profile',
    /*'providerApp.calendar',*/
    'providerApp.croom'
]).
config(['$routeProvider', function($routeProvider) {
    $routeProvider.otherwise({
        redirectTo: '/dashboard'
    });
}]).
config(function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise("/provider/index");
    $stateProvider.
    state('login', {
        url: '/provider/login',
        templateUrl: '/provider/session/login.html'
    }).
    state('chgpass', {
        url: '/provider/chgpass',
        templateUrl: '/provider/session/chgpass.html'
    }).
    state('feedback', {
        url: '/provider/acctreq',
        templateUrl: '/provider/feedback/feedback.html'
    }).
    state('dashboard', {
        // url: '/provider/dashboard',
        templateUrl: '/provider/dashboard/dashboard.html'
    }).
    state('dashboard.current_view', {
        url: '/provider/dashboard/main',
        templateUrl: '/provider/dashboard/current_view.html'
    }).
    state('dashboard.pastappt_view', {
        url: '/provider/dashboard/pastonly',
        templateUrl: '/provider/dashboard/pastappt_view.html'
    }).
    state('dashboard.todayappt_view', {
        url: '/provider/dashboard/todayonly',
        templateUrl: '/provider/dashboard/todayappt_view.html'
    }).
    state('dashboard.futureappt_view', {
        url: '/provider/dashboard/futureonly',
        templateUrl: '/provider/dashboard/futureappt_view.html'
    }).
    state('dashboard.appt_view', {
        url: '/:cref/appt_view.html',
        templateUrl: '/provider/dashboard/appt_view.html',
        params: {appt:{}},
        controller: 'PatientApptCtrl'
    }).
    state('croom', {
        /*url: '/provider/croom',*/
        templateUrl: '/provider/croom/croom.html',
        params: {appt:{}}
    }).
    state('croom_audio', {
        /*url: '/provider/croom',*/
        templateUrl: '/provider/croom/croom_audio.html',
        params: {appt:{}}
    })

}).
directive('myHolder1', function() {
    console.log('myholder1 directive invoked');
    return {
        link: function(scope, element, attrs) {
            attrs.$set('data-src', attrs.myHolder1);
            Holder.run({
                images: element[0]
            });
        }
    };
}).controller('MenuContainerCtrl', function($scope, $window, $timeout, $state, ipCookie, Subscriber, HMPUser) {
    debug('MenuContainerCtrl called');
    // debug('route params', $routeParams, $location, $window.location);

    $scope.$on('loginEvent', function(event, args) {
        debug('Menubar ctrl received login event');
        initializeUser();
    });

    function initializeUser() {
        debug('initializeUser from menubar invoked. hmpuser ', HMPUser);
        $scope.authFlag = HMPUser.isLoggedId();
        $scope.userName = HMPUser.getName();
        $scope.provider = {
            providerId: HMPUser.getId(),
            name: HMPUser.getName()
        }
        debug('is user logged in', HMPUser.isLoggedId(), $scope.authFlag, 'name', HMPUser.getName());
    }

    initializeUser();

    $scope.logout = function() {

        function resetUser() {
            HMPUser.logout();
            initializeUser();
        }

        $timeout(function() {
            Subscriber.logout({}, {}, function() {
                resetUser();
            }, function() {
                resetUser();
            });

            //$route.reload();
            //$window.location.href = '/user/index.html';
            $state.go('login');
        }, 2000);

    }

    if (HMPUser.isLoggedId()) {
        $state.go('dashboard.current_view');
    } else if($window.location.search.indexOf("interest") > 0){
        debug('go to feedback');
        $state.go('feedback');
    } else {
        $state.go('login');
    }

}).controller('ProviderMainCtrl', function($scope, $window, $timeout, $state, ipCookie, Subscriber, HMPUser) {


});