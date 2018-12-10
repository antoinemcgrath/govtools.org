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
import numpy as np

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


#inputfile = sys.argv[1]
inputfile = "food.pdf" # For test
outputfile = inputfile[:-3]+"txt"
max_doc_width = 1275  #Standard pdf width
TOLERANCE = 4  #Bbox tolerance

#   Tolerance analysis driven by
# > sort visas_tol_20.txt |uniq -c | egrep -v "  1  " |sort
# Tolerance 1: results in least dup lines but 92 blanks
# Tolerance 2: results in few dup lines but 87 blanks
# Tolerance 3: results in same as 3
# Tolerance 4: results in lease dup lines but 49 blanks
# Tolerance 5: results in same as 4
# Tolerance 10: results in same as 4
# Tolerance 20: starts to grab page numbers and other offline words

NUMBERS = map(lambda x:str(x),range(1,26))  #Line preface numbers which may be expected

#PDFtoText the file
output = Popen(["pdftotext", "-nopgbrk", "-f", "1", "-bbox", inputfile, "-"], stdout=PIPE, stderr=PIPE).communicate()[0]
soup = BeautifulSoup(output.decode('utf-8'), "lxml")  #Load PDF into beautifulsoup

all_words = soup.html.body.doc('word')  #Get all words and their coordinates

def get_nums(words):
    nums = []
    for one in words:
        if one.text in NUMBERS:
            nums.append(float(one['xmax']))
    return(nums)


def crop_split(words, side, deliminator):
    cropped_words = []
    numis_xmax = []
    for one in words:
        if side == "lt":
            if one < deliminator:
                numis_xmax.append(one)
        if side == "gt":
            if one > deliminator:
                numis_xmax.append(one)
    return(numis_xmax)


#### Slight improvement to num column identification, perhaps not needed
def reject_outliers(data):
    m = 2
    u = np.mean(data)
    s = np.std(data)
    filtered = [e for e in data if (u - 2 * s < e < u + 2 * s)]
    return filtered


def mean(numbers):
    return float(sum(numbers))/max(len(numbers),1)


def get_page_words(): #Fetch all of the words on specified page
    page_count = 0
    pages = []
    for each_page in soup.html.body.doc('page'):
        page_count += 1
        page_words = each_page('word')
        pages.append({"page":page_count, "words":page_words})
    return (pages)


def get_pages_specs():
    specs = []
    for p in p_words:
        print "Page " + str(p['page'])
        page_numbers = []
        for word in p['words']:     #For every word on a page
            if word.text in NUMBERS: #Check if word is a number
                page_numbers.append(word) #If a number add to list of page('s)_numbers
        left_nums = [] #Get left nums for each page
        for num in page_numbers: #For every page's_number
            if float(num['xmax']) < xmax_mean + 2 and float(num['xmax']) > xmax_mean-2:
                left_nums.append(num) #Append to left nums list if it is near the xmax_mean
        left_nums = sorted(left_nums, key=lambda elem: float(elem['ymin']))
        prev_boxed_num = 99999  #Detect which of the left_nums is the first "1" in a sequence
        for line in left_nums:
            if prev_boxed_num >= int(line.text):
                line_nums = []
                line_nums.append(line)  #print("Page " + str(page_number) + " starts with line " + line.text + " at ymin " + str(line['ymin'])) #print(line)
                start_y = line['ymin']
                prev_boxed_num = int(line.text)
            else:
                if prev_boxed_num == int(line.text)-1:
                    line_nums.append(line)
                    prev_boxed_num = int(line.text)
        #print(line_nums)
        specs.append({"page":int(p['page']),
        "ymin":float(start_y),
        "ymax":float(line['ymax']),
        "xmin_avec_num":float(line['xmin'])-2,
        "xmin_sans_num":float(line['xmin'])-2,
        "xmax":float(max_doc_width),
        "line_nums":line_nums})
    return(specs)


# Inorder to merge dictionary pwords[words] into specs
def get_pwords(p_words, page):
    for dict_ in p_words:
        if dict_["page"] == page:
            return {"words": dict_["words"]}


def print_specs_num(specs):
    for p in specs: #display page and word count
       print("Page " + str(p['page']) +
       ", word count " + str(len(p['words'])) +
       ", ymin " + str(p['ymin']) +
       ", ymax " + str(p['ymax']) +
       ", xmax " + str(p['xmax']) +
       ", xmin avec num " + str(p['xmin_avec_num']) +
       ", xmin sans num " + str(p['xmin_sans_num']))


# Get all numbers from all pages
all_nums = get_nums(all_words)

#Reduce all_nums to just those with an xmax less than 300px
pages_nums = crop_split(all_nums, "lt", 300)

#Reduce nums by removing outliers
fav_xmax = reject_outliers(pages_nums)

#Get the mean of xmax of nums colum
xmax_mean = mean(fav_xmax)

#Get page words
p_words = get_page_words()


for p in p_words:
    print(str(p['page']) + " " + str(len(p['words'])))


#Define page count
page_count = len(p_words)

#Get bbox specs for each page
specs = get_pages_specs()


# Merge dictionary pwords[words] into specs
# Now specs contains for each page its bbox and page words
for dict_ in specs:
    dict_.update(get_pwords(p_words, dict_["page"]))


# Proof you can see
print_specs_num(specs)


def get_spaces(space): #input is space between bbox of words in pixels
    h = int(round(space))
    if h == 0:
        spaces = ""
    if h != 0 and h < 7:
        spaces = " "
    else:
        spaces = " "*(h/7)
    return(spaces)


line_tol = 10

def get_docs_texts(specs):
    doc_t = ""
    for one in specs:
        page_t = ""
        for line_start in one["line_nums"]:
            line = ""
            word_end = float(line_start["xmax"])
            #print(str(line_start["ymin"]) + " " + str(line_start["ymax"]))
            for aword in one['words']:
                if float(aword["ymin"]) > float(line_start["ymin"]) - line_tol and float(aword["ymax"]) < float(line_start["ymax"]) + line_tol:
                    space = float(aword['xmin'])-word_end #Calculate the space between boxes (words)
                    word_end = float(aword['xmax']) #Reset word end for next word
                    spaces = get_spaces(space)
                    line += spaces + aword.text
            page_t += line + "\n"
        doc_t += page_t
    return(doc_t)


doc_t = get_docs_texts(specs)

f = open(outputfile, 'w')
f.write(doc_t.encode('utf8'))
f.close()