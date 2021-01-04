# Returns a list of stats which are useful to monitor while annotating CSI data 

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
echo "DATA_DIR: $(pwd)/$1"
echo "=========\n\n"

echo "========="
echo "Devices:"
sh get_devices.sh
echo "=========\n\n"

echo "========="
echo "File Sizes:"
sh get_file_sizes.sh $1
echo "=========\n\n"

echo "========="
echo "Most recent actions:"
tail -5 "$1annotations.csv"
echo "=========\n\n"

echo "Done"
