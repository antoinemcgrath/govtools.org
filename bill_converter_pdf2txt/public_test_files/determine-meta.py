import glob
from subprocess import Popen, PIPE
from BeautifulSoup import BeautifulSoup
from decimal import *
import sys
import re
import magic
from datetime import datetime
mag = magic.open(magic.MAGIC_MIME)
mag.load()
from pymongo import MongoClient
#to login and edit mongodb as user crs
client = MongoClient('mongodb://crs:ubu14tree@127.0.0.1:27017/crs')
# Connect to MongoDB
db = client.crs


TOLERANCE = 1

# !!! INCREMENT THIS VERSION WHEN WE CHANGE THE METADATA EXTRACTION !!!
VERSION = 1

#Magic determines true file type, if not a true pdf it is skipped

#1 Locate date, pending location set type
#2 Pending type search specified areas for max font
#3 Find all max fonts and set the areas of the fonts to BBox 
#4 Gather all text in BBox regardless of font size: -/+ size for OCR inconsistency
#5 

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

#setting allowed report code allowed (starts with R or A or IB or lowercase)
def check_rpt_code(ct):
    if ct.lower().startswith("r") or ct.lower().startswith("a") or ct.lower().startswith("ib") or ct.lower().startswith("bb") or ct.lower().startswith("is"):
        if re.match(r"^[a-z]{1,2}\d{3,}$", ct.lower()):
            return True
    if re.match(r"^\d{2}-\d{2,}$", ct.lower()):
        return True
    return False
# Date location determined, then title, within the general box, find largest font size that is the title

# Finding the bounding box given discovered font sizes
def get_bbox(pdfname, words, fs):
    # Figure out the bounding box for the title                                               
    title_ymax = -1
    title_ymin = sys.maxint
    for w in words:
        pt = float(Decimal(w['ymax']) - Decimal(w['ymin']))

        if abs(pt-fs) < 0.5:
            if Decimal(w['ymax']) > title_ymax:
                title_ymax = Decimal(w['ymax'])
            if Decimal(w['ymin']) < title_ymin:
                title_ymin = Decimal(w['ymin'])

    # Get the text in the title bounding box (i.e., the title)                                
    output = Popen(["pdftotext", "-nopgbrk", "-f", "1", "-l", "1", "-x", "0", "-W", "612", "-y", str(title_ymin).split(".")[0], "-H", str(title_ymax - title_ymin).split(".")[0], pdfname, "/dev/stdout"], stdout=PIPE, stderr=PIPE).communicate()[0]
    return output.replace("\n", " ").rstrip()
    
# Return largest font size between Ymin and Ymax 
# Return the maximum font size
def get_font_size(words, ymin, ymax):
    font_sizes = []
    for w in words:
        word_ymin = float(Decimal(w['ymin']))
        word_ymax = float(Decimal(w['ymax']))
        if word_ymin >= float(Decimal(ymin))-5 and word_ymax <= float(Decimal(ymax))+5:
            fs = word_ymax - word_ymin
            if fs not in font_sizes:
                font_sizes.append(fs)
    return max(font_sizes)
            
# Get all title words in BBox wmin wmax
def get_words_on_line(words, wmin, wmax):
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

def get_code(words, wmin, wmax):
    rcwords, _ = get_words_on_line(words, wmin, wmax)
    code = None
    for wd in rcwords:
        if check_rpt_code(wd):
            code = wd
    return code

def write_invalid():
	db.reports.update({
                '_id': report['_id']
            },{
                '$set': {
                    'parsed_metadata': {'error': True,
                                        'version': VERSION}
                }
            }, upsert = False, multi=False)

  # Function definitions above, main control flow starts below   
# Loops over all files  in report directory         
# continue skips file
#deleted timeout due to pymongo upgrade no longer supporting it
#rpts = db.reports.find({'parsed_metadata': {'$exists': False}, 'magic':'application/pdf' }, timeout=False)
rpts = db.reports.find({'magic':'application/pdf', '$or': [{'parsed_metadata' : {'$exists': False}},
                                                         {'parsed_metadata.version' : {'$exists': False}},
                                                         {'parsed_metadata.version': {'$lt': VERSION}}]},
                       no_cursor_timeout=True);

for report in rpts:
    pdfname = report['filename']

    mts = mag.file(pdfname)
    if not mts:
        continue    
    mt = mts.split(';')[0]
    if mt != 'application/pdf':
#        print "Invalid mimetype:", mt, pdfname
        continue
    output = Popen(["pdftotext", "-nopgbrk", "-f", "1", "-l", "2", "-bbox", pdfname, "-"], stdout=PIPE, stderr=PIPE).communicate()[0]
    soup = BeautifulSoup(output.decode('utf-8'))
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

    # Based on date position, figure out type:
    if len(dates) > 2:
#        raise Exception('Unknown PDF type ' + pdfname)
        print "Unknown PDF type", pdfname
        write_invalid()
        continue
    elif len(dates) == 0:
#        print pdfname, "**Needs OCR**"
        pass
    elif len(dates) == 2:
        # Check if 'WikiLeaks' is the first word.  We also need
        # its yMax, so we can correctly target the title font
        if words[0].text != "WikiLeaks":
            print "Unknown PDF type", pdfname
            write_invalid()
            continue
