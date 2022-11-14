# ArtMode

## Overview

A Python library and command line interface for interacting with the Samsung Frame's [Art Mode](https://www.samsung.com/us/support/answer/ANS00076727/).

## Background

The latest [SmartThings iOS app](https://apps.apple.com/us/app/smartthings/id1222822904) doesn't work consistently and isn't scriptable in any case. The [samsung-tv-ws-api](https://github.com/xchwarze/samsung-tv-ws-api) project initially looked promising, but it didn't work on my 2019 Frame (software version 1401).

My ancient iPad mini runs an older version of SmartThings, which *does* consistently connect to the Frame. Using [rvictl](https://developer.apple.com/documentation/network/recording_a_packet_trace) and [WireShark](http://wireshark.org), I was able to record a packet trace of the unencrypted websocket traffic. Unlike [samsung-tv-ws-api](https://github.com/xchwarze/samsung-tv-ws-api), which appears to [upload images on another port](https://github.com/xchwarze/samsung-tv-ws-api/blob/master/samsungtvws/art.py#L251), my 2019 Frame expects "Binary WebSockets" -- both the JSON message and the content of the image are transmitted in the same connection.

## Usage

`artmode` can be used as either a library or via the command line.

### Library

```python
import artmode

conn = ArtMode("samsung_tv.local.") # mDNS record or IP address
print(conn.get_content_list())
```

### Command Line

```sh
$ python artmode.py samsung_tv.local. list
```
