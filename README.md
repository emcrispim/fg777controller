
# FG777controller


## About
flighgear boeing 777 Controller for android

This application allows control the [boeing 777](http://wiki.flightgear.org/Boeing_777) [Flightgear](http://www.flightgear.org/), read usage for proper configuration.


![Apk Panel](https://s31.postimg.org/tess898xn/fg777controller.png)


## Control Features:
-----------------
* Steering with virtual pad or accelerometer
* Elevator trim
* Rudder
* Throttle (left and right engine)
* Flaps
* Speedbrake
* Gear
* Parking brake
* Reverse
* brakes
* autobrake
* views
* lights
* autopilot

This are specific controllers for the boeing 777, but it  can be used to controll other aircrafts for basic usage like the, steering,rudder, throttle (one or two engines), gear, brakes, lights.


## Usage:
------
1. Install/running Flighgear ([Site link](http://www.flightgear.org))
2. Install/Select Boeing 777 ([download link](http://fgfs.goneabitbursar.com/official/777.zip))
1. Copy the xml files from the xml repository directory to your FlightGear `Protocol` directory 
2. Run the FlighGear with the required parameters:
  * From command line:
        
        fgfs --generic=socket,in,20,,9009,udp,from_fgcontroller777 \
        --generic=socket,out,5,android-device-ip,9010,udp,to_fgcontroller777 \ 
        --telnet 9000

  * Or Use FGRun to set the required parameters in the  via Advanced > Input/Output menu.
  
  **Obs**: Change **android-device-ip** with your local ip Wifi network

3. Install the apk from the bin directory (debug version).
4. Go to the Settings (left up corner button) and enter the IP of your computer running Flighgear


## Development Requirements
------------------------

This application was developed with python kivy that can runs on Linux, Windows, OS X, Android and iOS.

### Requirements:

* python (2.7)
* Kivy (used 1.9.1)
* plyer (used 1.2.4)
* twisted (used 13.2)
* jnius (used 1.1)


Before run on PC uncomment the line `Window.size = (960, 540)` it can be used other resolution with the same ratio.
It can be run under the android kivy luncher app.
