#!/usr/bin/python3
# python3 generate.py https://github.com/antoinemcgrath/govtools.org/archive/master.zip

#### This script will login to Digital Ocean
#### Destroy any existing "process-files" droplet
#### Create & start a new "process-files" droplet
#### Determine the new servers IP
#### Seed the new droplet
#### If seed is a git: Attempt to execute run.sh

import sys
import digitalocean
import subprocess
import time

## access from instead /home/crscloud/digitalocean.txt
def get_digitalocean_keys():
    with open('keys.json') as f:
          credentials = [x.strip().split(',') for x in f.readlines()]
          the_token = credentials[0][3]
    return(the_token)


the_token = get_digitalocean_keys()
new_droplet_name = "process-files"
manager = digitalocean.Manager(token=the_token)
keys = manager.get_all_sshkeys()


#### Destroying old droplet(s) (if exists)
def destroy_earlier_droplet(manager, new_droplet_name):
    my_droplets = manager.get_all_droplets()
    for droplet in my_droplets:
        if droplet.name == new_droplet_name:
            print("Recreating droplet:", droplet.name)
            droplet.destroy()


#### Generating new droplet
droplet = digitalocean.Droplet(token=the_token,
                               name=new_droplet_name,
                               region='nyc2', # New York 2
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
        print (status_is)


#### Get droplet IP address
ip_address = manager.get_droplet(droplet.id).ip_address
print(ip_address)
print("ssh -tt -o 'StrictHostKeyChecking no' root@"+ip_address)


#### Format seed url if one was provided
def determine_seed(sys_argv): # Example https://github.com/caraphon/summer_of_antoine/archive/master.zip
    if len(sys_argv) > 1:
        inputgit = sys_argv[1]
        if inputgit.find("github.com/") > -1:
            if inputgit.endswith(".zip") == False:
                if inputgit.endswith(".git"):
                    inputgit = inputgit.replace(".git", "/archive/master.zip")
                else:
                    inputgit = inputgit + "/archive/master.zip"
            if inputgit.startswith("github.com") == True:
                inputgit = inputgit.replace("github.com", "https://github.com")
            print("Seed is:", inputgit)
        else:
            print("URL is not a git")
        return(inputgit)
    else:
        print("No seed")


#### Wait untiil droplet OS is running and then send it files through SCP
def scp_files(ip_address):
    try: # scp -r -o 'StrictHostKeyChecking no' conversion_script root@162.243.14.5:~/
        subprocess.check_output(["scp",
        "-r", "-o StrictHostKeyChecking no",
        "/home/crscloud/govtools.org/public/uploads",
        "root@" + ip_address + ": ~/"])
        print("scp of uploads dir success")
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    print("SCP failed check if digital ocean instance is working, if so check SCP specifics")


#### Seed droplet through SSH, and if seed is a github with run.sh then execute
def ssh_to_command(ip_address, inputgit):
    print("SSH file executing") # ssh -tt -o 'StrictHostKeyChecking no' root@IP_Address
    sshProcess = subprocess.Popen(["ssh",
                                   "-tt",
                                   "-o StrictHostKeyChecking no",
                                   "root@" + ip_address],
                                  stdin=subprocess.PIPE,
                                  stdout = subprocess.PIPE,
                                  universal_newlines=True,
                                  bufsize=0)
    if inputgit.find("github.com/") > -1:
        instruct = "wget " + inputgit + " && unzip *zip" + "\n" #apt install unzip
        sshProcess.stdin.write(instruct) # wget https://github.com/antoinemcgrath/govtools.org/archive/master.zip && unzip *zip
        sshProcess.stdin.write("sh ~/" + inputgit.split('/')[4] + "-master/run.sh " + " uploads/*.pdf" + "\n")
    else:
        instruct = "wget " + inputgit + "\n"
        sshProcess.stdin.write(instruct)
    sshProcess.stdin.write("logout\n")
    sshProcess.stdin.close()



inputgit = determine_seed(sys.argv)

#inputgit = "https://github.com/antoinemcgrath/govtools.org/archive/master.zip"
if inputgit is not None:
    scp_files(ip_address)
    ssh_to_command(ip_address, inputgit)