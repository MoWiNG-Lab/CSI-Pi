#!/bin/bash

sda1=/dev/sda1
status_file=/tmp/usb_status.txt

if [ -e "$sda1" ]; then
	# if file exists
	sudo sh -c "echo 1 > /sys/class/leds/led0/brightness"
	
	previous_status=$(cat $status_file)
	if [ "$previous_status" = "usb_unmounted" ]; then
		DATA_DIR="$(curl -s 'http://localhost:8080/data-directory')"
		NEW_DIR="$(echo $DATA_DIR | awk -F/ '{print $7}')"
		sudo mount /dev/sda1

		name=$(cat /home/pi/CSI-Pi/name.txt)
		time=$(date +%s)
		sleep 1 && mkdir -p "/home/pi/CSI-Pi/usb_data_dump/CSI-Pi/$name/$time" && cp -r $DATA_DIR "/home/pi/CSI-Pi/usb_data_dump/CSI-Pi/$name/$time/$NEW_DIR" & 
		pid=$!

		while ps -p $pid >/dev/null
		do
			sleep 0.25
			sudo sh -c "echo 0 > /sys/class/leds/led0/brightness"
   			sleep 0.25
			sudo sh -c "echo 1 > /sys/class/leds/led0/brightness"
		done

		sudo umount /dev/sda1
	fi

	echo "usb_mounted" > $status_file
else
	# if file does not exist
	sudo sh -c "echo 0 > /sys/class/leds/led0/brightness"
	echo "usb_unmounted" > $status_file
fi

