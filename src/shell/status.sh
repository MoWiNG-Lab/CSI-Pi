# Returns a list of stats which are useful to monitor while annotating CSI data 
# Variables: 
# 	     $1: DATA_DIR (absolute path)

echo "
   ___ ___ ___   ___ _ 
  / __/ __|_ _| | _ (_)
 | (__\__ \| |  |  _/ |
  \___|___/___| |_| |_|
"
echo "CSI Pi, Steven M. Hernandez"
echo "\n"
date
echo "\n"

echo "========="
echo "Config:"
echo "DATA_DIR: $1"
echo "=========\n\n"

echo "========="
echo "Devices [Data Rate]:"
echo "\n"
WRITE_CSI_LOCK='/tmp/lock.write_csi.txt'
ls /dev/ttyUSB* | while read f; do
	echo $f
	device=$(echo $f | awk -F"/" '{print $3}')
	echo "Channel: $(tail /tmp/wifi_channel$f)"
	tail -1 /tmp/data_rates$f
	if [ $(cat $WRITE_CSI_LOCK) -eq 0 ]; then
		echo " -> CURRENTLY NOT WRITING CSI TO FILE!! (POWERED_DOWN)"
	fi
	echo "\n"
done
echo "=========\n"

echo "========="
echo "File Sizes:"
ls -al $1
echo "=========\n\n"



echo "========="
echo "Most Recent Actions:"
TIMESTAMP=$(head -2 "$1annotations.csv" | tail -1 | awk -F, '{print substr($3,1,length($1)-4)}')
echo " - (Oldest action recorded on: $(date -d @$TIMESTAMP))"
TIMESTAMP=$(tail -1 "$1annotations.csv" | awk -F, '{print substr($3,1,length($1)-4)}')
echo " - (Most recent action recorded on: $(date -d @$TIMESTAMP))\n"
tail -5 "$1annotations.csv"
echo "=========\n\n"

echo "========="
echo "Most Recent CSI:\n"
ls $1 | grep tty | while read f; do
	echo $f
	TIMESTAMP=$(head -2 $1$f | tail -1 | awk -F, '{print $(NF-1)}' | awk -F. '{print substr($1,1,length($1)-3)}')
	echo " - (Oldest CSI sample collected on: $(date -d @$TIMESTAMP))"
	TIMESTAMP=$(tail -1 $1$f | awk -F, '{print $(NF-1)}' | awk -F. '{print substr($1,1,length($1)-3)}')
	echo " - (Most recent CSI sample collected on: $(date -d @$TIMESTAMP))\n"
	tail -3 $1$f
	echo "\n"
done
echo "=========\n\n"

echo "Done"
