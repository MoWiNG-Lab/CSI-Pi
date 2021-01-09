DATA_DIR="$(curl -s localhost:8080/data-directory)"

if [ -z $DATA_DIR ]; then
	echo "Make sure the Flask server is running."
	exit
fi

# Watch Annotations
tmux new-session -d "tail -f $DATA_DIR/annotations.csv"

# Get Data Rates
ls /dev/ttyUSB* | while read f; do
	tmux split-window -h "tail -f /tmp/data_rates$f"
done

tmux attach-session
