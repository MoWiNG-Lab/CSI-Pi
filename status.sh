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
	/bin/sh /home/pi/CSI-Pi/get_wifi_channel.sh $f
	tail -1 /tmp/data_rates$f
	if [ $(cat $WRITE_CSI_LOCK) -eq 0 ]; then   
		echo " -> CURRENTLY NOT WRITING CSI TO FILE!! (POWERED_DOWN)"
	fi
	echo "\n"	
done
echo "=========\n"

echo "========="
echo "File Sizes:"
sh /home/pi/CSI-Pi/get_file_sizes.sh $1
echo "=========\n\n"

echo "========="
echo "Most Recent Actions:"
tail -5 "$1annotations.csv"
echo "=========\n\n"

echo "========="
echo "Most Recent CSI:\n"
ls $1 | grep tty | while read f; do
	echo $f
	tail -3 $1$f
	echo "\n"
done
echo "=========\n\n"

echo "Done"
