#!/usr/bin/python3
# python3 send_action.py

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

###### Accesses droplet IP
def get_ip_address():
    with open(home + "/govtools.org/bill_converter_pdf2txt/ip.txt", "r+") as f:
        credentials = [x.strip().split(',') for x in f.readlines()]
        ip_address = credentials[0][0]
        print(ip_address)
    return(ip_address)


ip_address = get_ip_address()
print("Status: ssh -tt -o 'StrictHostKeyChecking no' root@"+ip_address)

###### SCP Send file to droplet
def scp_file(ip_address, inputfile):
    print("Status: Attempting scp of", home + "/govtools.org/public/uploads/"+inputfile)
    try: # scp -r -o 'StrictHostKeyChecking no' inputfile root@162.243.14.5:~/
        subprocess.check_output(["scp", #"-v",
        "-r","-o", "StrictHostKeyChecking no",
        home + "/govtools.org/public/uploads/"+inputfile,
        "root@" + ip_address + ":~/uploads/"])
        print("Status: scp of inputfile to output dir complete")
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        print("Status: SCP failed check if digital ocean instance is working, if so check SCP specifics")


scp_file(ip_address, inputfile)


###### Triggers droplet conversion and requests final file through SSH
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
    instructA = "python3 ~/govtools.org-master/bill_converter_pdf2txt/convertBill2txt.py " + "~/uploads/"+inputfile + "\n"
    sshProcess.stdin.write(instructA)
    sshProcess.stdin.write("logout\n")
    sshProcess.stdin.close()


ssh_to_command(ip_address, inputfile)


###### Serves final file to user as a url
###### Return SCP Send file to droplet
returnfile = inputfile.replace(".pdf", ".txt")

def scp_file_return(ip_address, returnfile):
    print("Status: Attempting return scp of", "~/govtools.org/public/uploads/"+returnfile)
    try: # scp -r -o 'StrictHostKeyChecking no' inputfile root@162.243.14.5:~/
        subprocess.check_output(["scp", #"-v",
        "-r","-o", "StrictHostKeyChecking no",
        "root@" + ip_address + ":~/uploads/" + returnfile,
        home + "/govtools.org/public/uploads/"+returnfile])
        print("Status: scp of returnfile to uploads dir complete")
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        print("Status: SCP failed check if digital ocean instance is working, if so check SCP specifics")


scp_file_return(ip_address, returnfile)


##javascript attempts transfer file(s) 10 times
##javascript rendering a progress (socet.io) pushes messages between server and the browser
