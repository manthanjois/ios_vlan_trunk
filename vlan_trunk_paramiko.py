import paramiko
import time

ip_address = "" #add nat network ip
username   = "" #ssh username
password   = "" #ssh password

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(ip_address, username=username, password=password, timeout=10, look_for_keys=False, allow_agent=False)

r = ssh.invoke_shell()
time.sleep(2)
r.recv(9999).decode('utf-8', errors='ignore')  # Clear initial buffer

def send(cmd, wait=0.8):
    print(f">>> {cmd}")
    r.send(cmd + "\n")
    time.sleep(wait)
    # Optional: drain output to prevent buffer overflow
    while r.recv_ready():
        r.recv(9999)

print(f"[+] Connected to {ip_address}")

# === Enter enable mode ===
send("enable")
send(password)                    # enable password
time.sleep(1)

# === Terminal length 0 (no pagination) ===
send("terminal length 0")

# === Enter global config ===
send("conf t", 2)

# === 1. Create VLANs 2-6 ===
for v in range(2, 7):
    send(f"vlan {v}")
    send(f"name VLAN_{v}")
    send("exit")

# === 2. Assign ONE access port per VLAN ===
access_assignments = {
    2: "GigabitEthernet0/2",
    3: "GigabitEthernet0/3",
    4: "GigabitEthernet1/0",
    5: "GigabitEthernet1/1",
    6: "GigabitEthernet1/2"
}

for vlan, port in access_assignments.items():
    send(f"interface {port}")
    send("switchport mode access")
    send(f"switchport access vlan {vlan}")
    send("spanning-tree portfast")
    send(f"description VLAN_{vlan}_ACCESS")
    send("exit")

# === 3. Configure Gi0/1 as TRUNK (only VLANs 2-6) ===
send("interface GigabitEthernet0/1")
send("switchport trunk encapsulation dot1q")   # Needed on older platforms
send("switchport mode trunk")
send("switchport trunk native vlan 999")       # Isolate native VLAN
send("switchport trunk allowed vlan 2-6")      # Cleaner range syntax
send("description UPLINK_TRUNK_TO_ROUTER")
send("spanning-tree portfast trunk")           # Optional but safe for edge trunks
send("exit")

# === 4. Shutdown all unused ports (adjust list for your switch model) ===
unused_ports = [
    "GigabitEthernet0/0", "GigabitEthernet0/1",  # Gi0/1 is trunk → remove from shutdown!
    "GigabitEthernet1/3",
    "GigabitEthernet2/0", "GigabitEthernet2/1", "GigabitEthernet2/2", "GigabitEthernet2/3",
    "GigabitEthernet3/0", "GigabitEthernet3/1", "GigabitEthernet3/2", "GigabitEthernet3/3"
]

# Remove trunk port from shutdown list
unused_ports = [p for p in unused_ports if p != "GigabitEthernet0/1"]

if unused_ports:
    send("interface range " + ", ".join(unused_ports))
    send("shutdown")
    send("description UNUSED_SHUTDOWN")
    send("exit")

# === 5. Save config ===
send("end")
send("wr mem", 6)

# === Capture final output ===
time.sleep(3)
output = ""
while r.recv_ready():
    output += r.recv(9999).decode('utf-8', errors='ignore')

ssh.close()

# === Pretty final banner ===
print("\n" + "="*80)
print(" FINAL CONFIGURATION APPLIED SUCCESSFULLY ".center(80, "="))
print("="*80)
print(output[-3000:])  # Last 3000 chars usually contain the save confirmation

print("\nDONE! PERFECT SETUP:")
print("   VLAN_2 → Gi0/2    VLAN_3 → Gi0/3")
print("   VLAN_4 → Gi1/0    VLAN_5 → Gi1/1    VLAN_6 → Gi1/2")
print("   Gi0/1  → TRUNK (allowed 2-6, native 999)")
print("   All unused ports → shutdown")
print("\nVerify with:")
print("   show vlan brief")
print("   show interfaces trunk")
print("   show interfaces switchport")
print("   show run interface Gi0/1")