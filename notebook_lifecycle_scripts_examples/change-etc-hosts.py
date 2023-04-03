import subprocess
 
file_path = "/etc/hosts"
ip_address = "127.0.0.1"
hostname = "example.com"
 
# Check if the new entry already exists in the file
with open(file_path, "r") as f:
    if f"{ip_address}\t{hostname}" in f.read():
        print(f"The entry for {hostname} with IP address {ip_address} already exists in {file_path}, no change required!")
        exit()
         
cmd = f"echo '{ip_address}\t{hostname}' | sudo tee -a {file_path}"
subprocess.run(cmd, shell=True)
 
print(f"Added {hostname} with IP address {ip_address} to {file_path}")