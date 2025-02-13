import socket
import threading
import requests
import sqlite3
import datetime

# Configuration
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"
WEBHOOK_URL = ""
LISTEN_PORTS = [21, 22, 23, 25, 53, 137, 138, 139, 445, 80, 443, 1433, 1434, 3389]

# Database Setup
conn = sqlite3.connect("honeypot_logs.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    
)
conn.commit()

def log_to_db(ip, port):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO logs (ip, port, timestamp) VALUES (?, ?, ?)", (ip, port, timestamp))
    conn.commit()

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"[!] Telegram Error: {e}")

def send_webhook_alert(message):
    try:
        requests.post(WEBHOOK_URL, json={"text": message})
    except Exception as e:
        print(f"[!] Webhook Error: {e}")

def fake_service(client, port):
    try:
        fake_responses = {
            21: b"220 Fake FTP Server Ready.\r\n",
            22: b"SSH-2.0-OpenSSH_7.9p1\r\n",
            23: b"Welcome to Telnet honeypot. Enter username: ",
            25: b"220 Fake SMTP Server Ready\r\n",
            53: b"Fake DNS Response\r\n",
            80: b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body>Fake HTTP Server</body></html>",
            443: b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body>Fake HTTPS Server</body></html>",
            3389: b"RDP Protocol Detected\r\n"
        }

        if port in fake_responses:
            client.send(fake_responses[port])
        
        data = client.recv(1024)
        print(f"[FAKE INTERACTION] Received: {data.decode(errors='ignore')}")
    except Exception as e:
        print(f"[!] Error in fake service: {e}")
    
    client.close()

def honeypot_listener(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("0.0.0.0", port))
        server.listen(5)
        print(f"[*] Honeypot active on port {port}")

        while True:
            client, addr = server.accept()
            ip, _ = addr
            message = f"[!] Intrusion detected from {ip} on port {port}"
            print(message)

            log_to_db(ip, port)
            send_telegram_alert(message)
            send_webhook_alert(message)

            threading.Thread(target=fake_service, args=(client, port)).start()

def start_honeypot():
    for port in LISTEN_PORTS:
        thread = threading.Thread(target=honeypot_listener, args=(port,))
        thread.start()

if __name__ == "__main__":
    start_honeypot()
