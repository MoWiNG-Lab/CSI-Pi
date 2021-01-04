# Returns the size of the CSI-data files in KB along with the file name
ls -lsh --block-size=K $1 | awk '{print $1 "\t\t"  $10}'
