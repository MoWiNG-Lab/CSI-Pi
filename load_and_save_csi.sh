cat $1 | grep CSI | perl -MTime::HiRes=time -wne'chomp $_;print sprintf"$_,fake_uuid,%d,example_experiment_name\n",int(time*1000);' >> $2
