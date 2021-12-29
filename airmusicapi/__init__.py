"""
Support for Lenco DIR150BK and other Airmusic based Internet Radios.
"""
import logging
import requests
import xmltodict


class airmusic(object):
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
        self.send_cmd('stop')
        self.send_cmd('exit')

    def __repr__(self):
        """!
        @private
        Return a string representation of the Airmusic API instance, showing the most important variables.
        """
        ret = ""
        ret += "Airmusic API"
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
        # Send the command to the device. The Basic Authentication values are hardcoded.
        result = requests.get('http://{}:{}/{}'.format(self.device_address, port, cmd),
                              auth=('su3g4go6sk7', 'ji39454xu/^'),
                              params=params,
                              timeout=self.timeout)
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
        Initialise session and select the communication language.
        The GUI on the device will show messages in the selected language.
        The same is valid for the content of specific tags.
        @param language holds the communication language, eg. en, fr, de, nl, ...
        """
        resp = self.send_cmd('init', params=dict(language=language))
        # <result><id>1</id><lang>en</lang> ... </result>
        self.language = resp['result']['lang']
        self.hotkey_fav = resp['result']['hotkey_fav']
        self.push_talk = resp['result']['push_talk']
        self.play_mode = resp['result']['PlayMode']
        self.sw_update = resp['result']['SWUpdate']
        return resp

    def get_hotkeylist(self):
        """!
        Fetch the list of hotkeys.
        It is possible to store multiple stations in the favourites list.
        The first five entries are the hotkeylist.
        This function will retrieve only those five entries. To fetch the complete list,
        it is required to query with the 'list' command.
        @return On success, a dict of favourite stations; On error, a dict {'error': 'reason'}; else None
        """
        resp = self.send_cmd('hotkeylist')
        if 'menu' in resp:
            return resp['menu']
        if 'result' in resp:
            return dict(result=resp['result']['rt'])
        return None

    def get_playinfo(self):
        """!
        Return information about the song being played.
        """
        resp = self.send_cmd('playinfo')
        return resp['result']

    def play_hotkey(self, keynr):
        resp = self.send_cmd('playhotkey', params=dict(key=keynr))
