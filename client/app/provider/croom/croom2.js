'use strict';




angular.module('providerApp.croom', ['ngRoute', 'myApp.services'])

// .config(['$routeProvider', function($routeProvider) {
//   $routeProvider.when('/croom', {
//     templateUrl: 'croom/croom.html',
//     controller: 'CRoomCtrl'
//   });
// }])
// .config(function($stateProvider, $urlRouterProvider) {
//     $stateProvider.
//     state('croom', {
//         url: '/provider/croom',
//         templateUrl: '/provider/croom/croom.html'
//     });
// })


.controller('CRoomCtrl', ['$scope', '$window', '$stateParams', 'HMPUser', 'Consultation', 'fPatientQBank','fmoment', function($scope, $window, $stateParams, hUser, Consultation, fPatientQBank, fmoment) {

    var userId; // = "bistri_user_002";
    var userName; // = "Jane Smith";
    var remoteUserId; // = "bistri_user_001";
    var myroom;

    console.log('croom controller for provider called !', $stateParams);
    userId = 'D'+$stateParams.appt.provider[0][1];
    remoteUserId = 'U'+$stateParams.appt.user[0][1];
    function setupPatientDataForDisplay(){
        $scope.appt = $stateParams.appt;
        var questionSize, questionSizeArray = [];
        questionSize = 0 || $scope.appt.patientDetailsWF.questionId.length;
        for (var i = 0; i < questionSize; i++) {
            questionSizeArray.push(i);
        }

        $scope.qLoopHelper = questionSizeArray;
        // console.log('question size array', questionSizeArray);
        // console.log('qid 1', $stateParams.appt.patientDetailsWF.questionId[0]);
        $scope.qbank = fPatientQBank;
        $scope.waitingSince = fmoment($stateParams.appt.apptWF.confirmedTS).fromNow()
    }
    setupPatientDataForDisplay();
    
    // provider_appts
    // $scope.apptList = Consultation.provider_appts();

    userName = hUser.getName();
    userId = 'D'+hUser.getId();
    $scope.patientDesc = $stateParams.appt.patientDetailsWF.patientName;
    


    $window.onBistriConferenceReady = function() {

        console.log('bistri onBistriConferenceReady invoked for provider locally');

        var localStream;
        //var room;

        // test if the browser is WebRTC compatible
        if (!bc.isCompatible()) {
            // if the browser is not compatible, display an alert
            alert("your browser is not WebRTC compatible !");
            // then stop the script execution
            return;
        }

        // initialize API client with application keys
        // if you don't have your own, you can get them at:
        // https://api.developers.bistri.com/login
        bc.init({
            appId: "0ba2e6fb",
            appKey: "167e53147b24c7d417a8ad6a29b37297",

            userId: userId,
            userName: userName,
            debug: true
        });

        /* Set events handler */

        // when local user is connected to the server
        bc.signaling.bind("onConnected", function() {
            // show pane with id "pane_1"
            showPanel("pane_1");
        });

        // when an error occured on the server side
        bc.signaling.bind("onError", function(error) {
            // display an alert message
            alert(error.text + " (" + error.code + ")");
        });

        // when the user has joined a room
        bc.signaling.bind("onJoinedRoom", function(data) {
            console.log('onJoinedRoom received in provider', data);
            // set the current room name
            //room = data.room;
            myroom = data.room;
            // // then, for every single members present in the room ...
            // for (var i = 0, max = data.members.length; i < max; i++) {
            //     // ... request a call
            //     bc.call(data.members[i].id, data.room, {
            //         stream: localStream
            //     });
            // }
        });

        // when an error occurred while trying to join a room
        bc.signaling.bind("onJoinRoomError", function(error) {
            // display an alert message
            alert(error.text + " (" + error.code + ")");
        });

        // when the local user has quitted the room
        bc.signaling.bind("onQuittedRoom", function(room) {
            // reset the current room name
            //room = undefined;
            myroom = undefined;
            // show pane with id "pane_1"
            showPanel("pane_1");
            // stop the local stream
            bc.stopStream(bc.getLocalStreams()[0], function(stream) {
                // remove the local stream from the page
                bc.detachStream(stream);

                // show the remote and local holders again
                showOrHideHolder("#video_local_holder", true);
                showOrHideHolder("#video_remote_holder", true);
            });
        });

        // when a new remote stream is received
        bc.streams.bind("onStreamAdded", function(remoteStream) {
            // hide the local holder
            showOrHideHolder("#video_remote_holder", false);

            // insert the new remote stream into div#video_container node
            bc.attachStream(remoteStream, q("#video_container_remote"));
        });

        // when a local or a remote stream has been stopped
        bc.streams.bind("onStreamClosed", function(stream) {
            // remove the remote stream from the page
            bc.detachStream(stream);
            // if room has not been quitted yet
            if (myroom) { // was room
                // quit room
                bc.quitRoom(myroom);
                myroom = undefined;
            }
        });

        // when a remote user presence status is received
        bc.signaling.bind("onPresence", function(result) {
            console.log('remote user presence detected',result, userId, userName, remoteUserId);
            if (result.presence != "offline") {
                // ask the user to access to his webcam and set the resolution to 640x480
                bc.startStream("320x240:12", function(stream) {
                    // when webcam access has been granted
                    // show pane with id "pane_2"
                    showPanel("pane_2");
                    // hide the local holder
                    showOrHideHolder("#video_local_holder", false);
                    // insert the local webcam stream into the page body, mirror option invert the display

                    bc.attachStream(stream, q("#video_container_local"), {
                        mirror: true
                    });
                    // invite user
                    myroom = getRandomRoomName();
                    bc.call(result.id, myroom, {
                        stream: stream
                    });
                });
            } else {
                alert("The user you try to reach is currently offline");
            }
        });

        // when a call request is received from remote user
        // bc.signaling.bind("onIncomingRequest", function(request) {
        //     // ask the user to accept or decline the invitation
        //     if (confirm(request.name + " is inviting you to join his conference room. Click \"Ok\" to start the call.")) {
        //         // invitation has been accepted
        //         // ask the user to access to his webcam and set the resolution to 640x480
        //         bc.startStream("640x480", function(stream) {
        //             // when webcam access has been granted
        //             // show pane with id "pane_2"
        //             showPanel("pane_2");
        //             // set "localStream" variable with the local stream
        //             localStream = stream;
        //             // insert the local webcam stream into the page body, mirror option invert the display
        //             bc.attachStream(stream, q("#video_container"), {
        //                 mirror: true
        //             });
        //             // then join the room specified in the "request" object
        //             bc.joinRoom(request.room);
        //         });
        //     }
        // });

        // // bind function "callUser" to button "Call XXX"
        // q("#call").addEventListener("click", callUser);

        // // bind function "stopCall" to button "Stop Call"
        // q("#quit").addEventListener("click", stopCall);

        // open a new session on the server
        bc.connect();
    };

    $scope.callUser = function(){
        // check remote user presence
        bc.getPresence(remoteUserId);
    };

    $scope.stopCall = function(){
        // quit the current conference room
        if(myroom)
            bc.quitRoom(myroom);
    };
    function getRandomRoomName() {
        var chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_";
        var randomId = "";
        for (var i = 0; i < 20; i++) {
            randomId += chars.charAt(Math.random() * 63);
        }
        // return a random room name
        return randomId;
    }

    function showPanel(id) {
        // var panes = document.querySelectorAll(".pane");
        // // for all nodes matching the query ".pane"
        // for (var i = 0, max = panes.length; i < max; i++) {
        //     // hide all nodes except the one to show
        //     panes[i].style.display = panes[i].id == id ? "block" : "none";
        // };
    }

    function showOrHideHolder(id, showFlag) {
        var holder = document.querySelector(id);
        holder.style.display = showFlag ? "block" : "none";

        // for (var i = 0, max = panes.length; i < max; i++) {
        //     // hide all nodes except the one to show
        //     panes[i].style.display = panes[i].id == id ? "block" : "none";
        // };
    }

    function q(query) {
        // return the DOM node matching the query
        return document.querySelector(query);
    }

}]);

// // when button "Call XXX" has been clicked
// function callUser() {
//     // check remote user presence
//     bc.getPresence(remoteUserId);
// }

// // when button "Stop Call" has been clicked
// function stopCall() {
//     // quit the current conference room
//     bc.quitRoom(room);
// }

