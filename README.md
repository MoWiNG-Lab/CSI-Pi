# CSI Pi

Developed by [Steven M. Hernandez](https://github.com/StevenMHernandez)

![CSI-Pi Vue.js Web Interface](figures/csi_pi_web.png)

CSI-Pi allows CSI collection to be performed on a Raspberry Pi using any number of ESP32 microcontrollers connected through USB using the [ESP32-CSI-Tool](https://stevenmhernandez.github.io/ESP32-CSI-Tool/).

## Raspberry Pi Setup

Begin by setting up your operating system on the Raspberry Pi. 
[This guide](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up) may be a useful resource.
Afterwards, from the Raspberry Pi terminal, run the following commands:

```
# Install project dependencies
sudo apt-get install git python3-pip libgirepository1.0-dev libcairo2-dev vim -y --fix-missing

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

# Copy config variables. 
cp .env.example .env

# Edit your configuration. Most important variables to edit: `APP_DIR=`, `HOSTNAME=`,
nano .env
```

## Run Server

```
/home/pi/.local/bin/uvicorn src.csi_pi.app:app --host 0.0.0.0 --port 8080
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

## Disable CSI Data collection

To disable collecting CSIdata from the ESP32.

```
curl --location --request POST 'http://<PI_HOSTNAME>.local:8080/disable_csi'
```

## Enable CSI Data collection

```
curl --location --request POST 'http://<PI_HOSTNAME>.local:8080/enable_csi'
```

## Download data as a ZIP file

Open your web browser to `http://<PI_HOSTNAME>.local:8080/data`.

## Hourly Statistics

If you use discord, you can setup a cronjob to automatically send hourly statistics to a discord webhook. 
Edit your crontab with `crontab -e` and add the following lines: 
(Note: you must set your own webhook value for `CSI_PI_WEBHOOK`. 
[This article](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) may be useful for creating your own discord webhook.)

```
CSI_PI_WEBHOOK='https://discord.com/api/webhooks/123123123/abc123123abc'
0 * * * *  /usr/bin/curl --location --request POST $CSI_PI_WEBHOOK --form "content=\"$(/usr/bin/python3 /home/pi/CSI-Pi/src/stats/daily_stats.py)\""
```

## TTY_PLUGINS

The CSI data streaming through USB-Serial (TTY) from the ESP32s to CSI-Pi is automatically captured and recorded. 
This processing is handled through the use of an extendable `tty_plugin` system and is specifically implemented in
[tty_plugins/csi_data_plugin.py](https://github.com/StevenMHernandez/CSI-Pi/blob/main/src/csi_pi/tty_plugins/csi_data_plugin.py).
Within this file, we have a normal Python class which implements the following interface:

```
class ExampleTTYPlugin:
    def __init__(self, tty_full_path, tty_save_path, config):
        pass
        
    def prefix_string(self):
        """
        For each incoming line from our devices we will look for the following prefix-string.
        If the line starts with this string, then we will call `process(line)`.
        :return: str
        """

        return "CSI_DATA,"

    def process(self, line):
        """
        When we find a string that begins with `prefix_string()`, this function will be called.
        Process the incoming line as you wish.
        :param line: str
        :return: None
        """

        pass

    def process_every_millisecond(self, current_millisecond):
        """
        Process and store statistics for the past one second of TTY data.

        :param current_millisecond:
        :return:
        """
        
        pass
```

Notice, the `prefix_string()` method returns a string `"CSI_DATA,"`. 
As new lines of data are streamed from your USB-serial devices, CSI-Pi will check if the lines begin with this `prefix_string()`. 
If they do, then CSI-Pi will automatically pass the new line to the `process()` method. 
You are free to process the new line in any way that you see fit. 

Currently, there are [three tty_plugins](https://github.com/StevenMHernandez/CSI-Pi/blob/main/src/csi_pi/tty_plugins/) built-into CSI-Pi.
To create your own tty_plugins, create a new python file and build a new class which implements the above interface.
To install the new tty_plugin, add it to `TTY_PLUGINS` within `~/.env` and restart the CSI-Pi service.

### `src.csi_pi.tty_plugins.csi_data_plugin`

The first and most important tty_plugin is the `csi_data_plugin` which captures all new lines starting with `CSI_DATA,`.
These lines are saved in a local storage file and the plugin automatically calculates important metrics about the incoming data such as the data rate.

### `src.csi_pi.tty_plugins.csipi_command_plugin`

The `csipi_command_plugin` listens for any lines that begin with `CSIPI_COMMAND,`. 
This tty_plugin allows you to control CSI-Pi directly from your ESP32 (or other) microcontroller.
The following commands are currently implemented:

* `DISABLE_CSI` will stop CSI data from being collected. This is useful if you only want to collect CSI periodically.
* `ENABLE_CSI` will re-allow CSI data from being collected.

Example: To disable CSI data collection, your ESP32 (or similar) microcontroller must send the following string through serial: `CSIPI_COMMAND,DISABLE_CSI\n`.

### `src.csi_pi.tty_plugins.sensor_data_plugin`

Finally, we have a tty_plugin which allows us to create new annotations automatically from your ESP32 (or other) microcontroller. 
This is useful when we have a sensor that we wish to use for performing annotation.

Suppose we have some sensor with a reading of value `10`. 
If our ESP32 (or similar) microcontroller outputs the following string through serial: `SENSOR_DATA,10\n`,
then the value `10` will automatically be posted as a new annotation. 
Notice, we can pass not only numeric values, but also any string we wish. 
For example: `SENSOR_DATA,ANYTHING_WE_WISH\n`.

## Common Issues

**Power Supply**. Make sure you have a powerful enough power supply to prevent a brown out. 
Brown outs can cause the Raspberry Pi to reset randomly, especially when many USB devices are attached.

**ESP32 Module**. Some modules seem to cause more issues than others. 
We found that if the module does not auto-reset *when being flashed*, it will not automatically reset *when connected to CSI-Pi or when CSI-Pi restarts*. 
*Help in analyzing this is appreciated!* 

**`ModuleNotFoundError: No module named 'src'`** You are likely not in the correct directory. Make sure to `cd ~/CSI-Pi`.

## Citing this work

If you use this project, please cite our work:

> S. M. Hernandez and E. Bulut, "WiFi Sensing on the Edge: Signal Processing Techniques and Challenges for Real-World Systems," in Communications Surveys and Tutorials (IEEE COMST) 2023.

```
@article{EdgeWiFiSensing2023,
  title={{{WiFi Sensing on the Edge: Signal Processing Techniques and Challenges for Real-World Systems}}},
  author={Steven M. Hernandez and Eyuphan Bulut},
  journal={IEEE Communications Surveys and Tutorials},
  year={2023},
  publisher={IEEE},
  doi={10.1109/COMST.2022.3209144}
}
```

A PDF version of this paper is available here: ["WiFi Sensing on the Edge PDF"](https://www.people.vcu.edu/~ebulut/COMST22_WiFi_Sensing_Survey.pdf).
