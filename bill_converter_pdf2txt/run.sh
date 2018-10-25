#!/bin/bash
#run.sh
#. run.sh  #.~/run.sh  #sh run.sh  #bash run.sh
mkdir output
echo "created directory: output"
echo "sending " $1 " to "/root/govtools.org-master/bill_converter_pdf2txt/convertBill2txt.py"
python3 /root/govtools.org-master/bill_converter_pdf2txt/convertBill2txt.py $1