/*
 * This class is the management of the websocket communication on the client side.
 */
var websocket = {

    onReady: function() {
        /*
         * Just initializing some variables.
         */
        websocket.opened = false;
        websocket.local = true;

        $('#dialog-box-general .bt_ok').click(function () {
            $('#dialog-overlay, .dialog').hide();
        });
    },

    create_websocket: function(host, port, openfunction ) {
        /*
         * This function creates a websocket. It receives by argument the host and port to be used and
         * an opening function (different pages open websockets that require different opening actions)
         */

        if (host == '') {			//if no host is given the connection is local.
            host = '127.0.0.1';	//local address
            websocket.local = true;
        }

        if (typeof MozWebSocket != "undefined") {	//for mozzila firefox
            websocket.ws = new MozWebSocket("ws://"+host+":"+port);
        }
        else if (window.WebSocket) {					//for other browsers that support websockets
            websocket.ws = new WebSocket("ws://"+host+":"+port);
        }
        else{										//if the browser doesn't support websockets
            alert("This Browser does not support WebSockets.")
        }
        //when the websocket opens it fires the opening function received by argument.
        websocket.ws.onopen =  openfunction;

        //when the websocket receives a message, that message is redirected to the correspondent function (by eval).
        websocket.ws.onmessage =  function(evt) {
          var data = evt.data.split("\t");
          var func = data[0];
          var arg = data.slice(1);
          console.log(arg.toString())
          eval(func+"("+arg.toString()+")");		//all messages should be in this format: class.function(argument)
        };

    },

    send_request: function(request, argument) {
        /*
         * This function receives a request from the user and sends it to the websocket.
         */
        if (websocket.opened == true) {	//only sends the request if the websocket is already opened.
            console.log("websocket opened")
            websocket.ws.send(request + "\t" + argument + "\n");
        } else {
            console.log("websocket isn't ready");
        }
    },

    close: function(data) {
        /*
         * Close the websocket.
         */
        websocket.send_request("DISCONNECT", "");
        websocket.ws.close();
    },

    test_ws: function(data) {
        /*
         * Function to test the websocket.
         */
        //alert("this is a test!")
    }

};

$(document).ready( websocket.onReady );
