# Returns the wifi channel used for the given ESP32
# Variables:
#	     $1: /dev/ttyUSB#
#	     $2: /home/pi/CSI-Pi/storage/data/1600012300.123/ttyUSB0.csv

FILENAME="/tmp/wifi_channel$1"
mkdir -p '/tmp/wifi_channel/dev/'

if [ -f "$FILENAME" ]; then
	tail -1 $FILENAME
else
	CHANNEL="$(tail -10 $2 | grep "CSI" | awk -F ',' '{print "Channel: " $17}' | head -1 )"

	if [ ! -z "$CHANNEL" ]; then
		echo $CHANNEL > $FILENAME
		echo $CHANNEL
	fi
fi
