# python-airmusicapi
Python based API to control Airmusic based Internet Radios.

Verified against:
  - Lenco DIR150BK

Inspired by:
  - https://github.com/tabacha/dabman-api

Required python libs:
  - requests
  - lxml (via apt-get)
  - xmltodict

# Sample usage

See file tests.py for more details.

A quick application to retrieve the device's given name:
```python
from airmusicapi import airmusic

IPADDR = '192.168.2.147'
TIMEOUT = 1 # in seconds

am = airmusic(IPADDR, TIMEOUT)
print('Name: %s' % am.friendly_name)
```

# API documentation
The API methods are documented inline with Python docstrings.  
For processing with Doxygen, keywords like @param, @return, etc. are applied.  
Other documentation generators or IDEs can probably process the docstrings as well.

The airmusic-api is written on the lowest level. The device can be controlled by sending
commands to it. These commands are handled in the airmusic class. For each command a
method is implemented, sending the specific command to the radio device and returning
the response to the caller of the method.

# XML-syntax
## XML or not XML, that is the question
The device communicates with an XML like syntax. Unfortunately it is not handling special
characters in the proper way. For instance, assume a song is being played on the radio and
this song is performed by two artists. It is quite common that the names of the artists
are combined with the & (ampersand) character. For example, 'Simon & Garfunkel'. If the
command 'playinfo' is sent to the radio and returns the name of the artists, it might
contain the special character like this ampersand. Unfortunately, the device does not
escape this special character. For that reason, the usual xml-decoders cannot handle the
tagged data sent by the radio properly.  
Simply replacing any ampersand character by the escaped representation would help to decode the
xml-reply, but will potentially harm properly stated ampersands in other parts of the reply.

Also, in a few instances, a command will not return an XML reply, but an HTML page. This
is the case for example with the set_dname command. Some might argue that HTML can be regarded
as xml as well, but also here we have the issue with special characters not being escaped!

## Some examples of XML replies
The responses seem to follow a pattern. In most cases the command will return a 'result'
tag, with nested sublevels of tagged information.

### Example: Start playing a radio station with ID=75_2
The command to send is **play_stn?id=75_2**.
The xml-formatted reply, on success, wil be:
~~~xml
<?xml version="1.0" encoding="UTF-8"?>
<result><id>91_6</id><isfav>0</isfav></result>
~~~
Then the API will return a Python dict, holding the **id** and the **isfav** tagged data.

### Example: Retrieve the hotkeylist
There are several lists of favourites, eg. for FM, DAB or Internet radio stations.
But there is one overall list of favourites. The Infrared Remote has a few numbered buttons to select one from this list directly.
To retrieve the overall list, command **hotkeylist** must be sent to the device.
The reply will reveal how many items there are in this list, how many of them are returned in the actual
respone and, of course, the items themselves.
The response will look like this (edited for readability):
~~~xml
<?xml version="1.0" encoding="UTF-8"?>
<menu>
	<item_total>5</item_total>
	<item_return>5</item_return>
	<item><id>75_0</id><status>emptyfile</status><name>Leeg</name></item>
	<item><id>75_1</id><status>emptyfile</status><name>Leeg</name></item>
	<item><id>75_2</id><status>emptyfile</status><name>Leeg</name></item>
	<item><id>75_3</id><status>emptyfile</status><name>Leeg</name></item>
	<item><id>75_4</id><status>emptyfile</status><name>Leeg</name></item>
</menu>
~~~
There is no 'result' tag. Instead the 'menu' tag holds all tagged data.
One interesting thing to note is the content of the 'name' tag: **Leeg**.
While using the **hotkeylist** command, the device responded in the language 'nl' (as instructed at the **init** command).
That is why the content of this name tag is in Dutch. In English, it would contain *Empty*, in German *Leer*, etc.
Only for this example the Dutch language was selected, but in all other parts of the API description it is assumed
that the language is English (init?language=en).
And by the way, the API will return a Python dict holding **item_total**, **item_return** and (a list/array) of the five **item** entries. Each item holds a Python dict with the tags **id**, **status** and **name**.

# The API in operation
## Initialization and termination
The device will not allow some commands to work properly if the **init** command is omitted.
Likewise, if no more communication is needed, it is required to send the **exit** command.
Therefore it is recommended that all implementations on top of this API will start by calling the **init()** method, including the **language** value.
The API itself, on termination (i.e. destruction of the class instance, implemented in the '\__del__' method), will send the **exit** command.

I also noticed that the device starts to act strange if it is controlled by more than one application at the time.
For example, I was using the Airmusic Control App on my phone and at the same time I was trying
commands in the browser. Same holds when I was running the 'tests.py' sample script and used that App simultaneously.

The **init** and **exit** commands do not create resp. close a session with the device. Therefore the
device cannot distinct between commands coming from the Python API or the phone App.
Changing the volume by program code and doing the same at the device does not seem to harm.

