# CSI Pi

![CSI-Pi Vue.js Web Interface](figures/csi_pi_web.png)

CSI-Pi allows CSI collection to be performed on a Raspberry Pi using any number of ESP32 microcontrollers connected through USB using the [ESP32-CSI-Tool](https://stevenmhernandez.github.io/ESP32-CSI-Tool/).

## Raspberry Pi Setup

Begin by setting up your operating system on the Raspberry Pi. 
[This guide](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up) may be a useful resource.
Afterwards, from the Raspberry Pi terminal, run the following commands:

```
# Install project dependencies
sudo apt-get install git python3-pip pv tmux libgirepository1.0-dev

# Download CSI-Pi from github
git clone https://github.com/StevenMHernandez/CSI-Pi.git

# Open the project directory
cd CSI-Pi

# Install python libraries
pip3 install -r requirements.txt

# Add your user to the dailout group for non-sudo access to TTY devices
sudo usermod -a -G dialout $USER

# Set Your Local Timezone
sudo dpkg-reconfigure tzdata

# Set the name for the deployment location
echo "example_location_name" > ./name.txt
```

## Run Server

```
uvicorn src.csi_pi.app:app --host 0.0.0.0 --port 8080
```

**Note**: a better way to handle this is to automatically run this script on boot. Then you will not need to SSH to start recording. To do this, see **"Run on startup"** below.

View CSI-Pi at `http://<PI_IP>:8080` or `http://<PI_HOSTNAME>.local:8080`.

## Run on startup

You can run CSI-Pi on system boot through the following:

```
# You may need to edit `./csipi.service` depending on your $USER and $HOME_DIR
sudo cp ./csipi.service /etc/systemd/system/csipi.service
sudo systemctl start csipi.service
sudo systemctl enable csipi.service
```

You can stop and restart the service with the following commands too:

```
sudo systemctl stop csipi.service
sudo systemctl restart csipi.service
```

Similar to the previous section, you can now view CSI-Pi at `http://<PI_IP>:8080` or `http://<PI_HOSTNAME>.local:8080`.
Now, when you power on your Raspberry Pi, CSI-Pi will be running automatically without having to use your terminal at all.

## Annotate CSI Data

Annotating CSI data can be done through an HTTP endpoint. While the server is running, run the following command:

```
curl --location --request POST 'http://<PI_HOSTNAME>.local:8080/annotation?value=<ACTION_OR_MEASUREMENT_VALUE>'
```

## Power Down the USB

To disable collecting data from the ESP32, you can disable the USB power (technically, this does not power off the ESP32, but it does make the serial data hidden from the Raspberry Pi)

```
curl --location --request POST 'http://<PI_HOSTNAME>.local:8080/power_down'
```

## Power Up the USB

```
curl --location --request POST 'http://<PI_HOSTNAME>.local:8080/power_up'
```

## Download data as a ZIP file

Open your web browser to `http://<PI_HOSTNAME>.local:8080/data`.

## Download data to a USB Flash Drive

Data is stored on the device, but this does not give us an easy way to collect data from the Raspberry Pi. One method is to mount a usb flash drive to save the files. To achieve, this we need to first setup auto-mount:

```
$ mkdir /home/pi/CSI-Pi/usb_data_dump
$ sudo vim /etc/fstab

# Add the next line to the bottom of the file
/dev/sda1 /home/pi/CSI-Pi/usb_data_dump vfat uid=pi,gid=pi,umask=0022,sync,auto,nosuid,rw,nouser,nofail 0   0 
```

Next, create a new crontab entry which will be run every minute to check if a new USB flash drive is attached:

```
$ crontab -e

# Add the next line to the bottom of the file
* * * * * cd /home/pi/CSI-Pi && /usr/bin/sh src/shell/usb_status.sh
```

Now, when a USB flash drive is attached, it will copy over the current experiment data to the flash drive. 
It may take some time to complete this process. As such, the green LED on the raspberry pi will give some status information.

- LED Off: USB device is not attached.
- LED ON: USB device is detected.
- LED BLINKING: Data is being saved to the flash drive. **Do not disconnect.**

**Alternatively:** If you want to copy ALL historically recorded data files manually, you can run the following:

```
sh src/shell/usb_save_all.sh $YOUR_UNIQUE_DEVICE_NAME
```

Where `YOUR_UNIQUE_DEVICE_NAME` is some arbitrary name given to your device.  
The files will be stored on your flash drive under the directory `/CSI-Pi/$YOUR_UNIQUE_DEVICE_NAME/1630123456.0123456/*`.

## Hourly Statistics

If you use discord, you can setup a cronjob to automatically send hourly statistics to a discord webhook. 
Edit your crontab with `crontab -e` and add the following lines: 
(Note: you must set your own webhook value for `CSI_PI_WEBHOOK`. 
[This article](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) may be useful for creating your own discord webhook.)

```
CSI_PI_WEBHOOK='https://discord.com/api/webhooks/123123123/abc123123abc'
0 * * * *  /usr/bin/curl --location --request POST $CSI_PI_WEBHOOK --form "content=\"$(/usr/bin/python3 /home/pi/CSI-Pi/src/stats/daily_stats.py)\""
```

## Common Issues

**Power Supply**. Make sure you have a powerful enough power supply to prevent a brown out. 
Brown outs can cause the Raspberry Pi to reset randomly, especially when many USB devices are attached.

**ESP32 Module**. Some modules seem to cause more issues than others. 
We found that if the module does not auto-reset *when being flashed*, it will not automatically reset *when connected to CSI-Pi or when CSI-Pi restarts*. 
*Help in analyzing this is appreciated!* 

## System Diagrams

![CSI-Pi Flow Diagram](figures/csi_pi_diagram.png)

![CSI-Pi Metrics Flow](figures/csi_pi_metrics.png)