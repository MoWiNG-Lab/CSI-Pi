#!/bin/bash

IFS=$'\n'
WRITE_CSI_LOCK='/tmp/lock.write_csi.txt'

if [ ! -f $WRITE_CSI_LOCK ]; then
	touch $WRITE_CSI_LOCK
	echo 1 > $WRITE_CSI_LOCK
fi

cat $1 | grep CSI | while IFS= read -r line
do
	if [ $(cat $WRITE_CSI_LOCK) -eq 1 ]; then
		echo $line | perl -MTime::HiRes=time -wne'chomp $_;print sprintf"$_,fake_uuid,%f,example_experiment_name\n",scalar(time*1000);' >> $2
	fi
done
