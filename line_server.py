"""
line_server.py
==============
เซิร์ฟเวอร์หลักสำหรับรัน LINE Bot Webhook ของระบบ Tokyo Smart Transit & Tourism Hybrid Graph RAG

วิธีเริ่มต้นใช้งาน:
1. ตั้งค่า Rich Menu อัตโนมัติและเริ่มรันเซิร์ฟเวอร์:
   python line_server.py --setup-rich-menu

2. รันเซิร์ฟเวอร์ตามปกติ:
   python line_server.py

3. เชื่อมต่อ Cloudflare Tunnel:
   cloudflared tunnel --url http://localhost:8000
   นำ URL ที่ได้ (เช่น https://xxxx.trycloudflare.com/callback) ไปใส่ใน LINE Developers Console
"""

import sys
import argparse
import uvicorn
from dotenv import load_dotenv

# รองรับภาษาไทยบน Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()


def print_line_banner(port: int):
    banner = f"""
================================================================================
       🗼 TOKYO HYBRID GRAPH RAG: LINE BOT WEBHOOK SERVER 🗼
   (FastAPI + LINE Messaging API + Rich Menu + Cloudflare Tunnel Support)
================================================================================
* Local Server: http://localhost:{port}
* Webhook Endpoint: http://localhost:{port}/callback
* Health Check: http://localhost:{port}/health

💡 วิธีเชื่อมต่อผ่าน Cloudflare Tunnel ให้ LINE คุยกับเครื่องได้:
   เปิด Terminal อีกหน้าต่าง แล้วพิมพ์คำสั่ง:
   cloudflared tunnel --url http://localhost:{port}

   คัดลอก URL https://xxxxx.trycloudflare.com/callback ไปวางใน LINE Developers
   -> Webhook settings -> Webhook URL -> กด Verify และเปิด Use webhook
================================================================================
"""
    print(banner)


def main():
    parser = argparse.ArgumentParser(description="Tokyo Hybrid Graph RAG LINE Bot Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host IP address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port number (default: 8000)")
    parser.add_argument("--setup-rich-menu", action="store_true", help="สร้างและลงทะเบียน Rich Menu กับ LINE API ทันที")
    parser.add_argument("--reload", action="store_true", help="เปิด auto-reload สำหรับโหมด dev")

    args = parser.parse_args()

    # ตั้งค่า Rich Menu หากมีการระบุ flag
    if args.setup_rich_menu:
        print("\n🎨 กำลังสร้างและลงทะเบียน Rich Menu ไปยัง LINE Messaging API...")
        from src.line_bot.rich_menu_creator import setup_default_rich_menu
        rich_id = setup_default_rich_menu()
        if rich_id:
            print(f"✅ ลงทะเบียน Rich Menu เรียบร้อย (ID: {rich_id})")
        else:
            print("⚠️ ไม่สามารถลงทะเบียน Rich Menu ได้ กรุณาตรวจสอบ CHANNEL_ACCESS_TOKEN ใน .env")

    print_line_banner(args.port)

    # รัน FastAPI ผ่าน Uvicorn
    uvicorn.run(
        "src.line_bot.webhook:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()
