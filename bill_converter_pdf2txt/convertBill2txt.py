#!/usr/bin/env python3
import os.path
import sys
import subprocess
#from operator import itemgetter
#DOES NOT INCLUDE HEADER OR ANY TEXT THAT FAILS TO MEET THE PREFACE SCHEMA

#Python script will receive a Lediglative draft via input pdf and output an editable text version of the bill
#https://github.com/richardgirges/express-fileupload
#https://github.com/richardgirges/express-fileupload/tree/master/example#basic-file-upload
direct = os.path.dirname(os.path.realpath(__file__))
#direct = "/home/crscloud/congress.ai/public/uploads"
inputfile = sys.argv[1]

#direct = "/Users/macbook/Desktop/Demand_Progress"
#inputfile = "in.pdf"

file_loc = direct + "/" + inputfile
matched = []
iter = 0
matched_lines = []
preline = {}
#Describe line prefaces " 1. " or " 1 " etc
preline.update(pre_num = "")    #Preface first characters
preline.update(num_iter = 1)    #Preface iterable starting number
preline.update(post_num = " ")  #Preface post iterable number


#Create text version
    #html_fmt = subprocess.check_output(["pdftotext", os.path.join(REPORTS_DIR, formats["PDF"]), "-"]).decode("utf8")
    #subprocess.check_output(["pdftotext", file_loc, "-"]).decode("utf8")
    #subprocess.check_output(["pdftotext", file_loc]).decode("utf8")
    #subprocess.check_output(["pdftotext", file_loc]).decode("ISO-8859-1")

#### Install missing package pdftotext
subprocess.check_output(["sudo", "apt-get", "-y", "install", "poppler-utils"])

subprocess.check_output(["pdftotext", file_loc])
file_loc = file_loc.replace(".pdf",".txt")


def fetch_text(file_loc):
    all_text = []
    for line in open(file_loc, encoding='ISO-8859-1'):
        all_text.append(line)
    return(all_text)


def text_cleaner(atext):
    clean_text = []   #### Replaces line seperators with lines instead of ascii "llllll"
    for aline in atext:
        aline = aline.replace("llllllllll","––––––––––")
        aline = aline.replace("S. ll","S. ––")
        aline = aline.replace("``","''")
        clean_text.append(aline)
    return(clean_text)


#Generate the iterated line preface
def iter_match(preline, iter):
    match_me = preline['pre_num'] + str(preline['num_iter']+iter) + preline['post_num']
    #print(match_me)
    return(match_me)


#### Search each line in all_text for match_me
#### Store the match_me+all_text.index+lines_text as matched in matched_lines
def find_match(all_text, match_me, matched_lines):
    for aline in all_text:
        if aline.startswith(match_me) == True:
            matched = [match_me, all_text.index(aline), aline]
            matched_lines.append(matched)
            #print(matched)
    return(matched_lines)


all_text = fetch_text(file_loc)   #### Get all lines from the pdf converted text file
all_text = text_cleaner(all_text) #### Replace odd characters including llll as lines ----
match_me = iter_match(preline, 0) #### Generate first line preface " 1. " or " 1 " etc


#### Discover lines that match the line preface(s)
def get_all_preface_matches(iter, all_text, match_me, matched_lines, preline):
    while iter < len(all_text):
        iter += 1
        matched_lines = find_match(all_text, match_me, matched_lines) #matched_lines = sorted(matched_lines)
        match_me = iter_match(preline, iter)
    return(matched_lines)


matched_lines = get_all_preface_matches(iter, all_text, match_me, matched_lines, preline)

matched_lines.sort(key=lambda x: x[1])


out_file = open(file_loc, 'w')
for one in matched_lines:
    #print(one)
    out_file.write(one[2][len(one[0]):])


out_file.close()