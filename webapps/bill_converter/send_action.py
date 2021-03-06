#!/usr/bin/python3
# python3 send_action.py "file"
# python3 send_action.py visas.pdf

### A users upload of a pdf triggers this python script
###### Receives an uploaded file as input
###### Accesses droplet IP
###### Sends file to droplet
###### Triggers droplet conversion and requests final file
###### Serves final file to user as a url

import sys
import subprocess
import time


from pathlib import Path
home = str(Path.home())

###### Receives an uploaded file as input
inputfile = sys.argv[1]
print(inputfile)

###### Accesses processing server droplet IP
def get_ip_address():
    with open(home + "/govtools.org/webapps/bill_converter/ip.txt", "r+") as f:
        credentials = [x.strip().split(',') for x in f.readlines()]
        ip_address = credentials[0][0]
        print(ip_address)
    return(ip_address)


ip_address = get_ip_address()
print("Status: ssh -tt -o 'StrictHostKeyChecking no' root@"+ip_address)

###### SCP Send file to processing server/droplet
def scp_file(ip_address, inputfile):
    print("Status: Attempting scp of", home + "/govtools.org/public/upload/"+inputfile)
    try: # scp -r -o 'StrictHostKeyChecking no' inputfile root@162.243.14.5:~/
        subprocess.check_output(["scp", #"-v",
        "-r","-o", "StrictHostKeyChecking no",
        home + "/govtools.org/public/upload/"+inputfile,
        "root@" + ip_address + ":~/upload/"])
        print("Status: scp of inputfile to output dir complete")
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        print("Status: SCP failed check if digital ocean instance is working, if so check SCP specifics")


scp_file(ip_address, inputfile)


###### Triggers provessing server/droplet conversion and requests final file through SSH
def ssh_to_command(ip_address, inputfile):
    print("Status: SSH file executing") # ssh -tt -o 'StrictHostKeyChecking no' root@IP_Address
    sshProcess = subprocess.Popen(["ssh", #"-tt",
                                   "-o StrictHostKeyChecking no",
                                   "root@" + ip_address],
                                  stdin=subprocess.PIPE,
                                  stdout = subprocess.PIPE,
                                  universal_newlines=True,
                                  bufsize=0)
    print("Status: SSH of actions")
    instructA = "python2 ~/govtools.org-master/webapps/bill_converter/get_words.py " + "~/upload/"+inputfile + "\n"
    sshProcess.stdin.write(instructA)
    #time.sleep(60)
    sshProcess.stdin.write("logout\n")
    sshProcess.stdin.close()


ssh_to_command(ip_address, inputfile)


###### Serves final file to user as a url
###### Return SCP Send file to droplet
returnfile = inputfile.replace(".pdf", ".txt")

def scp_file_return(ip_address, returnfile):
    print("Status: Attempting return scp of", "~/govtools.org/public/upload/"+returnfile)
    try: # scp -r -o 'StrictHostKeyChecking no' inputfile root@162.243.14.5:~/
        subprocess.check_output(["scp", #"-v",
        "-r","-o", "StrictHostKeyChecking no",
        "root@" + ip_address + ":~/upload/" + returnfile,
        home + "/govtools.org/public/upload/"])
        print("Status: scp of returnfile to upload dir complete")
        print("https://govtools.org/upload/"+returnfile)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        print("Status: SCP failed check if digital ocean instance is working, if so check SCP specifics")


time.sleep(10)
scp_file_return(ip_address, returnfile)
scp_file_return(ip_address, returnfile[:-4]+"_num.txt")


##javascript attempts transfer file(s) 10 times
##javascript rendering a progress (socet.io) pushes messages between server and the browser
