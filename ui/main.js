var main, faces, controls, container;
var rightKey, leftKey, backKey;

var width = window.innerWidth;
var height = window.innerHeight;
var aspect = width / height;
var pos = 0;
var bonePath = 'models/foot-final.json'; //'models/first-foot.json';

(function() {
    'use strict';

    /**
     * This is called from the tween.update function - and
     */
    var onUpdate = function () {

        //main.obj.skeleton.bones[rightKey].rotation.y = this.right_y;
        //main.obj.skeleton.bones[leftKey].rotation.y = this.left_y;

/*
        main.obj.skeleton.bones[backKey].rotation.x = this.back_x;
        main.obj.skeleton.bones[backKey].rotation.y = this.back_y;
        main.obj.skeleton.bones[backKey].rotation.z = this.back_z;
*/
    };


    /**
     * With the tween, it takes rotate_obj.min and moves towards rotate_obj.max during the 3 second loop
     */
    var rotate_obj = {
        reset: {
            left_x: 0,
            left_y: 0,
            left_z: 0,

            right_x: 0,
            right_y: 0,
            right_z: 0,

            back_x: 0,
            back_y: 0,
            back_z: 0
        },
        min: {
            left_x: -0.35,
            left_y: -0.2,
            left_z: -0.35,

            right_x: -0.35,
            right_y: -0.2,
            right_z: -0.35,

            back_x: -0.5,
            back_y: -0.1,
            back_z: -0.5,
        },
        max: {
            left_x: 0.35,
            left_y: 0.2,
            left_z: 0.35,

            right_x: 0.35,
            right_y: 0.2,
            right_z: 0.35,

            back_x: 0.5,
            back_y: 0.1,
            back_z: 0.5
        }
    };

    var tween = new TWEEN.Tween(rotate_obj.max)
        .to(rotate_obj.min, 3000)
        .easing(TWEEN.Easing.Cubic.InOut)
        .yoyo(true)
        .repeat(Infinity)
        .onUpdate(onUpdate);

    main = {

        onReady: function() {
            main.init();
        },

        init: function() {
            websocket.create_websocket(
                window.location.hostname,
                "5500",
                function() {
                    websocket.opened = true;
                    websocket.send_request('BROWSER_READY','\t');
                }
            );

            main.create_object();
        },

        create_object: function() {
            container = $("#container");

            main.scene = new THREE.Scene();

            // Adding a camera
            main.camera = new THREE.PerspectiveCamera( 45, aspect, 1, 10000 );

            // WebGL renderer
            main.renderer = new THREE.WebGLRenderer( { antialias: true, alpha: false } );
            main.renderer.setClearColor( new THREE.Color(0x777777, 1.0) );
            main.renderer.setPixelRatio( window.devicePixelRatio );
            main.renderer.setSize( width, height );
            main.renderer.autoClear = true;
            main.renderer.shadowMapEnabled = true;

            // Position and point the camera to the center of the scene
            main.camera.position.x = 2;
            main.camera.position.y = 2;
            main.camera.position.z = 4;
            main.camera.lookAt(new THREE.Vector3(1, 10, 0));

            // Adding lights
            main.scene.add ( new THREE.AmbientLight( 0xaaaaaa ) );
            var light = new THREE.DirectionalLight( 0xffffff, 0.5 );
            light.position.set( 0, 90, 1200 );
            main.scene.add( light );

            // Append webGl element to container element
            container.append( main.renderer.domElement );

            // instantiate a loader
            var loader = new THREE.JSONLoader();

            // load a resource
            loader.load(
                // resource URL
                bonePath,
                // Function when resource is loaded
                function ( geometry, materials ) {
                    var mat = new THREE.MeshLambertMaterial({color: 0xE8C2C3, skinning: true});

                    main.obj = new THREE.SkinnedMesh( geometry, mat );
                    main.scene.add( main.obj );
                    main.start();
                }
            );
        },

        start: function() {
            // adding controls. with this enabled we can move the object.
            controls = new THREE.OrbitControls( main.camera, main.renderer.domElement );
            controls.target.set( 0, 0, 0 );
            controls.addEventListener('change', main.renderer.render(main.scene, main.camera) );

            main.obj.scale.x = 1;
            main.obj.scale.y = 1;
            main.obj.scale.z = 1;

						console.log(main.obj);

            $.each(main.obj.skeleton.bones, function (key, bone) {
                if (bone.name === 'BottomRight') {
                    rightKey = key;
                } else if (bone.name === 'BottomLeft') {
                    leftKey = key;
                } else if (bone.name === 'BottomBack') {
                    backKey = key;
                }
            });

            tween.start();

            main.render();
        },

        render: function() {
            TWEEN.update();

            // render using requestAnimationFrame
            requestAnimationFrame(main.render);
            main.renderer.render(main.scene, main.camera);
        },

        onWindowResize: function() {
            main.camera.aspect = window.innerWidth / window.innerHeight;
            main.camera.updateProjectionMatrix();
            main.renderer.setSize( window.innerWidth, window.innerHeight );
        },

        getMousePosition: function ( dom, x, y ) {
            var rect = dom.getBoundingClientRect();
            return [ ( x - rect.left ) / rect.width, ( y - rect.top ) / rect.height ];
        },

				fillTable: function(fsr_values){
					for (var i = 0; i < fsr_values.length; i++) {
						$("#fsr"+(i+1)).removeClass();
						if (fsr_values[i] > 60){
							$("#fsr"+(i+1)).addClass('strong');
						}
						else if (fsr_values[i] > 40){
							$("#fsr"+(i+1)).addClass('medium');
						}
						else if (fsr_values[i] > 20){
							$("#fsr"+(i+1)).addClass('light');
						}
						else if (fsr_values[i] > 10){
							$("#fsr"+(i+1)).addClass('very_light');
						}
						$("#fsr"+(i+1)).html(fsr_values[i]+'%');
					}
				},

        getData_ws: function(fsr1,fsr2,fsr3,fsr4,fsr5,fsr6,fsr7,flex1,flex2,g1x,g1y,g1z) {
            /*
             * Data comes from the websocket in a string format.
             */

						 //"HEADER\tFSRS1\tFSRS2\tFSRS3\tFSRB1\tFSRB2\tFSRB3\tFSRH\tFLEX1\tFLEX2\tG1x\tG1y\tG1z"
						//main.setFlex(flex1/90,flex2/90);
						main.setGyro(g1x,g1y,g1z);
						main.fillTable([fsr1,fsr2,fsr3,fsr4,fsr5,fsr6,fsr7]);
        },

				setFlex(f1,f2){
					console.log(f1);
					main.obj.skeleton.bones[rightKey].rotation.x = f1;
					main.obj.skeleton.bones[leftKey].rotation.x = f1;
				},

				setGyro(x,y,z){
					//main.obj.skeleton.bones[rightKey].rotation.x = x;
					//main.obj.skeleton.bones[leftKey].rotation.x = x;

					main.obj.skeleton.bones[rightKey].rotation.y =  main.obj.skeleton.bones[rightKey].rotation.y + z;
					main.obj.skeleton.bones[leftKey].rotation.y =  main.obj.skeleton.bones[leftKey].rotation.y + z;

					//main.obj.skeleton.bones[rightKey].rotation.x = main.obj.skeleton.bones[rightKey].rotation.x + x;
					//main.obj.skeleton.bones[leftKey].rotation.x = main.obj.skeleton.bones[leftKey].rotation.x + x;
				},

        onChangeX: function(angle_x) {
            /*
             * We give to this function the change (in degrees) that we want to apply
             * in the x axis. If the object is rotated at 45º in this axis, and we
             * do onChangeX(45), the object will rotate to 90º
             */
            main.obj.rotation.x = main.obj.rotation.x + (Math.PI * angle_x /180);
        },

        onChangeY: function(angle_y) {
            /*
             * We give to this function the change (in degrees) that we want to apply
             * in the y axis.
             */
            main.obj.rotation.y = main.obj.rotation.y + (Math.PI * angle_y /180);
        },

        onChangeZ: function(angle_z) {
            /*
             * We give to this function the change (in degrees) that we want to apply
             * in the z axis.
             */
            main.obj.rotation.z = main.obj.rotation.z + (Math.PI * angle_z /180);
        }

    };

    $(document).ready(main.onReady);
    $(window).resize(main.onWindowResize);

})();
