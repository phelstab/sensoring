E4 for Developers > E4 streaming server > Message Protocol

Message Protocol
and Command Structure
Updated January, 2019
General Message Structure
Messages are ASCII strings terminated with a newline (in Windows '\r\n') character and encoded with UTF-8. Some commands have parameters, which are separated by spaces.

Client requests are in the following format

<COMMAND> <ARGUMENT_LIST>

Example:
device_subscribe gsr ON
Messages from server containing responses to commands are in the following format

<COMMAND> <ARGUMENT_LIST>

Example:
R device_subscribe acc ON
Messages from server containing data from device are in the following format

<STREAM_TYPE> <TIMESTAMP> <DATA>

Example:
G 123345627891.123 3.129
Commands and Responses Details
List of Discovered BTLE Devices (Manual BTLE)
The client requests the list of Empatica E4 devices, that are in range and not connected over BTLE. The server responds with the number of discovered devices and a list of device info. If Manual BTLE is not set, this command is not needed since discovery and connection over BTLE are handled automatically.

Client Request:
device_discover_list

Server Response:
R device_discover_list <NUMBER_OF_DEVICES> | <DEVICE_INFO_1> | <DEVICE_INFO_2> | ...

Example:
R device_discover_list 2 | 9ff167 Empatica_E4 allowed | 740163 Empatica_E4 not_allowed
The format of the device info is the following:

<DEVICE_ID> <DEVICE_NAME> <API_KEY_PERMISSION>

Example:
9ff167 Empatica_E4 allowed
The strings allowed and not_allowed indicate if the devices are allowed to be used with the given API key.

Connect Device over BTLE (Manual BTLE)
The client sends a BTLE connection request for a specific device. The server will connect to the device over BTLE if it has been discovered and if allowed by the API key. If Manual BTLE is not set, this command is not needed since discovery and connection over BTLE are handled automatically.

An optional parameter can be specified, that defines a timeout for BTLE discovery after an accidental disconnection (e.g. device out of range). The device will stay on and be discoverable over BTLE for the specified amount of time. The timeout is an integer number defined in minutes and can be in the range 0-254, where 0 specifies an infinite timeout. If the optional parameter is left out there will be an infinite timeout if Autoreconnect BTLE is set, otherwise there will be no timeout.

The optional timeout parameter only takes effect for devices with a firmware version higher than 1.2.4.x. Devices with lower firmware versions will automatically turn off after an accidental disconnection.

Client Request:
device_connect_btle <DEVICE_ID> [<TIMEOUT>]

Example:
device_connect_btle 9ff167 208
Server Response:
R device_connect_btle OK
R device_connect_btle ERR <reason>

Example:
R device_connect_btle ERR The device has not been discovered yet
Disconnect Device from BTLE
The client sends a BTLE disconnection request for a specific device. The server will disconnect the device from BTLE. This command terminates active connections as well as stops reconnection attempts to devices that have temporarily lost BTLE connection.

Client Request:
device_disconnect_btle <DEVICE_ID>

Example:
device_disconnect_btle 9ff167
Server Response:
R device_disconnect_btle OK
R device_disconnect_btle ERR <reason>

Example:
R device_disconnect_btle ERR The device is not connected over btle
List of Devices Connected over BTLE
The client requests the list of Empatica E4 devices that are in range and connected over BTLE. The server responds with the number of connected devices and a list of device info.

Client Request:
device_list

Server Response:
R device_list <NUMBER_OF_DEVICES> | <DEVICE_INFO_1> | <DEVICE_INFO_2>

Example:
R device_list 2 | 9ff167 Empatica_E4 | 740163 Empatica_E4
The format of the device info is the following:

<DEVICE_ID> <DEVICE_NAME>

Example:
9ff167 Empatica_E4
Connect to a Device
The client sends a connection request to a specific device. The E4 streaming server binds the client connected by TCP to the device connected over BTLE. The bound client needs to subscribe to channels with the device_subscribe command in order to start receiving data.

Each TCP connection is allowed to connect to one Empatica Device at a time. To receive data from multiple devices, multiple TCP connections are required. The TCP connection remains bound to the device regardless of the status of the BTLE connection. However, if the device has lost BTLE connectivity, only then TCP connection has the possibility to bind to another E4 using the "device_connect" connection request. In this case the previous device will be unbound and subscriptions will be cleared.

Client Request:
device_connect <DEVICE_ID>

Example:
device_connect 9ff167
Server Response:
R device_connect OK
R device_connect ERR <reason>

