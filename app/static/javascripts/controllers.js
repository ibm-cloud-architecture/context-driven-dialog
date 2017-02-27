var theCtrls = angular.module('Ctrls', [ 'ngRoute','ui.bootstrap', 'ngMaterial', 'ngCookies']);

var app = angular.module('DDApp');

var assessment={}

app.config(['$routeProvider',
  function($routeProvider) {
    // present the list of projects, and the ability to add new project
    $routeProvider.when('/dd',{
      templateUrl: 'partials/Main.html',
      controller: 'HomeCtrl'
    });
    $routeProvider.when('/dialog',{
      templateUrl: 'partials/Dialog.html',
      controller: 'DialogCtrl',
      resolve : {
        a : function(ddService) {
          return ddService.getAssessment();
        }
      }
    });
    $routeProvider.when('/login',{
      templateUrl: 'partials/Login.html',
      controller: 'HomeCtrl'
    });
    $routeProvider.otherwise({redirectTo: '/login'});
  }
]);

/**
 * The first controller is supporting the home page view, with the following
 * functions:
 * - query entry form and ask button
 */
theCtrls.controller('HomeCtrl',  ['$scope', '$rootScope', '$location','ddService','$http','$sce', '$mdDialog', '$cookies',
      function ($scope,$rootScope,$location,ddService,$http,$sce,$mdDialog,$cookies) {		
      // Check if a username has been provided. Prompt for one if this is not the case
      //if ($cookies.get('username') === undefined) {

		if ($scope.introduction === undefined){
			$http.get("data/intro.json").then(function(response) {
		          $scope.introduction= $sce.trustAsHtml(response.data.content);
	      },function(error) {
	    	  return [];
	      });
		}
		$scope.title="Context Driven Dialog";
		$rootScope.username=$cookies.get('username')
      
      // when user pushes the login button in /login
      $scope.showLoginPrompt = function(ev) {
        var confirm = $mdDialog.prompt()
          .title('Please enter your username')
          .textContent('This simulates a login dialog box')
          .placeholder('Login info')
          .ariaLabel('Login info')
          .initialValue('Bill')
          .ok('Sign in')
          .cancel('Use defaults');
          
        $mdDialog.show(confirm).then(function(username) {
          $cookies.put('username', username);
          $location.path('/dd');
        }, function() {
          $cookies.put('username', 'Bill');
          $location.path('/dd');
        });
      };
      
      // when user clicks logout
      $rootScope.logout = function() {
        $cookies.remove('username');
        $location.path('/')
      };
      
	  // when user pushes query button
	  $scope.helpMe = function(query) {
				 var cq={}
				 cq.userId=$cookies.get('username');
				 cq.firstQueryContent=query;
				 $http({
					    method:'POST',
						url:'/dd/api/a/classify',
						data: cq,
						headers: {'Content-Type': 'application/json'}	
				 }).then(function(response){
					 if (response.data.error) { 
						 alert(response.data.error);
						 $location.path('/dialog');
						 return false;
					 }
					 assessment=response.data;
					 ddService.setAssessment(assessment);
					 $location.path('/dialog');
				     },function(error) {
						alert("Query failed.");
						 $location.path('/dialog');
				   }); 
				};
      }	
]);// home ctrl

theCtrls.controller('DialogCtrl',  ['$scope','$location','ddService','$http','$cookies',
    function ($scope,$location,ddService,$http,$cookies) {
       		$scope.title="Assessing...";
       		$scope.assessment=ddService.getAssessment()
       		$scope.question=$scope.assessment.nextQuestion;
       		$scope.showButton=true;
       		$scope.response={};
    	 	if ($scope.question){
    	 		$scope.response.questionLabel=$scope.question.label;
    		}
        $scope.recommendations=[]
    	 	
    	 	$scope.assess = function(r) {
    	    	$scope.assessment.lastResponse=r;
    	    	$scope.assessment.nextQuestion={}
    	    	$http({
    			    method:'POST',
    				url:'/dd/api/a',
    				data: $scope.assessment,
    				headers: {'Content-Type': 'application/json'}	
    	    	}).then(function(response){
    	    			$scope.assessment=response.data;
    			 		$scope.response={};
    			 		//$location.path('/dialog');
    			 		$scope.question=$scope.assessment.nextQuestion;
    		       		$scope.response.questionLabel=$scope.question.label;
    			 		if ($scope.assessment.status === "Completed") {
    			 			$scope.recommendations=$scope.assessment.recommendations;	
    			 			$scope.question.type="text";
    			 			$scope.showButton=false;
    			 		}

    		  		},function(error) {
    					alert("Query failed.");
    				}); 
        }
    } // constructor                  
]);
	

