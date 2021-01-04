# Returns a list of file names corresponding to the attached USB Serial devices (ESP32 receivers)
ls -al /dev/ttyUSB* | awk '{print $10}'