Example:
R device_connect ERR The device requested for connection is not available.
Disconnect from a Device
The client sends a device disconnection request. The client will be disconnected from the currently connected device and close the TCP connection to the E4 streaming server. The device will remain connected to the E4 streaming server over BTLE.

Client Request:
device_disconnect

Server Response:
R device_disconnect OK
R device_disconnect ERR <reason>

Example:
R device_disconnect ERR No connected device.
Subscribe and Unsubscribe to Data Stream
To start or stop receiving data from a given stream, the client sends a data subscription requests specifying the desired stream. The client needs to be first bound to a device with the device_connect command.

Subscriptions persist independent of the BTLE connection status of the device.

Client Request:
device_subscribe <STREAM> <STATUS>

Example:
device_subscribe gsr ON
Server Response:
R device_subscribe <STREAM> <STATUS>
R device_subscribe <STREAM> ERR <REASON>

Example:
R device_subscribe gsr OK
To subscribe to a stream specify ON and to unsubscribe OFF.

STREAM SUBSCRIPTIONS
The available stream subscriptions are:

acc - 3-axis acceleration
bvp - Blood Volume Pulse
gsr - Galvanic Skin Response
ibi - Interbeat Interval and Heartbeat
tmp - Skin Temperature
bat - Device Battery
tag - Tag taken from the device (by pressing the button)
Suspend and Resume Data Streaming
To temporarily suspend and resume the data streaming (without disconnecting or turning off the device), the client sends a pause requests

Client Request:
pause <STATUS>

Example:
pause ON
Server Response:
R pause <STATUS>
R pause ERR <REASON>

Example:
R pause ERR You are not connected to any device
To pause the stream specify ON and to resume OFF.

System Messages
In certain events the E4 streaming server sends an informative system message to the TCP connections.

BTLE Connection Lost
When the E4 streaming server loses connection to a device over BTLE, a disconnection message is sent to all TCP connections that are bound to the device.

Server Message:
R connection lost to device <DEVICE_ID>

Example:
R connection lost to device 9ff167
BTLE Connection Re-Established
When a previously connected device is connected again over BTLE to the E4 streaming server, a connection re-established message is sent to all TCP connections that are bound to the device. This message is sent independent of the setting Autoreconnect BTLE and of how the BTLE connection to the device was dropped.

Server Message:
R connection re-established to device <DEVICE_ID>

Example:
R connection re-established to device 9ff167
Device Turned Off
When a device is turned off by pressing the button, a device turned off message is sent to all TCP connections that are bound to the device. This message is only sent for devices with a firmware version higher than 1.2.4.x.

Server Message:
R device <DEVICE_ID> turned off via button

Example:
R device 9ff167 turned off via button
Protocol Example (no Manual BTLE)
[OPEN TCP CONNECTION]

  ==>  device_list
  <==  R device_list 2 | 9ff167 Empatica_E4 | 7a3166 Empatica_E4

  ==>  device_connect ffffff
  <==  R device_connect ERR the requested device is not available

  ==>  device_connect 9ff167
  <==  R device_connect OK

  ==>  device_subscribe bvp ON
  <==  R device_subscribe bvp OK

  <==  E4_Bvp 123345627891.123 3.212
  <==  E4_Bvp 123345627891.327 10.423
  <==  E4_Bvp 123345627891.472 12.665

  ==>  device_disconnect
  <==  R device_disconnect OK

[EOF]
Protocol Example (Manual BTLE)
[OPEN TCP CONNECTION]

  ==>  device_list
  <==  R device_list 0

  ==>  device_discover_list
  <==  R device_list 2 | 9ff167 Empatica_E4 allowed | 7a3166 Empatica_E4 not_allowed

  ==>  device_connect_btle 7a3166
  <==  R device_connect_btle ERR The device is not registered with the API key

  ==>  device_connect_btle 9ff167
  <==  R device_connect_btle OK

  ==>  device_list
  <==  R device_list 1 | 9ff167 Empatica_E4

  ==>  device_connect 9ff167
  <==  R device_connect OK

  ==>  device_subscribe acc ON
  <==  R device_subscribe acc OK

  <==  E4_Acc 123345627891.123 51 -2 -10
  <==  E4_Acc 123345627891.327 60 -8 -12
  <==  E4_Acc 123345627891.472 55 -16 -1

  ==>  device_disconnect
  <==  R device_disconnect OK

[EOF]
Having trouble with Empatica E4 software for Developers? Contact Support and we’ll help you sort it out.