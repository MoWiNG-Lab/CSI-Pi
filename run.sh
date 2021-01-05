cat $1 | grep CSI | gawk -F ',' '{ print $0 ",fake_uuid," systime() ",example_experiment_name" }' >> $2
