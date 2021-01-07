# Returns the wifi channel used for the given ESP32
# Variables:
#	     $1: /dev/ttyUSB#

FILENAME="/tmp/wifi_channel$1"
mkdir -p '/tmp/wifi_channel/dev/'

if [ -f "$FILENAME" ]; then
	tail -1 $FILENAME
else
	CHANNEL="$(timeout 0.25 head -10 $1 | grep "CSI" | awk -F ',' '{print "Channel: " $17}' | head -1 )"

	if [ ! -z "$CHANNEL" ]; then
		echo $CHANNEL > $FILENAME
		echo $CHANNEL
	fi
fi
