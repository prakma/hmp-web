'use strict';

angular.module('providerApp.version.interpolate-filter', [])

.filter('interpolate', ['version', function(version) {
  return function(text) {
    return String(text).replace(/\%VERSION\%/mg, version);
  };
}])
.filter('cwfFilter', [function() {
  return function(status, cwfObjectType) {
  	var statusTxt;
  	switch(cwfObjectType){
  		case 'appt':
  			//# 1 = not started, 2 = requested, 3 = confirmed , 4 = new time rescheduled by user, 5 = new time proposed by provider, 6 = canceled by user, 7 = canceled by provider
  			switch(status){
  				case 1:
  					return 'Not Started';
  				case 2:
  					return 'Requested';
  				case 3:
  					return 'Confirmed';
  				case 4:
  				case 5:
  					return 'Reschedule Requested';
  				case 6:
  				case 7:
  					return 'Canceled';
  				default:
  					return status;
  			}
  			break;
  		
      case 'payment':
  			switch(status){
  				case 1:
  					return 'Not Paid';
  				case 2:
  					return 'Payment In-Process';
          case 3:
            return 'Payment Done';
          case 4:
            return 'Payment Rejected';  
  				default:
  					return 'Payment Status - Unknown';
  			}
  		break;
  		
      case 'meeting':
  		break;
      
      case 'fullfillment':
        switch(status){

          case 1:
            return 'Not Uploaded';
          
          case 3:
            return 'Prescription Available';
          default:
            console.log('prescription status', status);
            return 'Prescription Status - Unknown';
        }
      break;
  		
      default:
  			return status;

  	}

  	
    return status;
  };
}]);
