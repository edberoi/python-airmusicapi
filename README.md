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

Usage
=====

See file tests.py for more details.

A quick application to retrieve the device's given name:
```python
from airmusicapi import airmusic

IPADDR = '192.168.2.147'
TIMEOUT = 1 # in seconds

am = airmusic(IPADDR, TIMEOUT)
print('Name: %s' % am.friendly_name)
