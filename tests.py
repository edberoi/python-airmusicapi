import logging
import time
from airmusicapi import airmusic


IPADDR = '192.168.2.147'
TIMEOUT = 5 # in seconds


am = airmusic(IPADDR, TIMEOUT)
am.log_level = logging.DEBUG
am.init(language="en")

print('Device Name: %s' % am.friendly_name)

hkl = am.get_hotkeylist()
print("Hotkeylist: {} out of {}:".format(hkl['item_total'], hkl['item_return']))
for itm in hkl['item']:
    print("  {}, {}, {}".format(itm['id'], itm['name'], itm['status']))

# Select favourite station #1 from the hotkeylist and update the station status periodicly.
print("Going to play the radio station at hotkey 1. Press CTRL-C to interrupt.")
am.play_hotkey(1)
print("{:3} {}".format('Vol', 'Status'))
try:
    while True:
        playinfo = am.get_playinfo()
        st = "{:3} {} ".format(playinfo['vol'], playinfo['status'])
        if 'artist' in playinfo:
            st += "Artist:'{}' Song:'{}'".format(playinfo['artist'], playinfo['song'])
        print(st)
        time.sleep(0.5)
except KeyboardInterrupt:
    pass
