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
        switch(status){
          case 1:
            return 'Meeting Pending';
          case 2:
            return 'Meeting In Progress';
          case 3:
            return 'Meeting Completed';
          default:
            return 'Not started';
        }

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
}])
.filter('cwfStateTransitionAllowed', [function() {
  /**
  tells true/false if the given action is "valid/possible" given the current state/status of cwf object ( ie, ConsultationWF object)
  */
  return function(cwf, userActionName) {
    var possibleActions = {
      apptCreateByUser: true,
      apptRescheduleByUser: true,
      apptRescheduleByProvider: true,
      apptConfirmByUser: true,
      apptConfirmByProvider: true,
      apptCancelByUser: true,
      apptCancelByProvider: true,
      cwfPaymentByUser:true,
      cwfGoToAdditionalQuestionsByUser: true,
      cwfGoToMeetingRoomByUser: true,
      cwfGoToMeetingRoomByProvider: true,
      cwfPrescriptionUploadByProvider: true,
      cwfFeedbackByUser:true,
      cwfFeedbackByProvider:true,
      cwfDoneByUser:true,
      cwfDoneByProvider:true
    };

    //console.log(userActionName, 'checking if this user Action is allowed', cwf);
    if(! cwf ) return false; // if cwf object is not resolved yet, don't show any action buttons
    switch(userActionName){
      
      case 'apptCreateByUser':
        return true;

      case 'apptRescheduleByUser':
        if(cwf.overallStatus < 3){
          if(cwf.meetingWF && cwf.meetingWF.meetingStatus){
            if(cwf.meetingWF.meetingStatus == 1 || cwf.meetingWF.meetingStatus > 3)
              return true;
          }else{
            return true;
          }
        }
        return false;
      
      case 'apptRescheduleByProvider':
        // check if appt is not canceled and is not in a terminal state
        // check if the appt is not old, ie, more than 1 day ago
        // then if appt is in "requested or confirmed" state, then allow, otherwise deny
        if(cwf.overallStatus < 3){
          if(cwf.apptWF.apptStatus == 2 || cwf.apptWF.apptStatus == 3 || cwf.apptWF.apptStatus == 4){
            if(cwf.apptWF.requestedTS){
              var notOlderThanOneDay = moment(cwf.apptWF.requestedTS).isAfter(moment().subtract(1,'day'), 'day')
              if(notOlderThanOneDay)
                return true;
            }
          }
        }
        return false;
      
      case 'apptConfirmByUser':

        if(cwf.overallStatus < 3){
          if(! cwf.apptWF){
            return false;
          }
          if(cwf.apptWF.apptStatus == 5){
            // console.log('aptconfirmby user', cwf);
            if(cwf.apptWF.proposedTS){
              var notOlderThanOneDay = moment(cwf.apptWF.proposedTS).isAfter(moment().subtract(1,'day'), 'day')
              if(notOlderThanOneDay)
                return true;
            }
          }
        }
        return false;

      case 'apptConfirmByProvider':
        // check if appt is not canceled and is not in a terminal state
        // check if the appt is not old, ie, more than 1 day ago
        // then if appt is in "rescheduledbyuser" state, then allow, otherwise deny
        if(cwf.overallStatus < 3){
          if(cwf.apptWF.apptStatus == 2 || cwf.apptWF.apptStatus == 4){
            return true;
          }
        }
        return false;

      case 'apptCancelByUser':

        if(cwf.apptWF == null){
            return true;
        }
        if(cwf.overallStatus < 3){
          if(cwf.apptWF.apptStatus <= 5){

            // check if meeting has not happened
            if(cwf.meetingWf == null){
              return true;
            }
            if(cwf.meetingWf.meetingStatus < 3){
              return true
            }
          }
        }
        return false;
      break;

      case 'apptCancelByProvider':
        // check if appt is not canceled and is not in a terminal state
        // check if the appt is not old, ie, more than 1 day ago
        // then if appt is in "rescheduledbyuser" state, then allow, otherwise deny
        if(cwf.overallStatus < 3){
          if(cwf.apptWF.apptStatus < 6){
            // check if meeting has not happened
            if(cwf.meetingWf == null){
              return true;
            }
            if(cwf.meetingWf.meetingStatus < 3){
              return true
            }
          }
        }
        return false;

      case 'cwfPaymentByUser':
        return cwf.paymentWF && cwf.paymentWF.paymentStatus != 3

      case 'cwfGoToAdditionalQuestionsByUser':
        return cwf.paymentWF && cwf.paymentWF.paymentStatus == 3;
      case 'cwfGoToMeetingRoomByUser':
        if(cwf.overallStatus < 3){
          if(cwf.paymentWF && cwf.paymentWF.paymentStatus == 3){
            if(cwf.apptWF.apptStatus == 3){
              if(cwf.apptWF.confirmedTS){
                var within4HrTimeWindow = moment(cwf.apptWF.confirmedTS)
                  .isBetween(
                    moment().subtract(4,'hour'), 
                    moment().add(4,'hour'), 
                  'hour');
                if(within4HrTimeWindow){
                  return true;
                }
              }
            }
          }
          
        }
        return false;

      case 'cwfGoToMeetingRoomByProvider':
        // check if appt is not canceled and is not in a terminal state
        // check if the appt time is confirmed.
        // check if the appt time is within +/- 4 hours 
        if(cwf.overallStatus < 3){
          if(cwf.apptWF && cwf.apptWF.apptStatus == 3){
            if(cwf.apptWF.confirmedTS){
              var within4HrTimeWindow = moment(cwf.apptWF.confirmedTS)
                .isBetween(
                  moment().subtract(4,'hour'), 
                  moment().add(4,'hour'), 
                'hour');
              if(within4HrTimeWindow){
                return true;
              }
            }
          }
        }
        return false;

      case 'cwfPrescriptionUploadByProvider':
      break;

      case 'cwfGoToPrescriptionByUser':
      return cwf.fullfillmentWF && cwf.fullfillmentWF.fulfillmentStatus == 3;

      case 'cwfFeedbackByUser':
      break;

      case 'cwfFeedbackByProvider':
      break;
      
      case 'cwfDoneByUser':
        // console.log('cwf overallStatus', cwf.overallStatus, cwf.meetingWF.meetingStatus);
        if(cwf.overallStatus < 3){
          // console.log('cwf overallStatus2', cwf.overallStatus, cwf.meetingWF.meetingStatus);
          if(cwf.meetingWF && cwf.meetingWF.meetingStatus == 3){
              return true;
          }
        } 
        return false;
      
      case 'cwfDoneByProvider':
        if(cwf.overallStatus < 3){
          if(cwf.apptWF && cwf.apptWF.apptStatus < 6){
            if(cwf.meetingWF && cwf.meetingWF.meetingStatus < 3){
              return true
            }
          }
        } 
        return false;
      
      default:
        return false;

    }
    return false;
  };
}]);
