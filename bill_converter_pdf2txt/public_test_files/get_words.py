



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
