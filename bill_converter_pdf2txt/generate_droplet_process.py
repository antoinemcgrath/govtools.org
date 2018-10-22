#!/usr/bin/python3

## https://cloud.digitalocean.com/droplets?i=9b827d&preserveScrollPosition=false
## https://github.com/koalalorenzo/python-digitalocean#add-a-tag-to-a-droplet
## https://github.com/search?q=%22digitalocean.Manager%28token%3D%22&type=Code
#### pip install -U python-digitalocean

import digitalocean
import subprocess
import time

#### This script will login to Digital Ocean
#### Destroy any existing "process-files" droplet
#### Create & start a new "process-files" droplet
#### Determine the new servers IP & SCP a directory to the droplet
#### SSH into the droplet and execute bash commands

## access from instead /home/crscloud/digitalocean.txt
with open('keys.json') as f:
      credentials = [x.strip().split(',') for x in f.readlines()]
      the_token = credentials[0][3]


conversion_script = "convertBill2txt.py"

#subprocess.stdin.write("touch convertBill2txt2.py\n")

# Read text file
with open(conversion_script, 'r') as fp:
    conversion_lines = fp.read()


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


destroy_earlier_droplet(manager, new_droplet_name)

#### Generating new droplet
droplet = digitalocean.Droplet(token=the_token,
                               name=new_droplet_name,
                               region='nyc2', # New York 2
                               image='ubuntu-14-04-x64', # Look up new longterm LTS
                               size_slug='512mb',  # 512MB
                               tag="disposable",
                               ssh_keys=keys, #Automatic conversion
                               backups=False)


droplet.create()


#### Sleep until droplet build is completed
time.sleep(8)
status_is = "starting"
while status_is != "completed":
    time.sleep(1.5)
    actions = droplet.get_actions()
    for action in actions:
        action.load()
        status_is = action.status
        print (status_is)


#### Get droplet IP address
ip_address = manager.get_droplet(droplet.id).ip_address
print(ip_address)


#### Wait untiil droplet OS is running and then send it files through SCP
def scp_files(ip_address):
    print("SCP in 20 secs")
    time.sleep(20.5)
    attempts = 0
    while attempts < 10:
        time.sleep(1.5)
        try:
            subprocess.check_output(["scp",
            "-r", "-o StrictHostKeyChecking no",
            "/home/crscloud/congress.ai/public/upload",
            "root@" + ip_address + ":~/"])
            print("scp success")
            return
        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
            attempts += 1
    print("SCP failed 10 attempts check if digital ocean instance is working, if so check SCP specifics")


#### Execute bash commands on droplet through SSH
def ssh_to_command(ip_address):
    print("SSH file executing")
    sshProcess = subprocess.Popen(['ssh',
                                   "-o StrictHostKeyChecking no",
                                   "root@" + ip_address],
                                  stdin=subprocess.PIPE,
                                  stdout = subprocess.PIPE,
                                  universal_newlines=True,
                                  bufsize=0)
    sshProcess.stdin.write("ls .\n")
    sshProcess.stdin.write("mkdir WORKED\n")
    sshProcess.stdin.write("ls .\n")
    sshProcess.stdin.write("echo END\n")
    sshProcess.stdin.write("cd ~/uploads\n")
    sshProcess.stdin.write("with open(conversion_script, 'w+') as f:\n")
    sshProcess.stdin.write("    f.write(conversion_lines)\n")
    sshProcess.stdin.write("ls .\n")
    #sshProcess.stdin.write("#python3 process.py in.pdf\n")
    sshProcess.stdin.write("logout\n")
    sshProcess.stdin.close()
    for line in sshProcess.stdout:
        if line == "END\n":
            break
        print(line,end="")

    for line in sshProcess.stdout:
        if line == "END\n":
            break
        print(line,end="")


scp_files(ip_address)
ssh_to_command(ip_address)

