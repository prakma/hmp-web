'use strict';

// Declare app level module which depends on views, and components

function debug() {
    console.log.apply(console, arguments);
}



angular.module('providerApp', [
    'ngRoute',
    'ui.router',
    'ngResource',
    'myApp.services',
    'providerApp.version',
    'ipCookie',
    'providerApp.session',
    'providerApp.dashboard',
    'providerApp.profile',
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
    state('dashboard', {
        url: '/provider/dashboard',
        templateUrl: '/provider/dashboard/dashboard.html'
    }).
    state('croom', {
        /*url: '/provider/croom',*/
        templateUrl: '/provider/croom/croom.html',
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

    $scope.$on('loginEvent', function(event, args) {
        debug('Menubar ctrl received login event');
        initializeUser();
    });

    function initializeUser() {
        debug('initializeUser from menubar invoked. hmpuser ', HMPUser);
        $scope.authFlag = HMPUser.isLoggedId();
        $scope.userName = HMPUser.getName();
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
        $state.go('dashboard');
    } else {
        $state.go('login');
    }

}).controller('ProviderMainCtrl', function($scope, $window, $timeout, $state, ipCookie, Subscriber, HMPUser) {


});