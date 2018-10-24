#!/bin/bash
#run.sh
#. run.sh  #.~/run.sh  #sh run.sh  #bash run.sh
mkdir output
echo "created directory: output"
echo "sending " $1 " to convertBill2txt.py"
python3 convertBill2txt.py $1