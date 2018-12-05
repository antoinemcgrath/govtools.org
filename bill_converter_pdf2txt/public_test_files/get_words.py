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
output = Popen(["pdftotext", "-nopgbrk", "-f", "1", "-bbox", pdfname, "-"], stdout=PIPE, stderr=PIPE).communicate()[0]
#Load PDF into beautifulsoup
soup = BeautifulSoup(output.decode('utf-8'))

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
    xmin = sys.maxint
    ymax = 0
    ymin = sys.maxint
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





















f = open('rs.txt', 'w')
for aline in pages_lines:
    f.write(aline.encode('utf8'))


f.close()






    for word in line_wordlist:
        word.decode('utf8')


import io
with io.open(filename, 'w', encoding=character_encoding) as file:
    file.write(unicode_text)

























for words in all_words:
    get_numbers_in_num_col_bbox(words, num_col_bbox)



def get_numbers_in_num_col_bbox(words, num_col_bbox):
    xmax = Decimal(num_col_bbox[1])   #[xmin, xmax, ymin, ymax]
    xmin = Decimal(num_col_bbox[0])
    ymax = Decimal(num_col_bbox[3])
    ymin = Decimal(num_col_bbox[2])
    num_column_list = []
    w = words
    if float(Decimal(w['xmin'])) > float(Decimal(xmin))-TOLERANCE and float(Decimal(w['xmax'])) < float(Decimal(xmax)) + TOLERANCE:
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
            print(w.text + " xmin:"+w['xmin'] + " xmax:"+w['xmax'] + " ymin:"+w['ymin'] + " ymax:"+w['ymax'])
    return (num_column_list, [xmin, xmax, ymin, ymax])




xmax must be +/-5 median,
ymin and ymax ought to be +/- 60 of another on page
num_col_bbox, column_num_sequence = get_longest_num_column(all_words)

w['xmin']

get page median of xmax











def get_page_words(page_number): #Fetch all of the words on specified page
    page_words = soup.html.body.doc('page')[page_number-1]('word') #[xmin, xmax, ymin, ymax]
    return(page_words)


page_words = get_page_words(page_number)




    xmin = float(num_col_bbox[0])
    xmax = float(num_col_bbox[1])
    num_column_list, pbbox = get_numbers_on_column(page_words, wmin, wmax)
    return(num_column_list)







for w in page_words:
    if w.text in NUMBERS:
        colum_words = get_words_on_line(page_words, w.min, w.max)




#Use num_col_bbox's xmin xmax to locate longest sequential line numbers (ymin ymax)
#Print the bbox of interest for each page
#Crop each page to bbox specs output as pdf
#Convert cropped pages to html
#Generate txt from each pages bbox minus num_col_bbox
#Generate txt from cropped pdf




if column_num_sequence.count(1) == page_count:
    print("Numeric column sequence suggests the same number of pages as the initial page count: " + str(page_count))


last_num = max(column_num_sequence)
column_num_sequence.reverse()
rev = column_num_sequence

page_count


for a_page in range(page_count):
    print(a_page)
    nums_column_list = get_col_page_words(a_page, num_col_bbox)
    print(nums_column_list)
    for a_num in num_column_list:
        best_words, mbbox = get_words_on_line(words, wmin, wmax)



        w['ymin'], w['ymax']






test_num = 0
for a_num in column_num_sequence:
    test_num += 1
    if a_num = test_num


del list1[2]

#print("The longest number column contains these numbers:")
for w in longest_numcolumn:
    on_same_line, line_bbox = get_words_on_line(all_words, w['ymin'], w['ymax'])
    line = on_same_line[1:] #Removes first word on line (the line number)
    a_line = ""
    for word in line:
        a_line += " " + word
    print(a_line)



def get_words_on_page(words, wmin, wmax):
    xmax = 0
    xmin = sys.maxint
    ymax = 0
    ymin = sys.maxint
    wordlist = []
    for w in words:
        if float(Decimal(w['ymin'])) > float(Decimal(wmin))-TOLERANCE and float(Decimal(w['ymax'])) < float(Decimal(wmax)) + TOLERANCE:
            if Decimal(w['ymax']) > ymax:
                ymax = Decimal(w['ymax'])
            if Decimal(w['ymin']) < ymin:
                ymin = Decimal(w['ymin'])
            if Decimal(w['xmax']) > xmax:
                xmax = Decimal(w['xmax'])
            if Decimal(w['xmin']) < xmin:
                xmin = Decimal(w['xmin'])
            if w.text.lower() != "updated" and w.text.lower() != "revised":
                wordlist.append(w.text)
    return (wordlist, [xmin, xmax, ymin, ymax])




