import json
import logging
import time
from airmusicapi import airmusic


IPADDR = '192.168.2.147'
TIMEOUT = 5  # in seconds


def print_list(l):
    if 'result' in l:
        print("Error: {}".format(l['result']))
        return
    print("List: {} out of {}:".format(l['item_total'], l['item_return']))
    for entry in l['item']:
        print("  {:5} {} -> {}".format(entry['id'], entry['name'], entry['status']))


am = airmusic(IPADDR, TIMEOUT)
am.log_level = logging.DEBUG
am.init(language="en")

print('Device Name: %s' % am.friendly_name)
print(json.dumps(am.get_systeminfo(), indent=2))

print("Current volume = {}".format(am.volume))
print("Current mute = {}".format(am.mute))

hkl = am.get_hotkeylist()
print("Hotkeylist: {} out of {}:".format(hkl['item_total'], hkl['item_return']))
for itm in hkl['item']:
    print("  {}, {}, {}".format(itm['id'], itm['name'], itm['status']))

print_list(am.get_menu(menu_id=1))
am.enter_menu(52)
print_list(am.get_menu(menu_id=52))
am.enter_menu(75)
print_list(am.get_menu(menu_id=75))
am.play_station('75_7')

# Select favourite station #1 from the hotkeylist and update the station status periodicly.
# print("Going to play the radio station at hotkey 1. Press CTRL-C to interrupt.")
# am.play_hotkey(1)
print("{:3} {}".format('Vol', 'Status'))
try:
    while True:
        playinfo = am.get_playinfo()
        if 'result' in playinfo:
            print(" ... {}".format(playinfo['result']))
        else:
            st = "{:3} {} ".format(playinfo['vol'], playinfo['status'])
            if 'artist' in playinfo:
                st += "Artist:'{}' Song:'{}'".format(playinfo['artist'], playinfo['song'])
            print(st)
        time.sleep(0.5)
except KeyboardInterrupt:
    pass
