#!/usr/bin/python3
# python3 generate.py https://github.com/antoinemcgrath/govtools.org/archive/master.zip


###generates Droplet
###### writes ip to a gitignoredfile on cloud
###### logs into droplet
###### get git&unzip
###### run run.sh to instal dependencies


#### This script will login to Digital Ocean
#### Destroy any existing "process-files" droplet
#### Create & start a new "process-files" droplet
#### Determine the new servers IP
#### Writes IP to gitignoredfile on commanding server
#### Seeds the new droplet
#### If seed is a git: Attempts to execute run.sh

import sys
import digitalocean
import subprocess
import time

from pathlib import Path
home = str(Path.home())


## access from instead ~/digitalocean.txt
def get_digitalocean_keys():
    with open(home + '/govtools.org/bill_converter_pdf2txt/keys.json') as f:
          credentials = [x.strip().split(',') for x in f.readlines()]
          the_token = credentials[0][3]
    return(the_token)


def store_new_ip(ip_address):
    with open(home + "/govtools.org/bill_converter_pdf2txt/ip.txt", "w+") as fi:
        fi.write(ip_address)

the_token = get_digitalocean_keys()
new_droplet_name = "process-files"
manager = digitalocean.Manager(token=the_token)
keys = manager.get_all_sshkeys()


#### Destroying old droplet(s) (if exists)
def destroy_earlier_droplet(manager, new_droplet_name):
    my_droplets = manager.get_all_droplets()
    for droplet in my_droplets:
        if droplet.name == new_droplet_name:
            print("Status: Recreating droplet:", droplet.name)
            droplet.destroy()


#### Generating new droplet
droplet = digitalocean.Droplet(token=the_token,
                               name=new_droplet_name,
                               region='sfo2', # nyc1 nyc2 lon1 sfo1 fra1 http://speedtest-lon1.digitalocean.com/
                               image='ubuntu-18-04-x64', # CoreOS tiniest?
                               size_slug='512MB',  # size_slug='512MB'
                               tag="disposable",
                               ssh_keys=keys, #Automatic conversion
                               backups=False)


destroy_earlier_droplet(manager, new_droplet_name)

droplet.create()

#### Sleep until droplet build is completed
time.sleep(28)
status_is = "starting"
while status_is != "completed":
    time.sleep(3.5)
    actions = droplet.get_actions()
    for action in actions:
        action.load()
        status_is = action.status
        print("Status:", status_is)


#### Get droplet IP address
ip_address = manager.get_droplet(droplet.id).ip_address
print("Status: ssh -tt -o 'StrictHostKeyChecking no' root@"+ip_address)
store_new_ip(ip_address)

#### Format seed url if one was provided
def determine_seed(sys_argv): # Example https://github.com/antoinemcgrath/govtools.org/archive/master.zip
    if len(sys_argv) > 0:
        inputgit = sys_argv[1]
        if inputgit.find("github.com/") > -1:
            if inputgit.endswith(".zip") == False:
                if inputgit.endswith(".git"):
                    inputgit = inputgit.replace(".git", "/archive/master.zip")
                else:
                    inputgit = inputgit + "/archive/master.zip"
            if inputgit.startswith("github.com") == True:
                inputgit = inputgit.replace("github.com", "https://github.com")
        else:
            print("Status: URL is not a git")
        print("Status: Seed is:", inputgit)
        return(inputgit)
    else:
        print("Status: No seed")


#### Wait untiil droplet OS is running and then send it files through SCP
def scp_files(ip_address):
    print("Status: Attempting scp of uploads dir")
    try: # scp -r -o 'StrictHostKeyChecking no' conversion_script root@162.243.14.5:~/
        subprocess.check_output(["scp", #"-v",
        "-r","-o", "StrictHostKeyChecking no",
        "~/govtools.org/public/uploads/",
        "root@" + ip_address + ":~/"])
        print("Status: scp of uploads dir success")
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        print("Status: SCP failed check if digital ocean instance is working, if so check SCP specifics")


#### Seed droplet through SSH, and if seed is a github with run.sh then execute
def ssh_to_command(ip_address, inputgit):
    print("Status: SSH file executing") # ssh -tt -o 'StrictHostKeyChecking no' root@IP_Address
    sshProcess = subprocess.Popen(["ssh", #"-tt",
                                   "-o StrictHostKeyChecking no",
                                   "root@" + ip_address],
                                  stdin=subprocess.PIPE,
                                  stdout = subprocess.PIPE,
                                  universal_newlines=True,
                                  bufsize=0)
    if inputgit.find("github.com/") > -1:
        print("Status: Route A, git found 5 sec delay")
        sshProcess.stdin.write("apt-get -y install unzip" + "\n")
        time.sleep(5)
        instructA = "wget " + inputgit + " && unzip *.zip " + "\n" #install & unzip
        sshProcess.stdin.write(instructA) # wget https://github.com/antoinemcgrath/govtools.org/archive/master.zip && unzip *zip
        time.sleep(5)
        instructA2 = "rm *.zip " + "\n" #Remove compressed file
        sshProcess.stdin.write(instructA2) # wget https://github.com/antoinemcgrath/govtools.org/archive/master.zip && unzip *zip
        sshProcess.stdin.write("sh ~/" + inputgit.split('/')[4] + "-master/bill_converter_pdf2txt/run.sh " + "\n")
        print("Status: Route A, ran run.sh attempted")


    else:
        print("Status: Route B, not found to be git")
        instructB = "wget " + inputgit + "\n"
        sshProcess.stdin.write(instructB)
    sshProcess.stdin.write("logout\n")
    sshProcess.stdin.close()



inputgit = determine_seed(sys.argv)
#inputgit = "https://github.com/antoinemcgrath/govtools.org/archive/master.zip"

if inputgit is not None:
    time.sleep(15)
    scp_files(ip_address)
    ssh_to_command(ip_address, inputgit)