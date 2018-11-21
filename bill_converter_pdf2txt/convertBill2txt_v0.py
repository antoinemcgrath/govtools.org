#!/usr/bin/env python3
import os.path
import sys
import subprocess
import re
#from operator import itemgetter
#DOES NOT INCLUDE HEADER OR ANY TEXT THAT FAILS TO MEET THE PREFACE SCHEMA

#Python script will receive a Lediglative draft via input pdf and output an editable text version of the bill
#https://github.com/richardgirges/express-fileupload
#https://github.com/richardgirges/express-fileupload/tree/master/example#basic-file-upload
#direct = "~/congress.ai/public/upload"
inputfile = sys.argv[1]
print(inputfile)
#direct = "/Users/macbook/Desktop/Demand_Progress"
#inputfile = "in.pdf"

file_loc = inputfile
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

##subprocess.check_output(["sudo", "apt-get", "-y", "install", "poppler-utils"])

subprocess.check_output(["pdftotext", file_loc])
file_loc = file_loc.replace(".pdf",".txt")


def fetch_text(file_loc):
    all_text = []
    for line in open(file_loc, encoding='ISO-8859-1'):
        all_text.append(line)
    return(all_text)


def get_page_repetitions(all_text):
    duplicate_lines = set([x for x in all_text if all_text.count(x) > 1])
    all_rep_lines = []
    for repeat in duplicate_lines:
        reps = [index for index, value in enumerate(all_text) if value == repeat]
        #print("Line repeats ", all_text.count(repeat), " times, at: ", reps)
        #print("Line is: '" + repeat[:-1] + "'")
        all_rep_lines += reps
    all_rep_lines.sort()
    return(all_rep_lines)

def text_cleaner(atext): #do not create new list items within this step
    clean_text = []   #### Replaces line seperators with lines instead of ascii "llllll"
    for aline in atext:
        aline = aline.replace("â","'")
        aline = aline.replace("â","'")
        aline = aline.replace("â","'")
        aline = aline.replace("S. ll","S.__")
        aline = aline.replace("H. R. ll","H.R.__")
        #aline = aline.replace("``","''")
        aline = re.sub(r'on (l)\1{5,}', 'on ___________', aline)
        aline = re.sub(r'(l)\1{5,}', '––––––––––', aline)
        clean_text.append(aline)
    return(clean_text)


#Generate the iterated line preface
def iter_match(preline, iter):
    match_me = preline['pre_num'] + str(preline['num_iter']+iter) + preline['post_num']
    #print("Match Me:", match_me)
    return(match_me)


#### Search each line in all_text for match_me
#### Store the match_me+all_text.index+lines_text as matched in matched_lines
def find_match(all_text, match_me, matched_lines):
    for aline in all_text:
        #print(match_me[:-2]+"/n")
        if aline.startswith(match_me) == True or aline.startswith(match_me[:-2]) == True:
            #print(aline)
            matched = [match_me, all_text.index(aline), aline]
            matched_lines.append(matched)
            #print("Matched: ", matched)
    return(matched_lines)


all_text = fetch_text(file_loc)   #### Get all lines from the pdf converted text file
#print(all_text)
repeat_lines = get_page_repetitions(all_text)

#print(repeat_lines)
#for aline in repeat_lines:
    #print(all_text[aline])

def get_first_line_of_legislation(all_text):
    line_on = 0
    first_line_of_legislation = None
    for aline in all_text:
        if first_line_of_legislation == None:
            if aline[0].isdigit():
                num = re.search(r'\d+', aline).group()
                if len(num) < len(aline):
                    if aline  == str(num+"\n"):
                        print(line_on, "Good ", aline[:-1], all_text[line_on][:-1])
                        first_line_of_legislation = line_on
                    elif aline[len(num)] != " ":
                        print(line_on, "Fail ", aline[:-1], all_text[line_on][:-1])
                    else:
                        print(line_on, "Good ", aline[:-1], all_text[line_on][:-1])
                        first_line_of_legislation = line_on
            line_on += 1
        #print(line_on, num, all_text[line_on])
    return(first_line_of_legislation)

def get_ordered_numlines(all_text):
    line_on = 0
    numlines = []
    for aline in all_text:
        if aline[0].isdigit():
            num = re.search(r'\d+', aline).group()
            if len(num) < len(aline):
                if aline  == str(num+"\n"):
                    numlines.append(line_on)
                    print(line_on, "Good ", aline[:-1], all_text[line_on][:-1])
                elif aline[len(num)] != " ":
                    print(line_on, "Fail ", aline[:-1], all_text[line_on][:-1])
                else:
                    numlines.append(line_on)
                    print(line_on, "Good ", aline[:-1], all_text[line_on][:-1])
        line_on += 1
    #print(line_on, num, all_text[line_on])
    return(numlines)


first_line_of_legislation = get_first_line_of_legislation(all_text)
numlines = get_ordered_numlines(all_text)
print(all_text[first_line_of_legislation])

all_text = text_cleaner(all_text) #### Replace odd characters including llll as lines ----

#match_me = iter_match(preline, 0) #### Generate first line preface " 1. " or " 1 " etc


#### Discover lines that match the line preface(s)
#def get_all_preface_matches(iter, all_text, match_me, matched_lines, preline):
#    while iter < len(all_text):
#        iter += 1
#        matched_lines = find_match(all_text, match_me, matched_lines) #matched_lines = sorted(matched_lines)
#        match_me = iter_match(preline, iter)
#    return(matched_lines)

#matched_lines = get_all_preface_matches(iter, all_text, match_me, matched_lines, preline)
#matched_lines.sort(key=lambda x: x[1])
out_file = open(file_loc[:-4]+"_a.txt", 'w')
print(repeat_lines)
one_count = 0

for one in all_text:
    print(one_count)
    if not repeat_lines.count(one_count) > 0:
        if one_count >= first_line_of_legislation:
            print(one)
            out_file.write(one)
    one_count += 1
out_file.close()


out_file = open(file_loc, 'w')
for one in numlines:
    #print(one)
    out_file.write(all_text[one])
out_file.close()