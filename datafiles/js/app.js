var outbitApp = angular.module('outbitApp', [ 'ngRoute', 'outbitControllers', 'satellizer', 'toaster']);

outbitApp.config(['$routeProvider', '$httpProvider', '$authProvider',
  function($routeProvider, $httpProvider, $authProvider) {

      // Login URL
      $authProvider.loginUrl = 'http://127.0.0.1:8088/login';

      // Support Cross-Domain
      $httpProvider.defaults.useXDomain = true;
      delete $httpProvider.defaults.headers.common["X-Requested-With"];

      // Routes
      $routeProvider.
        when('/login', {
         templateUrl: 'templates/login.html',
         controller: 'outbitLoginCtrl',
         resolve: {
            skipIfLoggedIn: skipIfLoggedIn
         }
        }).
        when('/jobs', {
         templateUrl: 'templates/jobs.html',
         controller: 'outbitJobsCtrl',
         resolve: {
            loginRequired: loginRequired
         }
        }).
        when('/actions', {
         templateUrl: 'templates/actions.html',
         controller: 'outbitJobsCtrl',
         resolve: {
            loginRequired: loginRequired
         }
        }).
        when('/user', {
         templateUrl: 'templates/user.html',
         controller: 'outbitJobsCtrl',
         resolve: {
            loginRequired: loginRequired
         }
        }).
        otherwise( {
         templateUrl: 'templates/jobs.html',
         controller: 'outbitJobsCtrl',
         resolve: {
            loginRequired: loginRequired
         }
        });

    // Login Required, redirect to login page
    function loginRequired($q, $auth, $location) {
        var deferred = $q.defer();
        if ($auth.isAuthenticated()) {
            deferred.resolve();
        } else {
            $location.path('/login');
        }
        return deferred.promise;
    }

    // Users Already Logged In, Skip Login
    function skipIfLoggedIn($q, $auth) {
      var deferred = $q.defer();
      if ($auth.isAuthenticated()) {
        deferred.reject();
      } else {
        deferred.resolve();
      }
      return deferred.promise;
    }
  }]);