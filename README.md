# GovTools.org
# Website & user interface

GovTools.org: Website & user interface
----

This Git supports GovTools.org a resource for government.
Tools include:
1. PDF to Text conversion.
-For the conversion of bill drafts stored in PDF to an easily editable .txt format.
-Files (bill drafts) are destroyed after conversion and not preserved on the servers.
-For users security the file processing server is periodically destroyed and recreated.
Functions
The app.js enables users to upload draft bills in .pdf format to https://govtools.org/upload.html
The send_action.py is activated by (app.js) to deliver pdf to disposable processing server
The send_action.py remotely activates the conversion script get_words.py
The send_action.py requests the completed .txt file to ~/govtools.org/public/upload/
*The send_action.py destroys all uploads and conversion on the processing server
The user is able to access their converted document at https://govtools.org/upload/TheirFilesName.txt
*The users files are destroyed on primary server upon being server (or if not acccessed after 10 minutes)
*Periodically Cron script triggers generate.py which destroys and rebuilds the processing server and sets env. stores new keys



-------
Welcome note: If any of this interests you please comment or join in!
-------
