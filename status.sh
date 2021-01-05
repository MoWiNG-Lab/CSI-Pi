# Returns a list of stats which are useful to monitor while annotating CSI data 
# $1: DATA_DIR (relative)

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
echo "DATA_DIR: /home/pi/CSI-Pi/$1"
echo "=========\n\n"

echo "========="
echo "Devices:"
sh /home/pi/CSI-Pi/get_devices.sh
echo "=========\n\n"

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
