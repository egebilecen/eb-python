This repo contains classes/wrappers to work with <b>Drones</b> that uses MAVLink, <b>image processing</b>,  <b>servo and ESC motor</b> control on Raspberry PI and <b>some sensors</b>.
(More detailed information about classes and methods can be found in <b>eb</b> folder and it's subfolders. Only external dependencies are written across all documentation.) 

# libs.txt
Consists the links of the libraries that is needed for my classes to work. Make sure to check it because not all of the libraries are needed if you are not going to use every class.

# Brief of Main Classes
(Those classes are located under "<b>eb/</b>" folder.)
<br><br>
<b>camera.py</b>

* Captures the frame(s) from connected camera device asynchronously.

<br>
<b>compass.py</b>

* Consists methods to work with compass degrees.

<br>
<b>convert.py</b>

* Consists methods to convert values. Such as converting byte array to ascii.

<br>
<b>file.py</b>

* Consists methods to work with files. Such as listing files in a directory.

<br>
<b>i2c.py</b>

* Depends on <a href="https://pypi.org/project/smbus2/">smbus2</a>.
* Consists methods to work with I2C communication protocol.

<br>
<b>logger.py</b>

* Consists methods to print debug messages. Can also save logs into a file.

<br>
<b>math.py</b>

* Consists methods to work with 2D points and basic value manipulation.

<br>
<b>method.py</b>

* Consists methods to work with methods. Such as executing given method as param in background, calling the same function until it returns (or NOT returns) the desired value with an option to timeout and delay the execution the same method after each try, calling the same function X times, etc...

<br>
<b>serialport.py</b>

* Depends on <a href="https://pypi.org/project/pyserial/">pyserial</a>.
* Consists methods to work with serialport.

<br>
<b>time.py</b>

* Consists methods to get timestamp, date, clock, etc...

<br>
<b>udp_client.py</b>

* Consists methods to connect to a UDP server. (Automatically responds to any "ping" message from server with "pong". You may want to uncomment that line.)

<br>
<b>udp_client.py</b>

* Consists methods to create a UDP server. (Automatically sends "ping" message to all sockets in specified time interval to check whether they are disconnected.)

# Brief of Drone Classes
(Those classes are located under "<b>eb/drone/</b>" folder.)
<br><br>
<b>action.py</b>

* Consists methods that requires drone to take an action. Such as going to GPS coordinates, landing, arming, etc... (Changing desired speed(s), yaw and things similar to these also counts as an action. At least for me. :P)

<br>
<b>control.py</b>

* Consists methods to control drone position, altitude, etc...

<br>
<b>convert.py</b>

* Consists methods to convert enum numbers to string or a custom class representative value.

<br>
<b>drone.py</b>

* Depends on <a href="https://github.com/ArduPilot/pymavlink/">pymavlink</a>.
* Initializes the connection between drone and computer. It keeps parsing specific mavlink messages in background.
* Consists various methods to communicate with flight controller.

<br>
<b>math.py</b>

* Consists methods to work with GPS coordinates. Such as calculating lat, lon position of the drone from heading and distance, getting relative heading between two GPS coordinates, calculating distance between two GPS coordinates etc...

<br>
<b>mavlink_helper.py</b>

* Depends on <a href="https://github.com/ArduPilot/pymavlink/">pymavlink</a>.
* Consists methods to get constants that is defined by pymavlink with more ease.

<br>
<b>mission.py</b>

* Companion computer controlled mission system. Allows user to execute python scripts while being allowed to control drone position. Drone will be held in it's present GPS coordinates while executing mission script.
* <b>Note: </b> This class doesn't load any mission(s) to drone.

<br>
<b>reference.py</b>

* pymavlink's mavutil constants and methods reference. And some other references.

<br>
<b>telemetry.py</b>

* Consists methods to get drone's various informations. Such as GPS position, last heartbeat, arm status, flight mode etc...

# Brief of Image Processing Classes
(Those classes are located under "<b>eb/image_processing/</b>" folder.)
<br><br>
<b>color.py</b>

* Consists class definations for color types to make working with them easier.

<br>
<b>define.py</b>

* Consists definations for specific colors in specific color spaces. Such as RED color values in HSV color space.

<br>
<b>detection.py</b>

* Consists methods to detect specific things on a frame. Such as blob detection, corner detection, circle detection, etc...

<br>
<b>image.py</b>

* Consists methods to work with images. For example encoding raw image to .JPG format.

<br>
<b>util.py</b>

* Consists utility methods to make working on image processing easier. Such as filtering neighbor points, extracting information from point list (such as compass bearing between camera center point and the target point), getting closest point to the center, etc...

# Brief of Raspberry Classes
(Those classes are located under "<b>eb/raspberry/</b>" folder.)
<br><br>
<b>motor/esc.py</b>

* Class for control a brushless motor via ESC.

<br>
<b>motor/servo.py</b>

* Class for control a servo motor.

<br>
