cat $1 | grep CSI | perl -MTime::HiRes=time -wne'chomp $_;print sprintf"$_,fake_uuid,%f,example_experiment_name\n",scalar(time*1000);' >> $2