## Menu navigation and song/station selection
The device can be controlled by means of the buttons on the device, by the Infrared Remote or by the (wireless) network interface.
The airmusic API implementation communicates via that interface with the device. It is funny to see that the device will show navigation actions on its display, even when the network interface is used to control it.
But it is a great help to understand the actions that can be taken at a certain point in the menu structure.

It has been notied as well that simply using navigation commands, and bypassing intermediate steps to go
from a certain menu level to another, that the device might respond with an error message, or even stop
responding at all. In the latter case the only solution to get the device back and responsive is to perform
a power cycle. Even the buttons on the device will not function is such a case.

Building an application on top of the API should follow the menu navigation as if the user is using the
buttons on the device or the Infrared Remote. Always, the initial menu must be retrieved. Then it is possible
to 'enter' only into those submenus available in this menu. After entering a submenu, the content of this submenu can be retrieved.
And then history repeats: 'Enter' only a submenu of this menu.
To retrieve the menu content, use **get_menu()**. To enter a (sub-)menu, use the method **enter_menu()**.

### Menu ID
All menus have their own unique ID. The main menu is known as ID=1. The ID value of other menus must be retrieved by fetching the menu content and reading the id-tag of the (sub-)menu.
The **get_menu()** and **enter_menu()** methods need the ID of the menu to retrieve or enter.
As mentioned before, it is important to enter a sub-menu that is part of the current menu, otherwise the device might freeze!

#### DIR150BK Menu overview
The device used in my experiments, a Lenco DIR150BK, seems to have a menu structure like this (not complete):
~~~text
1=Main → 8 items
	87=Local Radio (content) → 128 items
		87_1=100% NL Radio (file)
		87_2=538 Radio (file)
		87_3=538 Top 50 (file)
		87_4=AmorFM (file)
		  :
		87_128=...
	52=Internet Radio (content) → 5 items
		75=My Favorite (content)  → 8 items
			75_0=C-Dance RETRO (file)
			75_1=Empty (emptyfile)
			  :
			75_7=SLAM! (file)
		71=Radio Station/Music (content) → 4 items
			71_1=100% NL Radio (file)
			71_2=538 Radio (file)
			71_3=538 Top 50 (file)
			71_4=AmorFM (file)
		87=Local Radio (content) → @see (1)→(87)
		59=History (content) → 7 items
			59_0=SLAM! (file)
			59_1=Radio Orbital 101.9 FM (file)
			  :
			59_6=Sky Radio Hits (file)
		4=Service (content) → hangs when trying
	2=Media Center (content) → hangs when trying
		122=USB (content)
			122_1= mp3 file on USB stick
			  :
		8=UPnP (content)
	5=FM (content)
	3=Information Center (content)
	47=AUX (content)
	104=Bluetooth (content)
	6=Configuration (content) → hangs when trying
~~~
In this structure, the value in front of the equal sign (eg **1**=Main) is the unique menu ID. The menu name is given after the equal sign.
After the menu name is indicated how many items (submenus) are found. Note that the content of a menu can differ, for example when it holds the list of radio stations.
Below the menu name, indented, is the sub-menu level.
Sometimes, a submenu points to another (higher) menu. That is indicated with @see. For example, from the main menu (ID=1) I can navigate into the 'Internet Radio' menu (ID=52).
That menu contains also the item 'Local Radio' with ID=87. This is actually the samen menu as from the main menu. This way the device allows to jump from the 'Internet Radio' menu directly to the 'Local Radio' menu, without the need to go one level up first.

To understand the difference between an entry being a sub-menu or a radio station/file/song, the menu entry is commented with **(content)** or **(file)** respectively. These values can be retrieved from the 'status' tag that is part of the tagged structure returned with **get_menu()**.
This difference is important, because a sub-menu can be selected by calling **enter_menu()** and specifying the ID found for that menu entry.
A song/station/file can be played by calling **play_station()** and specifying the song/station/file ID.
Note that the ID for playing has an main ID, an underscore and a subnumber. The main ID is the ID of the menu in which it was found.
The subnumber is the sequence number of the song/etc in that menu.
This way all stations/etc will be assigned a unique ID (as the menu itself has a unique ID).
In the given menu structure, item **75_0** points to a radio station called **C-Dance RETRO**.
Note: If **play_station()** is called with an existing ID, eg 75_0, but the active menu of the device is not menu 'My Favorite' (ID=75), the device might freeze.

## Song status
With the **get_playinfo()** method it is possible to retrieve 'live' information about the song or station playing at that moment.
The information made available depends on the type of media being played.
Different information will be available when playing an MP3 file from an USB stick, compared with listening to
an FM radio station. But the tags returned by the device will be the same.
I have noticed that right after selecting an internet radio station the song information is rather short.
In that situation the tags 'artist' and 'song' are even not present.
Fortunately, the device is helping a bit by mentioning the play status of a song, station, etc by returning two tags, 'sid' and 'status'.
The **'status'** tag holds a human readable text, in the selected language.
The **'sid'** tag holds a numeric value and seems to indicate the same as the 'status' tag.
So far I have 'decoded' the following values for the 'sid' tag:

