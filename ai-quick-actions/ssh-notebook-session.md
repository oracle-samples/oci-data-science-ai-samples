
# SSH Data Science Notebook Session

## Table of Contents
  - [Introduction](#introduction)
  - [Prerequisite](#prerequisite)
  - [Step-by-Step Guide](#step-by-step-guide)
    - [Reveal the Notebook Private IP](#reveal-the-notebook-private-ip)
    - [Run the Script](#run-the-script)
    - [Enable OpenSSH Server Script](#enable-openssh-server-script)
    - [Run the `enablessh.sh` Script](#run-the-enablesshsh-script)
    - [Store the Private Key](#store-the-private-key)
    - [Create Bastion](#create-bastion)
    - [Create Bastion Session](#create-bastion-session)
    - [Connect to the Bastion](#connect-to-the-bastion)
    - [Tunnel](#tunnel)
    - [VSCode Configuration](#vscode-configuration)

## Introduction
Enabling the SSH tunnel to OCI Data Science notebooks provides the ability to do remote debugging and coding using tools like VSCode Remote-SSH or PyCharm's equivalent feature. Additionally, you can connect to the instance for manual debugging.

## Prerequisite
- Create a [Notebook Session](https://docs.oracle.com/en-us/iaas/data-science/using/manage-notebook-sessions.htm) in OCI Data Science Service using your own [VCN](https://docs.oracle.com/en-us/iaas/Content/Network/Tasks/VCNs.htm) and [Private Subnet](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/privateaccess.htm).

## Step-by-Step Guide
This guide outlines the steps required to enable SSH tunneling.

### Reveal the Notebook Private IP
Create a file named `nb_ip.py` and add the following Python code to reveal the private IP address of the notebook:

```python
import oci
import os

print(f"- get NB_SESSION_OCID")
NB_OCID = os.environ.get("NB_SESSION_OCID")
if NB_OCID is None:
    raise Exception("NB_SESSION_OCID environment variable is required.")

print(f"- init RP")
RP = os.environ.get("OCI_RESOURCE_PRINCIPAL_VERSION", "UNDEFINED")

if not RP or RP == "UNDEFINED":
    # LOCAL RUN
    config = oci.config.from_file("~/.oci/config", "DEFAULT")
    dsc = oci.data_science.DataScienceClient(config=config)
    network = oci.core.VirtualNetworkClient(config=config)
else:
    # NB RP
    signer = oci.auth.signers.get_resource_principals_signer()
    dsc = oci.data_science.DataScienceClient(config={}, signer=signer)
    network = oci.core.VirtualNetworkClient(config={}, signer=signer)

print(f"- get notebook data")
nb = dsc.get_notebook_session(NB_OCID).data
print(f"- notebook data: {nb}")

if not nb.notebook_session_configuration_details or not nb.notebook_session_configuration_details.subnet_id:
    raise Exception("IP Address cannot be determined when Default Networking is in use! For SSH tunneling to work, you must specify your own VCN and Private subnet!")

print(f"- get notebook subnet")
subnet_id = nb.notebook_session_configuration_details.subnet_id
print(f"- notebook subnet ocid: {subnet_id}")

print(f"- get subnet data")
subnet = network.get_subnet(subnet_id).data

print("- fetching subnet private IPs")
private_ips = oci.pagination.list_call_get_all_results(
    network.list_private_ips, subnet_id=subnet_id
).data

print("- finding the private IP for notebook session")
display_name = NB_OCID.split(".")[-1]
private_ip = [i for i in private_ips if i.display_name == display_name][0]

print(f"- private IP address: {private_ip.ip_address}")
```

### Run the Script
Run the script in the notebook to reveal the private IP address. Note the private IP address provided in the output:

```bash
python nb_ip.py
```

If the script runs successfully you will see something like:
```bash
(base) bash-4.2$ python nb_ip.py
- get NB_SESSION_OCID
- init RP
- get notebook data
- get notebook subnet
- notebook subnet ocid: ocid1.subnet.oc1.iad...
- get subnet data
- fetching subnet private IPs
- finding the private IP for notebook session
- private IP address: 10.0.1.167
```

**_NOTE_:** The last line "private IP address: 10.0.1.167" is the private IP of the notebook in the private subnet used to create the notebook.

### Enable OpenSSH Server Script
Create a file named `enablessh.sh` with the following script to install and enable the OpenSSH server, generate RSA keys for authentication, and start the server:

```bash
sudo yum install -y openssh-server
ssh-keygen -b 4096 -f $HOME/.ssh/ssh_host_rsa_key -t rsa -N ""
sudo ssh-keygen -A
cat $HOME/.ssh/ssh_host_rsa_key.pub >> $HOME/.ssh/authorized_keys
cat $HOME/.ssh/ssh_host_rsa_key
sudo cp /etc/environment /etc/environment2
sudo chmod 666 /etc/environment
env | grep OCI >> /etc/environment
echo "Run the OpenSSH Server on Port: 12345"
sudo /usr/sbin/sshd -p 12345; sleep infinity
```

### Run the `enablessh.sh` Script
Run the script in the notebook to proceed with the required operations:

```bash
sh enablessh.sh
```

If the script runs successfully you will see something like:
```bash
(base) bash-4.2$ sh enablessh.sh
Loaded plugins: ovl
Package openssh-server-7.4p1-22.0.1.el7_9.x86_64 already installed and latest version
Nothing to do
Generating public/private rsa key pair.
/home/datascience/.ssh/ssh_host_rsa_key already exists.
Overwrite (y/n)? n
-----BEGIN RSA PRIVATE KEY-----
key code goes here
-----END RSA PRIVATE KEY-----
Run the OpenSSH Server on Post: 12345
```

**_NOTE:_** We print the private key, so you could easily copy it and store on your local machine. You can change the script to not do that if you like. Also notice that the script will show an message that the Open SSH Server is running on specific port. Do not stop or exit the script, otherwise the SSH server will stop executing as well.

### Store the Private Key
Copy the private RSA key from the `enablessh.sh` script output and store it on your local machine. Execute the command `chmod 600 private.key` on the key to use it for SSH authentication.

### Create Bastion
**_NOTE:_** This step can be skipped if you have configured [FastConnect](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/fastconnect.htm) between your on-premises network and virtual cloud network (VCN).

Create an OCI Bastion instance to SSH tunnel and access the notebook in the private subnet. Ensure that the Bastion instance points to the VCN and subnet used by your notebook. Set the CIDR block to allow access from your local machine's IP address or range of IPs from your corporate network.

### Create Bastion Session
To open an SSH tunnel, create a session in the Bastion instance with the following settings:

- **Session type:** SSH port forwarding session
- **Session name:** Free text
- **Connect to the target host by using:**
  - IP address: 10.0.1.167 (private IP address from the logs)
  - Port: 12345 (the port set in the SSHD)

Generate an SSH key pair and store it on your machine.

### Connect to the Bastion
Once the Bastion session is running, connect to the Bastion instance and open the tunnel:

```bash
ssh -i <privateKey> -N -L <localPort>:10.0.1.167:12345 -p 22 ocid1.bastionsession.oc1.iad...@host.bastion.us-ashburn-1.oci.oraclecloud.com
```

Replace `<privateKey>` with the RSA private key file created earlier and `<localPort>` with the desired local port.

### Tunnel
Use the SSH tunnel to connect directly to the OpenSSH server in the notebook:

```bash
ssh -i private.key datascience@localhost -p <localPort>
```

You should now be able to see and execute all the ODSC and conda commands, install new Conda environments, and use VSCode Remote-SSH for remote working and debugging.

**_Note:_** The Bastion session expires after 3 hours, requiring a new session for continued access.

### VSCode Configuration
To use the VSCode Remote SSH feature, add the localhost configuration to your local machine's SSH config file:

```bash
vi ~/.ssh/config
```

Add the following entry:

```bash
Host localhost
    HostName localhost
    User datascience
    Port 12345
    IdentityFile <path to your notebook RSA key on your machine>/private.key
```

Open VSCode and use the Remote-SSH: Connect to Host feature to select localhost from the list, bringing you directly into the notebook.
