/**
Wrap call to back end in the angular service, and use the resource REST api for that
*/

var theServs = angular.module('Servs', []);



/**
 * Supports to access and cache the list of projects, the current selected 
 * project and the current scoping.
 */
theServs.service('ddService',function($http) {	
	// keep the assessment between controller
	var assessment ={};
	
	var assess = function(a){		
		$http({
		    method:'POST',
			url:'/dd/api/a',
			data: a,
			headers: {'Content-Type': 'application/json'}	
	 }).then(function(response){
		 		assessment=response.data;
	  		},function(error) {
				alert("Query failed.");
			}); 
	 
	};
	
	var setAssessment= function(a) {
		assessment=a;
	};
	
	var getAssessment = function(){
		return assessment;
	}
	
	return {
		assess : assess,
		setAssessment: setAssessment,
		getAssessment: getAssessment
	};
});

