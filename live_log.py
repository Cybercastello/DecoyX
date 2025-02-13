import sqlite3
import time

def tail_logs():
    conn = sqlite3.connect("honeypot_logs.db")
    cursor = conn.cursor()
    last_id = 0
    
    while True:
        cursor.execute("SELECT * FROM logs WHERE id > ? ORDER BY id ASC", (last_id,))
        rows = cursor.fetchall()
        
        for row in rows:
            log_id, ip, port, timestamp = row
            print(f"[LIVE LOG] {timestamp} - {ip} accessed port {port}")
            last_id = log_id 
        
        time.sleep(2) 

if __name__ == "__main__":
    tail_logs()