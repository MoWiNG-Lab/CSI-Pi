#
# Copy all new files from the data-directory to a USB flash drive.
# If this is a new flash drive ALL PREVIOUS EXPERIMENTS will be copied to the device.
# This may take a long time to complete.
#
# Usage:
#       cd /home/pi/CSI-Pi  # This is required because we use relative paths in this script.
#       sh ./src/usb_save_all.sh YOUR_CUSTOM_DEVICE_NAME
#
#   $1: YOUR_CUSTOM_DEVICE_NAME  # If you have multiple raspberry pis, changing this value will keep the data separated on the flash drive
#

sudo mount /dev/sda1 /home/mowing/CSI-Pi/usb_data_dump/

name=$1

sudo mkdir -p "./usb_data_dump/CSI-Pi/$name"
rsync --progress -r -u  ./storage/data "./usb_data_dump/CSI-Pi/$name"

sudo umount /dev/sda1