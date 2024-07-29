E4 for Developers > E4 streaming server > Data Streaming Packets

Data Streaming Packets
Data Format Specification
Updated January, 2019
After a successful connection and stream subscription to an Empatica Device the client starts receiving sensor data from the server.

Stream Data Format
<STREAM_TYPE> <TIMESTAMP> <DATA>

Example:
E4_Gsr 123345627891.123 3.129
Data Streams
The available data streams are:

E4_Acc - 3-axis acceleration
E4_Bvp - Blood Volume Pulse
E4_Gsr - Galvanic Skin Response
E4_Temp - Skin Temperature
E4_Ibi - Interbeat Interval
E4_Hr - Heartbeat
E4_Battery - Device Battery
E4_Tag - Tag taken from the device (by pressing the button)
Timestamp
The timestamp for the sample in seconds defined as time interval between the sample received and the reference date, 1 January 1970, GMT. The value contains a fractional part to represent microseconds.

The sample timestamps are calculated with reference to the first packet received by the E4 streaming server. Upon reception of the first packet, the system timestamp is recorded and the sample timestamps of the first and any further packets are calculated from the reference timestamp and the sample frequency of the respective stream.
Since the E4 starts streaming once the BTLE connection is established, the E4 streaming server starts receiving packets even without any TCP clients subscribed to streams.

Data
Each stream type has a different data format as described below:

Acceleration Data
The acceleration value for x axis. The x axis is defined by the vector whose starting point is set to the center of the device and whose direction points towards the USB slot.
The acceleration value for y axis. The y axis is defined by the vector whose starting point is set to the center of the device and whose direction points towards the shorter strap.
The acceleration value for z axis. The z axis is defined by the vector whose starting point is set to the center of the device and whose direction points towards the bottom of the device.
Example:
E4_Acc 123345627891.123 51 -2 -10
Blood Volume Pulse Data
The value of the BVP sample. The value is derived from the light absorbance of the arterial blood. The raw signal is filtered to remove movement artifacts.

Example:
E4_Bvp 123345627891.123 31.128
Galvanic Skin Response Data
The value of the GSR sample. The value is expressed in microsiemens.

Example:
E4_Gsr 123345627891.123 3.129
Temperature Data
The value of the temperature sample in Celsius degrees. The value is derived from the optical temperature sensor placed on the wrist.

Example:
E4_Temperature 123345627891.123 35.82
Interbeat Interval Data
The value of the IBI sample. The value is the distance from the previous detected heartbeat in seconds.

Example:
E4_Ibi 123345627891.123 0.822
Heartbeat Data
The value of the detected heartbeat, returned together with the interbeat interval data.

Example:
E4_Hr 123345627891.123 142.2156
Battery Level Data
The battery level of the device. Values: [0.0 - 1.0]

Example:
E4_Battery 123345627891.123 0.2
Tag Data
The tags taken from the device.

Example:
E4_Tag 123345627891.123
Having trouble with Empatica E4 software for Developers? Contact Support and we’ll help you sort it out.