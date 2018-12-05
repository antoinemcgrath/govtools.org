#python2 on ubuntu

import glob
from subprocess import Popen, PIPE
from decimal import *
import sys
import re
from datetime import datetime
#from BeautifulSoup import BeautifulSoup #apt install python-pip pip install beautifulsoup4
from bs4 import BeautifulSoup

inputfile = sys.argv[1]
outputfile = sys.argv[1][:-3]+"txt"


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
TOLERANCE = 1

#Line preface numbers which may be expected
NUMBERS = ['1', '2', '3', '4', '5', '6', '7', '9', '10', '11', '12', '13',
    '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25']


#PDFtoText the file
output = Popen(["pdftotext", "-nopgbrk", "-f", "1", "-bbox", inputfile, "-"], stdout=PIPE, stderr=PIPE).communicate()[0]
#Load PDF into beautifulsoup
soup = BeautifulSoup(output.decode('utf-8'), "lxml")

#Get all words and their coordinates
all_words = soup.html.body.doc('word') #For all pages


def get_page_count():
    page_count = 0
    for each_page in soup.html.body.doc('page'):
        page_count += 1
    print ("The PDF contains " + str(page_count) + " pages.")
    return (page_count)


page_count = get_page_count()


# Get all numbers in BBox wmin wmax
def get_numbers_on_column(words, wmin, wmax):
    xmax = 0
    xmin = 999,999,999
    ymax = 0
    ymin = 999,999,999
    num_column_list = []
    for w in words:
        if float(Decimal(w['xmin'])) > float(Decimal(wmin))-TOLERANCE and float(Decimal(w['xmax'])) < float(Decimal(wmax)) + TOLERANCE:
            if Decimal(w['xmax']) > xmax:
                ymax = Decimal(w['xmax'])
            if Decimal(w['xmin']) < ymin:
                ymin = Decimal(w['xmin'])
            if Decimal(w['ymax']) > xmax:
                xmax = Decimal(w['ymax'])
            if Decimal(w['ymin']) < xmin:
                xmin = Decimal(w['ymin'])
            if w.text.isdigit():
                num_column_list.append(w)
    return (num_column_list, [xmin, xmax, ymin, ymax])


#Search for the column with the most numbers (num_col_bbox)
def get_longest_num_column(all_words):
    longest_numcolumn = []
    column_num_sequence = []
    for w in all_words:
        if w.text in NUMBERS:
            on_same_column, bbox = get_numbers_on_column(all_words, w['xmin'], w['xmax'])
            if len(longest_numcolumn) < len(on_same_column) and len(on_same_column) > 1:
                longest_numcolumn = on_same_column
    print ("The longest column of numbers is " + str(len(longest_numcolumn)) + " long.") #print ("The longest number column contains these numbers:")
    for w in longest_numcolumn:
        column_num_sequence.append(w)
    return (column_num_sequence)


column_num_sequence = get_longest_num_column(all_words)


def get_page_words(page_number): #Fetch all of the words on specified page
    page_words = soup.html.body.doc('page')[page_number]('word') #[xmin, xmax, ymin, ymax]
    sorted_page_words = sorted(page_words, key=lambda elem: elem['xmax']) #This prevents misordering for the odd cases when they are not listed left to right by BeautifulSoup
    return (sorted_page_words)


def get_words_in_box(words, xmin, xmax, ymin, ymax):
    wordlist = []
    box_xmax = 0
    box_xmin = sys.maxint
    box_ymax = 0
    box_ymin = sys.maxint
    w_end = xmax
    line = ""
    for w in words:
        if float(Decimal(w['xmin'])) > xmax and float(Decimal(w['ymin'])) > ymin-TOLERANCE and float(Decimal(w['ymax'])) < ymax + TOLERANCE:
            space = Decimal(w['xmin'])-w_end #Calculate the space between boxes
            w_end = Decimal(w['xmax'])
            print("This next ended at " + str(w_end))
            if Decimal(w['ymax']) > box_ymax: #set new max if ought to
                box_ymax = Decimal(w['ymax'])
            if Decimal(w['ymin']) < box_ymin: #set new min if ought to
                box_ymin = Decimal(w['ymin'])
            if Decimal(w['xmax']) > box_xmax: #set new max if ought to
                box_xmax = Decimal(w['xmax'])
            if Decimal(w['xmin']) < box_xmin: #set new min if ought to
                box_xmin = Decimal(w['xmin'])
            print(str(space) + "  " + (w.text).encode('utf-8'))
            h = int(round(space))
            if h != 0 and h < 7:
                spaces = " "
            else:
                spaces = " "*(h/7)
            line += spaces + w.text #print (box_xmax, box_xmin, box_ymax, box_ymin)
    return (line)


ymax = 0
page = 0
pages_lines = ""
page_words = get_page_words(page)
for a_num in column_num_sequence:
    if ymax > float(a_num['ymax']):
        page += 1
        print(page)
        page_words = get_page_words(page)
    line = get_words_in_box(page_words, Decimal(a_num['xmin']), Decimal(a_num['xmax']), Decimal(a_num['ymin']), Decimal(a_num['ymax'])) #print (str(page) + ":" + str(a_num.text) + " line height is between " + a_num['ymin'] + " & " + a_num['ymax'])    #print(line)
    pages_lines += line + "\n"
    ymax = float(a_num['ymax'])


f = open(outputfile, 'w')
f.write(pages_lines.encode('utf8'))
f.close()