| sid | Meaning                  |
|-----|--------------------------|
|  1  | not playing              |
|  2  | buffering                |
|  5  | buffer at 100%             |
|  6  | playing song/station     |
|  7  | ending playing song/file |
|  9  | paused                   |
| 12  | reading song from file   |
| 14  | failed to connect   |

### Example output
The following XML formatted output was retrieved while I was listening to the SLAM Internet radio station.
Note: Omitted are the xml version and result tags. This output is what tags **get_playinfo()** returns.

~~~xml
<vol>5</vol>
<mute>0</mute>
<status>Bezig met Afspelen </status>
<sid>6</sid>
<logo_img>http://192.168.xxx.yyy:8080/playlogo.jpg</logo_img>
<stream_format>MP3 /128 Kbps</stream_format>
<station_info> SLAM</station_info>
<song>Housuh in de Pauzuh XL</song>
<artist>SLAM!</artist>
~~~
 
 The tag **logo_img** holds an URL to a small image. In the example above it points to the logo of the radio station.
 When playing an MP3 file, the image is the album art of that song.
 
# Authentication
The device requires HTML Basic Authentication, but so far it looks like the user and password are hardcoded.
As the credentials are base64 encrypted data, it is easy to decode them.
> See RFC7617 for more details on Basic Authentication, https://datatracker.ietf.org/doc/html/rfc7617

Wireshark traces showed the following text in the HTML Authorization header: **c3UzZzRnbzZzazc6amkzOTQ1NHh1L14=**
Decoding it:
~~~bash
~$ echo 'c3UzZzRnbzZzazc6amkzOTQ1NHh1L14=' | base64 -d; echo
su3g4go6sk7:ji39454xu/^ 
~$
~~~
As the username and password fields are separated by a ':', this learns us the username=su3g4go6sk7 and the password=ji39454xu/^.

# Alternative ways to access the device
For those that do not want to use this Python based API, they can use a browser, the command line or a script in for instance Bash syntax.
For example, the airmusic API has the **get_systeminfo()** method to retrieve the software version and (wireless) network configuration information.

**By browser**
The same information can be retrieved by opening a browser and typing **http://< ip of device>/GetSystemInfo** in the address bar.
Depending on which browser is used, the xml-formatted response will be shown as-is, or will be somehow interpreted. To be able to see all returned data, it is suggested to use the 'view-source' function in the browser.

**By command line**
On the command line, the system information can be retrieved using:
~~~bash
~$  curl -H 'Authorization: Basic c3UzZzRnbzZzazc6amkzOTQ1NHh1L14=' http://<ip of device>/GetSystemInfo
~~~

# How to discover the airmusic commands
As mentioned above, the airmusic API implementation was created based on information gathered from other pages, like the one from https://github.com/tabacha/dabman-api
I have verified this implementation against the Lenco DIR150BK radio. But it looks like different models can
have a slight different implementation (more or less commands). Therefore it is interesting to know how to
discover the commands and other details from your specific device yourself.

There are probably many ways to get to the same result, like there are roads to Rome.

What I have done is the following.
I have downloaded the Airmusic Control App on my smartphone.
Both the smartphone and the device, the Airmusic based radio, must be on the same subnet, otherwise the app cannot discover the device.
Once the App and the device were connected, I started to play a bit with this App, to ensure it worked fine.
The next App I started is the Package Capture App. Here I started the capture on the Airmusic app.
Then I switched back to the Airmusic Control app and pressed buttons, navigated through menus, made 'mistakes' on purpose to see error messages, etc. Finally I quit the Airmusic Control App.
Then, switching back to the Capture App, I checked which captures were found. Those captures on the UDP protocol were not interesting. These are there due to SSDP Discovery of the device.
> For more reading on SSDP discovery, there is a good article by Danny Buckley at https://medium.com/@danny.jamesbuckley/ssdp-how-to-find-local-devices-a24f73ce4262
A tiny Python implementation by Dan Krause can be found at https://gist.github.com/dankrause/6000248.

Only those on the TCP protocol showed the (HTML) commands and replies.
In the capture app the relevant (TCP) captures were saved, with .pcap at the end of the name, in the downloads folder.
With a cable between PC and smaprtphone I copied the *.pcap files from phone to PC.
The .pcap files can be examined with the Wireshark application.

Another idea would be to have a second wireless interface connected to the PC.
This second interface needs to be setup as an AP.
> If you want to allow the device (and the smartphone) to access internet via that AP, make sure your PC has internet access and routing is enabled.
How to setup an AP and how to make a router of your PC is out of scope here.
Maybe it is enough to setup the AP as bridge. See https://github.com/oblique/create_ap for details.

Then the Airmusic device and the smartphone must be setup to connect to this AP.
With Wireshark on that same PC it will be possible to see the communication between phone and Airmusic device 'live'.
In Wireshark, the captured data can be saved as well in .pcap format.
