ls /dev/ttyUSB* | awk -F'/' '{print $3}' | while read f; do
	DATA_DIR="$(curl -s localhost:8080/data-directory)"
	TOTAL_COLLECTED=$(cat $DATA_DIR/$f.csv | awk -v tstamp="$(date +%s)" -F',' '{print $(NF-1) " " tstamp}' | awk '{print $1}' | wc -l)
	NUM_COLLECTED_1=$(cat $DATA_DIR/$f.csv | awk -v tstamp="$(date +%s)" -F',' '{print $(NF-1) " " tstamp}' | awk '{if($1/1000>($2 - (60*60))) print $1}' | wc -l)
	NUM_COLLECTED_24=$(cat $DATA_DIR/$f.csv | awk -v tstamp="$(date +%s)" -F',' '{print $(NF-1) " " tstamp}' | awk '{if($1/1000>($2 - (60*60*24))) print $1}' | wc -l)
	CHANNEL=$(sh get_wifi_channel.sh /dev/$f $DATA_DIR/$f.csv)
	echo "$f, $CHANNEL, $NUM_COLLECTED_1 collected [1 hour], $NUM_COLLECTED_24 [24 hours], $TOTAL_COLLECTED [overall]"	
done