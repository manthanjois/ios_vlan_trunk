Cisco VLAN & Trunk Automation (Paramiko)
Automates VLAN creation, access port assignment, trunk configuration, interface cleanup, and config save on Cisco IOS switches using Python + Paramiko.
Designed for GNS3 / EVE-NG network automation labs.

Requirements
- GNS3 (with VM)
- Network Automation Appliance (Ubuntu-based) with internet access
- Cisco IOSv or IOSvL2 (v15.6+)
- Python 3.8+
- Paramiko (`pip install paramiko`)

Internet Access (Prerequisite - Before Running Script)
1. In GNS3, add the NAT node (End Devices).
2. Connect the Network Automation Appliance (e.g., eth0) to the NAT node.
3. Start the appliance and obtain an IP via DHCP or static.
4. Verify connectivity: `ping 8.8.8.8`

Files
File                     | Description
-------------------------|------------------------------------------
ssh.txt                  | Initial SSH setup (apply on switch)
vlan_trunk_paramiko.py   | Main automation script

Setup
1. Apply `ssh.txt` on the Cisco switch (paste into CLI to enable SSH).
2. Edit connection details (IP, username, password) in `vlan_trunk_paramiko.py`.
3. Run: `python vlan_trunk_paramiko.py`

Warning: Ensure target interfaces are not in use before running.

Note: All VLANs, ports, and trunk settings are defined in the script. Modify directly in `vlan_trunk_paramiko.py` to suit your topology.
