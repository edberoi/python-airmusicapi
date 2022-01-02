"""
Test file to check functionality in Airmusic API towards Lenco DIR150BK.
"""


import json
import logging
import time
from airmusicapi import airmusic


IPADDR = '192.168.2.147'  # Change this to the IP-address or hostname of your device.
TIMEOUT = 5  # in seconds. In most cases 1 second is sufficient.


def print_list(list_result):
    """!
    Show the response from a list command in pretty print format.
    @param list_result contains the result (dict) of the 'list' command.
    """
    if 'result' in list_result:
        print("Error: {}".format(list_result['result']))
        return
    print("List: {} out of {}:".format(list_result['item_total'], list_result['item_return']))
    for entry in list_result['item']:
        print("  {:5} {} -> {}".format(entry['id'], entry['name'], entry['status']))


def print_songinfo(api_ref):
    """!
    Print the song information, as far as it is available.
    @param api_ref is an Airmusic API instance.
    """
    print("Press CTRL-C to interrupt.")

    print("{:3} {:3} {}".format('Vol', 'sid', 'Status'))
    try:
        while True:
            playinfo = api_ref.get_playinfo()
            if 'result' in playinfo:
                print(" ... {}".format(playinfo['result']))
            else:
                status = "{:3} {:3} {} ".format(playinfo['vol'], playinfo['sid'], playinfo['status'])
                if 'artist' in playinfo:
                    status += "Artist:'{}' Song:'{}'".format(playinfo['artist'], playinfo['song'])
                print(status)
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass


def main():
    """
    Main part of the code. Checks some parts of the API against the Lenco DIR150BK radio.
    """
    # Create an API instance and setup initial communication with the device.
    am_obj = airmusic(IPADDR, TIMEOUT)
    am_obj.log_level = logging.DEBUG
    am_obj.init(language="en")

    # Show device information.
    print('Device Name: %s' % am_obj.friendly_name)
    print(json.dumps(am_obj.get_systeminfo(), indent=2))

    # Show volume and mute levels.
    print("Current volume = {}".format(am_obj.volume))
    print("Current mute = {}".format(am_obj.mute))

    # Show the content of the hotkeylist.
    hotkeylist = am_obj.get_hotkeylist()
    print("Hotkeylist: {} out of {}:".format(hotkeylist['item_total'], hotkeylist['item_return']))
    for itm in hotkeylist['item']:
        print("  {}, {}, {}".format(itm['id'], itm['name'], itm['status']))

    print("Verify navigation through menus to reach a station to play.")
    print_list(am_obj.get_menu(menu_id=1))
    am_obj.enter_menu(52)
    print_list(am_obj.get_menu(menu_id=52))
    am_obj.enter_menu(75)
    print_list(am_obj.get_menu(menu_id=75))
    am_obj.play_station('75_7')
    print_songinfo(am_obj)

    print("Going to play the radio station at hotkey 1.")
    am_obj.play_hotkey(1)
    print_songinfo(am_obj)


# ***************************************************************************
#                                    MAIN
# ***************************************************************************
if __name__ == '__main__':
    main()
