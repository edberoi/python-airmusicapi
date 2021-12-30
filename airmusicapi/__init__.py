"""
Support for Lenco DIR150BK and other Airmusic based Internet Radios.
"""
import logging
import requests
import xmltodict


VERSION = '0.0.1'


class airmusic(object):
    """
    This class contains constants ands methods to implement the AirMusic API.
    """

    # The KEY_... constants represent the corresponding key of the InfraRed Remote.
    KEY_HOME = 1
    KEY_UP = 2
    KEY_DOWN = 3
    KEY_LEFT = 4
    KEY_RIGHT = 5
    KEY_ENTER = 6
    KEY_POWER = 7  # Toggle power on/off.
    KEY_MUTE = 8
    KEY_VOLUP = 9  # Volume up one step.
    KEY_VOLDOWN = 10  # Volume down one step.
    KEY_ALARMCLOCK = 11
    KEY_SLEEPTIMER = 12
    KEY_LANGUAGE = 13  # Open the language menu.
    KEY_SCREENDIM = 14  # Toggle screen dim on/off.
    KEY_CHANNELFAV = 15  # Show the favourites menu.
    KEY_BUTTON0 = 17
    KEY_BUTTON1 = 18
    KEY_BUTTON2 = 19
    KEY_BUTTON3 = 20
    KEY_BUTTON4 = 21
    KEY_BUTTON5 = 22
    KEY_BUTTON6 = 23
    KEY_BUTTON7 = 24
    KEY_BUTTON8 = 25
    KEY_BUTTON9 = 26
    KEY_MODE = 28  # Toggle between the device modes: FM, IRadio, USB, AUX, UPNP, ...
    KEY_NEXT = 31  # Go to the next item.
    KEY_PREV = 32  # Go to the next item.
    KEY_USB = 36  # Swith to USB mode.
    KEY_INTERNETRADIO = 40  # Switch to IRadio mode.
    KEY_POWERSAVING = 105  # Go to the power saving menu, item 'Turn On'.
    KEY_EQ_FLAT = 106  # Select "Flat" equaliser mode.
    KEY_SYSTEMMENU = 110  # Go to the system menu.
    KEY_WPS = 111  # Start WPS mode.
    KEY_NEXTFAV = 112  # Go to the next station in the favourites list.

    def __init__(self, device_address, timeout=5):
        """
        Constructor of the Airmusic API class.
        @param device_address holds the device IP-address or resolvable name.
        @param timeout determines the maximum amount of seconds to wait for a reply from the device.
        """
        self.device_address = device_address
        self.timeout = timeout
        logging.basicConfig(level=logging.INFO,
                            format='[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s',
                            filename=('airmusic-debug.log'),)
        self.logger = logging.getLogger("airmusic")
        # Will be updated after successful call to init() command.
        self.language = None
        self.hotkey_fav = None
        self.push_talk = None
        self.play_mode = None
        self.sw_update = None

    def __del__(self):
        """!
        @private
        Finalise the communication with the device by closing the session.
        """
        self.logger = None  # No logging possible at termination.
        self.stop()
        self.send_cmd('exit')

    def __repr__(self):
        """!
        @private
        Return a string representation of the Airmusic API instance, showing the most important variables.
        """
        ret = ""
        ret += "Airmusic API Ver. {}".format(VERSION)
        ret += "\n  address={}".format(self.device_address)
        ret += "\n  timeout={}".format(self.timeout)
        ret += "\n  language={}".format(self.language)
        ret += "\n  hotkey={}".format(self.hotkey_fav)
        ret += "\n  push_talk={}".format(self.push_talk)
        ret += "\n  play_mode={}".format(self.play_mode)
        ret += "\n  sw_update={}".format(self.sw_update)
        return ret

    def __str__(self):
        """!
        @private
        Return a string representation of the Airmusic API instance, showing the most important variables.
        """
        return self.__repr__()

    def send_cmd(self, cmd, port=80, params=None):
        """!
        Send the command and optional parameters to the device and receive the response.
        Most commands will be sent to port 80, but some might require port 8080.
        There are commands that have no parameters. In that case the params parameter can be omitted.
        In case a command requires additional parameters, these must be passed as a dict().
        @param cmd is the command to send.
        @param port is the http port to send the command to. Default is 80.
        @param params holds the command parameters.
        """
        # The parameters for the command, if any, are received in a dict() structure.
        if type(params) is not dict:
            params = dict()
        if self.logger:
            self.logger.debug("Sending: {}".format(cmd))
        # Send the command to the device. The Basic Authentication values are hardcoded.
        result = requests.get('http://{}:{}/{}'.format(self.device_address, port, cmd),
                              auth=('su3g4go6sk7', 'ji39454xu/^'),
                              params=params,
                              timeout=self.timeout)
        if self.logger:
            self.logger.debug("Response: headers={}, text=\"{}\"".format(result.headers, result.text))
        if result.ok:
            return xmltodict.parse(result.text)  # Will fail if a tag contains an &, like combining two artist names.
        else:
            logging.error("Error in request: {} : {}".format(r.status_code, r.reason))
            return None

    # ========================================================================
    # Properties
    # ========================================================================

    # Friendly name
    def get_friendly_name(self):
        """!
        Return the human readable name of the device.
        @return the device name (string).
        """
        resp = self.send_cmd('irdevice.xml')
        # <root><device><friendlyName>...</friendlyName></device></root>
        return resp['root']['device']['friendlyName']

    def set_friendly_name(self, value):
        """!
        Assign a human readable name to the device.
        @param value the device name (string).
        """
        # <root><device><friendlyName>...</friendlyName></device></root>
        return resp['root']['device']['friendlyName']

    friendly_name = property(get_friendly_name, set_friendly_name)

    # log level
    def get_log_level(self, loglevel):
        """!
        Get the actual logging level. See the logging library for level values.
        @return the current log level.
        """
        self.logger.setLevel(loglevel)

    def set_log_level(self, loglevel):
        """!
        Change the logging level. See the logging library for level values.
        Default is logging.INFO level.
        @param loglevel specifies the level at which output to the logger will be activated.
        """
        self.logger.setLevel(loglevel)


    log_level = property(get_log_level, set_log_level)

    # ========================================================================
    # Public methods
    # ========================================================================

    def init(self, language='en'):
        """!
        Initialize session and select the communication language.
        The GUI on the device will show messages in the selected language.
        The same is valid for the content of specific tags.
        It returns the value of several system parameters, being:
         - id (The ID for the main menu),
         - version (The system version),
         - wifi_set_url (URL to start scanning for APs, but its IP address is wrong!),
         - ptver (date part of the version),
         - hotkey_fav (The key of the choosen station in the hotkey list),
         - push_talk (?),
         - leave_msg (?),
         - leave_msg_ios (?),
         - M7_SUPPORT (Flag to indicate if this device has support for the M7 chipset),
         - SMS_SUPPORT (Flag to indicate if SMS is supported),
         - MKEY_SUPPORT (?),
         - UART_CD (?),
         - PlayMode (Represents the current play mode, eg FM, IRadio, ...),
         - SWUpdate (If there is an update available, most of the time value NO).
        @param language holds the communication language, eg. en, fr, de, nl, ...
        @return a dict holding the system parameters and values.
        """
        resp = self.send_cmd('init', params=dict(language=language))
        # <result><id>1</id><lang>en</lang> ... </result>
        result = resp['result']
        self.language = result['lang']
        self.hotkey_fav = result['hotkey_fav']
        self.push_talk = result['push_talk']
        self.play_mode = result['PlayMode']
        self.sw_update = result['SWUpdate']
        return result

    def get_hotkeylist(self):
        """!
        Fetch the list of hotkeys.
        It is possible to store multiple stations in the favourites list.
        The first five entries are the hotkeylist. To fetch the complete list,
        it is required to query with the 'list' command.
        Returned are the following tags:
         - item_total (The total number of items in the list, i.e. 5),
         - item_return (The amount of items in the list),
         - item (repeated (5) times):
        Each item has the following tags:
         - id (Unique ID that can be used to play this station),
         - status ('emptyfile' indicates the entry is not used, 'file' indicates the entry is valid.),
         - name (Holds the station name, if used. Contains 'empty' or a translation of 'empty' if a
                 different language is active).
        @return On success, a dict of favourite stations; On error, a dict {'error': 'reason'}; else None
        """
        resp = self.send_cmd('hotkeylist')
        if 'menu' in resp:
            return resp['menu']
        if 'result' in resp:
            result
            return dict(result=resp['result']['rt'])
        return None

    def enter_menu(self, menu_id):
        """!
        Enter the given submenu.
        Menus in the device have a unique menu-ID. The contents of a menu can be retrieved
        in one go or in chunks with the get_menu() function. To enter a menu entry
        (i.e. an menu entry that is marked as status: content), the submenu unique ID is
        needed.
        @return True on success, False on error; else None
        """
        resp = self.send_cmd('gochild', params=dict(id=menu_id))
        if 'result' in resp:
            new_id = resp['result']['id']
            return new_id == menu_id
        return None

    def get_menu(self, cmd='list', menu_id=1, start=1, count=15):
        """!
        Fetch the list of items in a given menu.
        Menus in the device have a unique menu-ID. The contents of a menu can be retrieved
        in one go or in chunks. The params 'start' and 'count' determine which part of the
        full menu will be retrieved.
        Returned are the following tags:
         - item_total (The total number of items in the menu, eg. 50),
         - item_return (The amount of items returned here, eg. 10),
         - item (a menu entry, repeated (item_return) times):
        Each item has the following tags:
         - id (Unique ID for this menu entry),
         - status ('emptyfile' indicates the entry is not used, 'file' indicates the entry is valid,
                   'content' means there is a sub-menu available.),
         - name (The menu name, if used).
        If retrieving the menu failed, a single dict is returned holding the error reason.
        If no menu was returned by the device, nor an error indication, the function returns None.
        @return On success, a dict of menu entries; On error, a dict {'error': 'reason'}; else None
        """
        resp = self.send_cmd('list', params=dict(id=menu_id, start=start, count=count))
        if 'menu' in resp:
            return resp['menu']
        if 'result' in resp:
            return dict(result=resp['result']['error'])
        return None

    def get_playinfo(self):
        """!
        Return information about the song being played.
        Depending on the connection state, it is possible that not all tags are present.
        For instance, while connecting to a radio station the tags vol, mute and status are present,
        but tags artist, song and so on are not.
        When playing a song/station, the following tags are present:
         - vol (Volume, ranges 0 - 15),
         - mute (Mute flag, 0=Off, 1=On),
         - status (Song or connection status message, in the local language (see init() ),
         - sid (?),
         - logo_img (URL to fetch the logo of the station / song),
         - stream_format (Shows for instance 'MP3 /128 Kbps'),
         - station_info (The name of the station, eg ' SLAM'),
         - song (The name of the song),
         - artist (The artist of the song).
        @return A dict with information about the song/station being played.
        """
        resp = self.send_cmd('playinfo')
        if 'vol' in resp['result']:
            return resp['result']
        else:
            return dict(result=resp['result'])

    def play_hotkey(self, keynr):
        """!
        Start playing a station from the hotkey list.
        The hotkey list is a small list where favourite stations can be stored.
        On the remote control there is a limited set of numbered keys, each representing
        one entry in this list. This function will take the keynr and start to play the
        corresponding favourite station.
        On return:
         - id (The ID of the menu holding this station),
         - rt (The status text, eg 'OK').
        @param keynr is the number of the station, value range: 1 - ?.
        @return A dict with the tags id and rt.
        """
        # <result><id>75</id><rt>OK</rt></result>
        resp = self.send_cmd('playhotkey', params=dict(key=keynr))
        return resp['result']

    def play_station(self, station_id):
        """!
        Start playing a station based on its unique ID.
        The unique station ID can be found using the 'get_menu' command. The format is
        something like 75_3. This function will request the radio to play the
        given station ID.
        Note: It is required to navigate to the menu that holds the station_id. Failure
              to do so will cause the device to hang. A power cycle is needed to get the
              device remote controllable again!
        On return:
         - id (The ID of the menu containing this song/station),
         - rt (The status text, eg 'OK').
        @param station_id is the unique ID of the station to play.
        @return A dict with the tags id and rt.
        """
        # <result><id>75</id><rt>OK</rt></result>
        resp = self.send_cmd('play_stn', params=dict(id=station_id))
        return resp['result']

    def send_rc_key(self, keynr):
        """!
        Simulate a key pressed on the remote control.
        The device comes with an InfraRed Remote. This function can be used to simulate
        a key being pressed on that remote.
        On return:
         - rt (containing the status text, eg 'OK').
        @param keynr is the key on the IR remote control to simulate.
        @return A dict with the tag rt.
        """
        # <result><rt>OK</rt></result>
        resp = self.send_cmd('Sendkey', params=dict(key=keynr))
        return resp['result']

    def stop(self):
        """!
        Stop playing the current song/station.
        A song (file) or a station is stopped playing and the device will return to
        the menu.
        On return:
         - rt (The status text, eg 'OK').
        @return A dict with the tag rt.
        """
        resp = self.send_cmd('stop')
        return resp['result']
