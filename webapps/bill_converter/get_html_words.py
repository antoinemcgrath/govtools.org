#python2 on ubuntu
# python2 get_html_words.py public_test_files/visas.pdf #Ubuntu
# python get_html_words.py public_test_files/visas.pdf #mac

import PyPDF2 # version 1.26.0
import glob
from subprocess import Popen, PIPE
from decimal import *
import sys
import re
from datetime import datetime
#from BeautifulSoup import BeautifulSoup #apt install python-pip pip install beautifulsoup4
from bs4 import BeautifulSoup

#inputfile = sys.argv[1]
inputfile = "food.pdf" # For test
outputfile = inputfile[:-3]+"txt"


max_doc_width = 1275
#PDFtoText the file
#Load PDF into beautifulsoup
#Get all words and their coordinates
#Search for the column with the most numbers (num_col_bbox)

#Print the bbox of interest for each page
#Crop each page to bbox specs output as pdf
#Convert cropped pages to html
#Generate txt from each pages bbox minus num_col_bbox
#Generate txt from cropped pdf


#### If a filetype check is desired #'application/pdf; charset=binary'
#import magic
#mag = magic.open(magic.MAGIC_MIME)
#mag.load()
#mts = mag.file(pdfname)


#Bbox tolerance
TOLERANCE = 4

#   Analysis driven by
# sort visas_tol_6.txt |uniq -c | egrep -v "  1  " |sort
# Tolerance 1: results in least dup lines but 92 blanks
# Tolerance 2: results in few dup lines but 87 blanks
# Tolerance 3: results in same as 3
# Tolerance 4: results in lease dup lines but 49 blanks
# Tolerance 5: results in same as 4
# Tolerance 10: results in same as 4
# Tolerance 20: starts to grab page numbers and other offline words

#Line preface numbers which may be expected
NUMBERS = map(lambda x:str(x),range(1,26))

#PDFtoText the file
output = Popen(["pdftotext", "-nopgbrk", "-f", "1", "-bbox", inputfile, "-"], stdout=PIPE, stderr=PIPE).communicate()[0]
#Load PDF into beautifulsoup
soup = BeautifulSoup(output.decode('utf-8'), "lxml")

#Get all words and their coordinates
all_words = soup.html.body.doc('word') #For all pages


def get_nums(words):
    nums = []
    for one in words:
        if one.text in NUMBERS:
            nums.append(float(one['xmax']))
    return(nums)


all_nums = get_nums(all_words)


def crop_split(words, side, deliminator):
    cropped_words = []
    numis_xmax = []
    for one in words:
        if side == "lt":
            if one < deliminator:
                numis_xmax.append(one)
                print(one)
        if side == "gt":
            if one > deliminator:
                numis_xmax.append(one)
                print(one)
    return(numis_xmax)


pages_nums = crop_split(all_nums, "lt", 300) #Reduce all_nums to just those less than 300


#### Perhaps not entirely needed
import numpy as np
def reject_outliers(data):
    m = 2
    u = np.mean(data)
    s = np.std(data)
    filtered = [e for e in data if (u - 2 * s < e < u + 2 * s)]
    return filtered


fav_xmax = reject_outliers(pages_nums)

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


xmax_mean = mean(fav_xmax)


def get_page_count():
    page_count = 0
    for each_page in soup.html.body.doc('page'):
        page_count += 1
    print ("The PDF contains " + str(page_count) + " pages.")
    return (page_count)


page_count = get_page_count()


def get_page_words(page_number): #Fetch all of the words on specified page
    page_words = soup.html.body.doc('page')[page_number]('word') #[xmin, xmax, ymin, ymax]
    sorted_page_words = sorted(page_words, key=lambda elem: float(elem['xmax'])) #This prevents misordering for the odd cases when they are not listed left to right by BeautifulSoup
    return (sorted_page_words)


def get_pages_specs():
    specs = []
    for page_number in xrange(page_count):
        print "Page" + str(page_number)
        page_words = get_page_words(page_number)
        page_numbers = []
        for page_word in page_words:
            if page_word.text in NUMBERS:
                page_numbers.append(page_word)
        page_nums = []
        for page_word in page_numbers:
            if float(page_word['xmax']) < xmax_mean + 2 and float(page_word['xmax']) > xmax_mean-2:
                page_nums.append(page_word)
        page_nums = sorted(page_nums, key=lambda elem: float(elem['ymin']))
        prev_boxed_num = 2
        for line in page_nums:
            if prev_boxed_num >= int(line.text):
                prev_boxed_num = int(line.text)
                #print("Page " + str(page_number) + " starts with line " + line.text + " at ymin " + str(line['ymin'])) #print(line)
                start_y = line['ymin']
        specs.append({"ymin":start_y, "ymax":line['ymax'], "xmin":float(page_nums[-1]['xmin'])-2, "xmin_sans_num":float(page_nums[-1]['xmin'])-2, "xmax":max_doc_width})
    return(specs)


specs = get_pages_specs()



def get_bbox_words(specs):
    for page_number in specs:

        print "Page" + str(page_number)
        page_words = get_page_words(page_number)
        page_numbers = []
        for page_word in page_words:
            if page_word.text in NUMBERS:
                page_numbers.append(page_word)
        page_nums = []
        for page_word in page_numbers:
            if float(page_word['xmax']) < xmax_mean + 2 and float(page_word['xmax']) > xmax_mean-2:
                page_nums.append(page_word)
        page_nums = sorted(page_nums, key=lambda elem: float(elem['ymin']))
        prev_boxed_num = 2
        for line in page_nums:
            if prev_boxed_num >= int(line.text):
                prev_boxed_num = int(line.text)
                #print("Page " + str(page_number) + " starts with line " + line.text + " at ymin " + str(line['ymin'])) #print(line)
                start_y = line['ymin']
        specs.append({"ymin":start_y, "ymax":line['ymax'], "xmin":float(page_nums[-1]['xmin'])-2, "xmin_sans_num":float(page_nums[-1]['xmin'])-2, "xmax":max_doc_width})
    return(specs)
















for p in specs:
    print("Page " + str(page_number) + " ends with line " + line.text + " at ymax " + str(line['ymax'])) #print(line)
    print("xmax is doc width: " + str(max_doc_width))
    print("xmin includes line num: " + str(page_nums[-1].text) + " " + str(float(page_nums[-1]['xmin'])-2))
    print("xmin does not include line num: " + str(page_nums[-1].text) + " " + str(float(page_nums[-1]['xmax'])+1))



"save as new doc"






from PyPDF2 import PdfFileWriter,PdfFileReader,PdfFileMerger
pdf_file = PdfFileReader(open(inputfile,"rb")) ####crop Pdf
pdfWriter = PyPDF2.PdfFileWriter()









    page = pdf_file.getPage(page_number) ####crop Pdf
    page.trimBox.lowerLeft = (float(page_nums[-1]['xmin'])-2, line['ymax'])
    page.trimBox.upperRight = (max_doc_width, start_y) #xmax,ymin
    page.cropBox.lowerLeft = (float(page_nums[-1]['xmin'])-2, line['ymax'])
    page.cropBox.upperRight = (max_doc_width, start_y) #xmax,ymin
    pdfWriter.addPage(page)


#pdftohtml -enc UTF-8 -noframes ir.pdf result.html
subprocess.check_output(["pdftohtml", "-enc", "UTF-8", "-noframes", file_loc])
file_loc = file_loc.replace(".pdf",".html")
#file_loc = file_loc.replace(".html",".pdf")