#            raise Exception('Unknown PDF type ' + pdfname)

        try:
            fs = get_font_size(words,
                               int(Decimal(words[0]['ymax']))+100,
                               int(Decimal(words[0]['ymax']))+125)
        except:
            print '[WL] FAILURE locating title: ', pdfname
            write_invalid()
            continue
#            raise Exception('[WL] FAILURE locating title: ' + pdfname)

        # Get Title
        title = get_bbox(pdfname, words, fs)
        # Get Report Code
        code = get_code(words,
                        int(Decimal(words[0]['ymax']))+65,
                        int(Decimal(words[0]['ymax']))+95)
        if not code:
            print '[WL] FAILURE locating code:', pdfname
            write_invalid()
            continue
        try:
            thedate = datetime.strptime(" ".join(dates[1][0]), '%B %d, %Y')
        except:
            try:
                thedate = datetime.strptime(" ".join(dates[1][0]), '%B %d %Y')
            except:
                print '[WL] Invalid date!', dates[1][0], pdfname
                write_invalid()
                continue
        db.reports.update({
            '_id': report['_id']
        },{
            '$set': {
                'parsed_metadata': {'ordercode' : code,
                                    'title': title,
                                    'date': thedate,
                                    'version': VERSION}
            }
        }, upsert = False, multi=False)

    else:
        # Has 1 date, so examine bbox
        bbox = dates[0][1]

        # == Type 1 (Left Aligned Date) ==
        if int(bbox[0]) == 71 or int(bbox[0]) == 72:
            # Figure out title font size:
            try:
                fs = get_font_size(words, 175, 205)
            except:
#                raise Exception('[#1] FAILURE locating title: ' + pdfname)
                print '[#1] FAILURE locating title:', pdfname
                write_invalid()
                continue
            # Get Title
            title = get_bbox(pdfname, words, fs)
            # Get Report Code
            code = get_code(words, 700, 725)
            if not code:
#                raise Exception('[#1] FAILURE locating code: ' + pdfname)
                print '[#1] FAILURE locating code:', pdfname
                write_invalid()
                continue
            try:
                thedate = datetime.strptime(" ".join(dates[0][0]), '%B %d, %Y')
            except:
                try:
                    thedate = datetime.strptime(" ".join(dates[0][0]), '%B %d %Y')
                except:
                    print '[#1] Invalid date!'
                    write_invalid()
                    continue
            db.reports.update({
                '_id': report['_id']
            },{
                '$set': {
                    'parsed_metadata': {'ordercode' : code,
                                        'title': title,
                                        'date': thedate,
                                        'version': VERSION}
                }
            }, upsert = False, multi=False)
            
        # == Type 2 (Right Aligned Date) ==
        elif int(bbox[1]) >= 550 or int(bbox[1]) < 580:
            # Check for "IN FOCUS"
            try:
                # If one of the last four words on page 2 is
                # "IF" followed by 5 decimals
                pg2words = soup.html.body.doc('page')[1]('word')
                found_if = False
                for w in pg2words[-4:]:
                    if re.match(r"IF\d{5}$", w.text):
                        found_if = True
                        code = w.text

                        # Figure out title font size:
                        try:
                            fs = get_font_size(words, 105, 145)
                        except:
#                            raise Exception('[IF] FAILURE locating title: ' + pdfname)
                            print '[IF] FAILURE locating title:', pdfname

                        # Get Title
                        title = get_bbox(pdfname, words, fs)

                        try:
                            thedate = datetime.strptime(" ".join(dates[0][0]), '%B %d, %Y')
                        except:
                            try:
                                thedate = datetime.strptime(" ".join(dates[0][0]), '%B %d %Y')
                            except:
                                print '[IF] Invalid date!', dates[0][0], pdfname
                                write_invalid()
                                continue

                        db.reports.update({
                            '_id': report['_id']
                        },{
                            '$set': {
                                'parsed_metadata': {'ordercode' : code,
                                                    'title': title,
                                                    'date': thedate,
                                                    'version': VERSION}
                            }
                        }, upsert = False, multi=False)
                        break
                if found_if:
                    continue
            except:
                pass

            # NOT "IN FOCUS"
            # Figure out title font size:
            try:
                fs = get_font_size(words, 145, 270)
            except:
                # Broaden here?
                print "FAILURE locating title", pdfname
                write_invalid()
                continue
            if fs < 16 or fs > 26:
                # Broaden here?
                print "WRONG font size", pdfname
                write_invalid()
                continue
            # Get Title
            title = get_bbox(pdfname, words, fs)
            # Get Report Code
            code = get_code(words, 15, 55)
            if not code:
                # Broaden here?
                print "FAILURE locating code", pdfname
                write_invalid()
                continue

            try:
                thedate = datetime.strptime(" ".join(dates[0][0]), '%B %d, %Y')
            except:
                try:
                    thedate = datetime.strptime(" ".join(dates[0][0]), '%B %d %Y')
                except:
                    print '[#2] Invalid date!', dates[0][0], pdfname
                    write_invalid()
                    continue

            db.reports.update({
                '_id': report['_id']
            },{
                '$set': {
                    'parsed_metadata': {'ordercode' : code,
                                        'title': title,
                                    'date': thedate,
                                    'version': VERSION}
                }
            }, upsert = False, multi=False)            
        else:
#            raise Exception('UNHANDLED CRS format ' + pdfname)
            print 'UNHANDLED CRS format', pdfname
