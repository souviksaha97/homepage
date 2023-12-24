#!/bin/bash

# modprobe r8188eu
rfkill unblock all
wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant.conf
echo "Wifi is connected"

sleep 20

python webpage.py &