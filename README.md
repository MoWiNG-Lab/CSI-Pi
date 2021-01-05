# CSI Pi

## Raspberry Pi Setup

```
sudo apt-get install python3-pip
git clone https://github.com/StevenMHernandez/CSI-Pi.git
cd CSI-Pi
pip3 install -r requirements.txt
```

## Run Server

```
python3 app.py
```

View the stats at `http://<PI_IP>:8080` or `http://<PI_HOSTNAME>.local:8080`

## Annotate CSI Data

Annotating CSI data is currently done through an HTTP endpoint. While the server is running, run the following command

```
curl --location --request POST 'http://<PI_HOSTNAME>.local:8080/annotation?value=<ACTION_OR_MEASUREMENT_VALUE>'
```