#line_bbox

for each_page in range(pages):
    page_words = soup.html.body.doc('page')[each_page]('word')
    print("Page:", each_page, "is", len(page_words), "long.")

    get_words_on_page(each_page)

    print(len(each_page))
    for each_word in each_page:
        print(each_word)

    page_text = each_page




#Do each page
for w in all_words:
    if Decimal(w['xmin']) > bbox[0] and Decimal(w['xmax']) < bbox[1]:
        if Decimal(w['ymin']) > bbox[2]-2*TOLERANCE and Decimal(w['ymax']) < bbox[3]+2*TOLERANCE:
            print(w.text)   #          print(bbox)



for w in all_words:
    if Decimal(w['xmin']) > bbox[0] and Decimal(w['xmax']) < bbox[1]:
        if Decimal(w['ymin']) > bbox[2]: # and Decimal(w['ymax']) < bbox[3]+TOLERANCE:
            print(w.text)   #          print(bbox)



<word xmin="133.000000" ymin="546.415700" xmax="140.000000" ymax="559.239700">1</word>
<word xmin="178.000200" ymin="546.947700" xmax="192.476200" ymax="559.099700">Be</word>
<word xmin="197.409800" ymin="546.947700" xmax="206.411800" ymax="559.099700">it</word>
<word xmin="211.345400" ymin="546.947700" xmax="252.841400" ymax="559.099700">enacted</word>




      in words and w.text






for w in words:
    # For each month
    if w.text in NUMBERS:
        on_same_line, bbox = get_words_on_line(words, w['ymin'], w['ymax'])
        # Only if the date occurs alone on a line
        #if len(on_same_line) != 3:
        print(w['ymin'], w['ymax'])
        #print(w['xmin'], w['xmax'])
        if on_same_line > 1
        print(on_same_line)

        on_same_column, bbox = get_numbers_on_column(words, w['xmin'], w['xmax'])
        # Only if the date occurs alone on a line
        #if len(on_same_line) != 3:
        #print(w['ymin'], w['ymax'])
        print(w['xmin'], w['xmax'])
        print(on_same_column)






set(num_columns)
        print(len(on_same_column))
        #print(w['xmin'], w['xmax'])
        #print(on_same_column)







        # There should only be 2 things on the same line -- the year and day number
        for slw in on_same_line[1:3]:
            if slw[-1:] == ",":
                slw = slw[:-1]
            try:
                if int(slw) > 1900 and int(slw) < 2100:
                    got_year = int(slw)
                if int(slw) > 0 and int(slw) < 32:
                    got_day = int(slw)
            except:
                pass
        if got_day and got_year:
            dates.append((on_same_line,bbox))














get_words_on_line

for w in words:
    # For each month
    if w.text in MONTHS:
        on_same_line, bbox = get_words_on_line(words, w['ymin'], w['ymax'])





    # Holds all dates we parse from this
    dates = []

    if not soup.html or not soup.html.body or not soup.html.body.doc:
        continue
    words = soup.html.body.doc('page')[0]('word')

    for w in words:
        # For each month
        if w.text in MONTHS:
            on_same_line, bbox = get_words_on_line(words, w['ymin'], w['ymax'])
            # Only if the date occurs alone on a line
            if len(on_same_line) != 3:
                continue
            got_year = False
            got_day = False
            # There should only be 2 things on the same line -- the year and day number
            for slw in on_same_line[1:3]:
                if slw[-1:] == ",":
                    slw = slw[:-1]
                try:
                    if int(slw) > 1900 and int(slw) < 2100:
                        got_year = int(slw)
                    if int(slw) > 0 and int(slw) < 32:
                        got_day = int(slw)
                except:
                    pass
            if got_day and got_year:
                dates.append((on_same_line,bbox))