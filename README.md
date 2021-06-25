# CSI Pi

![CSI-Pi Flow Diagram](figures/csi_pi_diagram.png)

## Raspberry Pi Setup

```
sudo apt-get install git python3-pip pv tmux 
git clone https://github.com/StevenMHernandez/CSI-Pi.git
cd CSI-Pi
pip3 install -r requirements.txt

# Set Your Local Timezone
sudo dpkg-reconfigure tzdata
```

## Run Server

```
uvicorn app:app --host 0.0.0.0 --port 8080
```

**Note**: a better way to handle this is to automatically run this script on boot. Then you will not need to SSH to start recording. To do this, see **"Run on startup"** below.

View CSI-Pi stats at `http://<PI_IP>:8080` or `http://<PI_HOSTNAME>.local:8080`.

## Annotate CSI Data

Annotating CSI data is currently done through an HTTP endpoint. While the server is running, run the following command

```
curl --location --request POST 'http://<PI_HOSTNAME>.local:8080/annotation?value=<ACTION_OR_MEASUREMENT_VALUE>'
```

## Power Down the USB

To disable collecting data from the ESP32, you can disable to the power (technically, this does not power off the ESP32, but does make the serial data hidden from the Raspberry Pi)

```
curl --location --request POST 'http://<PI_HOSTNAME>.local:8080/power_down'
```

## Power Up the USB

```
curl --location --request POST 'http://<PI_HOSTNAME>.local:8080/power_up'
```

## Watch Server Stats

You can watch status of the current annotation file and the data rate per connect ESP32 by running the following:

```
sh watch.sh
```

Notice, if you restart the server, you will have to rerun this script otherwise the annotation file will not appear to update.

## Run on startup

You can run the system on boot through the following:

```
sudo cp ./csipi.service /etc/systemd/system/csipi.service
sudo systemctl start csipi.service
sudo systemctl enable csipi.service
```

You can stop and restart the service with the following commands too:

```
sudo systemctl stop csipi.service
sudo systemctl restart csipi.service
```
