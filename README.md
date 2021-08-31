# libs.txt
Consists the links of the libraries that is needed for my classes to work. Make sure to check it because not all of the libraries are needed if you are not going to use every class.

# Brief of Main Classes
(More detailed information can be found in <b>eb</b> folder and it's subfolders.) 
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
