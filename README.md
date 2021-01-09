# CSI Pi

![CSI-Pi Flow Diagram](figures/csi_pi_diagram.png)

## Raspberry Pi Setup

```
sudo apt-get install git python3-pip pv tmux 
git clone https://github.com/StevenMHernandez/CSI-Pi.git
cd CSI-Pi
pip3 install -r requirements.txt
```

## Run Server

```
uvicorn app:app --host 0.0.0.0 --port 8080
```

View the stats at `http://<PI_IP>:8080` or `http://<PI_HOSTNAME>.local:8080`

## Annotate CSI Data

Annotating CSI data is currently done through an HTTP endpoint. While the server is running, run the following command

```
curl --location --request POST 'http://<PI_HOSTNAME>.local:8080/annotation?value=<ACTION_OR_MEASUREMENT_VALUE>'
```

