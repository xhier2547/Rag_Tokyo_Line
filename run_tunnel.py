"""
run_tunnel.py
=============
สคริปต์เปิด Cloudflare Tunnel สำหรับเชื่อมต่อ LINE Webhook เข้ากับเซิร์ฟเวอร์ Local

วิธีใช้งาน:
1. ตรวจสอบให้แน่ใจว่าได้เปิดเซิร์ฟเวอร์ LINE Bot แล้ว (python line_server.py)
2. รันสคริปต์นี้:
   python run_tunnel.py
"""

import sys
import subprocess
import re
import time

# รองรับภาษาไทยบน Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_cloudflare_tunnel(port: int = 8000):
    print("=" * 80)
    print("       ☁️ CLOUDFLARE TUNNEL FOR TOKYO RAG LINE BOT ☁️")
    print("=" * 80)
    print(f"🚀 กำลังเปิด Cloudflare Tunnel ไปยังพอร์ต {port}...")

    cmd = ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"]

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        tunnel_url = None
        for line in process.stdout:
            # ค้นหา URL ที่ลงท้ายด้วย trycloudflare.com
            match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if match and not tunnel_url:
                tunnel_url = match.group(0)
                webhook_url = f"{tunnel_url}/callback"

                print("\n" + "=" * 80)
                print("🎉 CLOUDFLARE TUNNEL เชื่อมต่อสำเร็จแล้ว!")
                print("-" * 80)
                print(f"🌐 Public Tunnel URL : {tunnel_url}")
                print(f"📲 LINE Webhook URL  : {webhook_url}")
                print("-" * 80)
                print("📋 ขั้นตอนถัดไปใน LINE Developers Console:")
                print("  1. ไปที่ Messaging API -> Webhook settings")
                print(f"  2. วาง Webhook URL: {webhook_url}")
                print("  3. กดปุ่ม 'Update' แล้วกด 'Verify' (ต้องขึ้น Success)")
                print("  4. เลื่อนเปิด 'Use webhook' ให้เป็น สีเขียว")
                print("=" * 80 + "\n")
                print("🔔 กำลังรับส่งข้อมูลกับ LINE... (กด Ctrl+C เพื่อหยุดการทำงาน)\n")

            # แสดง Log ของ Tunnel
            if "INF" in line or "ERR" in line:
                print(f"[Cloudflare] {line.strip()}")

    except KeyboardInterrupt:
        print("\n🛑 หยุดการทำงานของ Cloudflare Tunnel แล้ว")
    except FileNotFoundError:
        print("❌ ไม่พบคำสั่ง 'cloudflared' ในเครื่อง กรุณาติดตั้ง cloudflared ก่อนใช้งาน")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")


if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run_cloudflare_tunnel(port)
