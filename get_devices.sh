# Returns a list of file names corresponding to the attached USB Serial devices (ESP32 receivers)
until [ ! -f "/dev/ttyUSB*" ]
do
    echo "Waiting..."
    sleep 0.1
done

ls -al /dev/ttyUSB* | awk '{print $10}'
