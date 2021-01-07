# Takes as input $1 which is a usb file (i.e. /dev/ttyUSB0)
# We can access the data rate for the previous second by calling:
# `tail -1 /tmp/data_rates/$1`
#
# Variables:
#	     $1: /dev/ttyUSB#
#	     $2: Output storage file

mkdir -p /tmp/data_rates/dev/
#echo "" > /tmp/data_rates/$1
cat  $1 | pv --line-mode --rate -f 2>&1 >/dev/null | stdbuf -oL tr '\r' '\n' > /tmp/data_rates/$1
#tail -f $2 | pv --line-mode --rate -f 2>&1 >/dev/null | stdbuf -oL tr '\r' '\n' > /tmp/data_rates/$1
