# FG777controller


## About
FlightGear Boeing 777 Controller for android

This application allows control the [Boeing 777](http://wiki.flightgear.org/Boeing_777) Airplane  from the [Flightgear](http://www.flightgear.org/) Flight Simulator, read usage for proper configuration.


![Apk Panel](https://s31.postimg.org/tess898xn/fg777controller.png)


## Control Features:
-----------------
* Steering with virtual pad or accelerometer
* Elevator trim
* Rudder
* Throttle (left and right engine)
* Flaps
* Speed brake
* Gear
* Parking brake
* Reverse
* brakes
* auto brake
* views
* lights
* autopilot

This are specific controllers for the Boeing 777, but it  can be used to control other aircrafts for basic usage, like:  steering,rudder, throttle (one or two engines), gear, brakes, lights.


## Usage:
------
1. Install/running FlightGear ([Site link](http://www.flightgear.org))
2. Install/Select Boeing 777 ([download link](http://fgfs.goneabitbursar.com/official/777.zip))
1. Copy the xml files (from_fg777controller.xml,to_fg777controller.xml) from this repository and place  in the  `FlightGear-installation-Directory`/Protocol` directory.
2. Run the FlighGear with the following configuration parameters:
  * From command line:
        
        `fgfs --generic=socket,in,20,,9009,udp,from_fgcontroller777 \
        --generic=socket,out,5,android-device-ip,9010,udp,to_fgcontroller777 \ 
        --telnet 9000`

  * Or Use FGRun to set the required parameters via Advanced > Input/Output menu.
  
  **Obs**: Change **android-device-ip** with your local IP Wi-Fi network device.

3. Install the apk from the bin directory (debug version).
4. Go to the Settings (upper left corner button) and enter the IP of your computer running FlightGear


## Development Requirements
------------------------

This application was developed with python kivy that can runs on Linux, Windows, OS X, Android and iOS.

### Requirements:

* python (2.7)
* Kivy (used 1.9.1)
* plyer (used 1.2.4)
* twisted (used 13.2)
* jnius (used 1.1)


Before run on PC uncomment the line `Window.size = (960, 540)` or use other resolution with the same ratio.
It can be run under the android kivy luncher app ([here](https://play.google.com/store/apps/details?id=org.kivy.pygame&hl=pt)).
