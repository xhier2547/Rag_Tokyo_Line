"""
main.py
=======
Command Line Interface (CLI) สำหรับระบบ Tokyo Smart Transit & Tourism Hybrid Graph RAG
(Phase 5: System Integration & Application Interface)

วิธีใช้งาน:
1. โหมด Interactive ถาม-ตอบต่อเนื่อง:
   python main.py

2. ถามคำถามเดียวผ่าน Command Line:
   python main.py --query "เดินทางจาก Shinjuku ไป Shibuya ยังไง ใช้เวลากี่นาที"

3. เลือกโหมด LLM Backend:
   python main.py --mode gemini   (ค่าเริ่มต้น: Google Gemini API รวดเร็วและไม่กินสเปกเครื่อง)
   python main.py --mode local    (รันผ่าน Ollama 3B/4B ในเครื่อง)
   python main.py --mode compare  (เปรียบเทียบผลลัพธ์ทั้งสองโมเดลแบบ Side-by-Side)
"""

import sys
import argparse
from typing import Optional
from dotenv import load_dotenv

# รองรับภาษาไทยบน Windows Terminal / Console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()



def print_banner():
    banner = """
================================================================================
       🗼 TOKYO SMART TRANSIT & TOURISM HYBRID GRAPH RAG 🗼
   (Dense RAG + Sparse BM25 + Neo4j Graph + Local 3B/4B & Gemini API)
================================================================================
"""
    print(banner)


def format_rag_output(response) -> None:
    """จัดรูปแบบการแสดงผลคำตอบให้สวยงามและอ่านง่าย"""
    print("\n" + "=" * 80)
    print(f"📌 คำถาม: {response.query}")
    print(f"🎯 เจตนาที่ระบบตรวจจับ (Intent): [{response.intent}]")
    print(f"🤖 โมเดลที่ใช้ประมวลผล: {response.model_name} (โหมด: {response.mode_used})")
    print(f"⏱️ เวลาที่ใช้ทั้งหมด: {response.latency_sec:.3f} วินาที | แคช: {'✅ ใช่ (In-Memory)' if response.is_cached else '❌ ไม่ใช่'}")
    print("-" * 80)
    print("💡 คำตอบจากระบบ:\n")
    print(response.answer)
    print("-" * 80)
    if response.citations:
        print(f"📚 แหล่งอ้างอิง ({len(response.citations)} รายการ):")
        for idx, cit in enumerate(response.citations, 1):
            print(f"   {idx}. {cit}")
    else:
        print("📚 แหล่งอ้างอิง: ไม่พบแท็กอ้างอิงโดยตรงในคำตอบ")
    print("=" * 80 + "\n")


def interactive_session(service, mode: str):
    """รันเซสชันแบบโต้ตอบต่อเนื่องใน Terminal"""
    print(f"\n[ระบบพร้อมใช้งาน] โหมดปัจจุบัน: [{mode.upper()}] (พิมพ์ 'exit' หรือ 'quit' เพื่อออก)")
    print("คำสั่งพิเศษ:")
    print("  :mode gemini   - สลับไปใช้ Gemini API")
    print("  :mode local    - สลับไปใช้ Ollama Local LLM (3B/4B)")
    print("  :mode compare  - สลับไปใช้โหมดเปรียบเทียบ Side-by-Side")
    print("  :clear         - ล้าง Response Cache")
    print("-" * 80)

    current_mode = mode

    while True:
        try:
            user_input = input(f"\n[{current_mode}] ถามคำถามเกี่ยวกับโตเกียว > ").strip()
            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", "q"):
                print("\nขอบคุณที่ใช้งาน Tokyo Smart Transit & Tourism RAG! ลาก่อนครับ 🙏")
                break

            if user_input.startswith(":mode"):
                parts = user_input.split()
                if len(parts) > 1 and parts[1].lower() in ("gemini", "local", "compare"):
                    current_mode = parts[1].lower()
                    print(f"🔄 สลับไปใช้โหมด: [{current_mode.upper()}] เรียบร้อยแล้ว")
                else:
                    print("⚠️ โหมดไม่ถูกต้อง กรุณาระบุ: :mode gemini, :mode local หรือ :mode compare")
                continue

            if user_input == ":clear":
                service.clear_cache()
                continue

            print("🔍 กำลังค้นหาข้อมูลจาก Graph และ Vector Database...")
            resp = service.answer_query(query=user_input, mode=current_mode)
            format_rag_output(resp)

        except KeyboardInterrupt:
            print("\n\nหยุดการทำงานโดยผู้ใช้ ลาก่อนครับ 🙏")
            break
        except Exception as e:
            print(f"\n❌ เกิดข้อผิดพลาดในการประมวลผล: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Tokyo Smart Transit & Tourism Hybrid Graph RAG CLI Application"
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        default=None,
        help="คำถามที่ต้องการถามระบบทันที (หากไม่ระบุจะเข้าสู่โหมด Interactive)"
    )
    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=["gemini", "local", "compare"],
        default="gemini",
        help="โหมด LLM Backend: 'gemini' (แนะนำ, เร็ว, ไม่กินสเปก), 'local' (Ollama 3B/4B), 'compare' (เปรียบเทียบทั้งสองโมเดล)"
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="ล้าง Response Cache ก่อนเริ่มทำงาน"
    )

    args = parser.parse_args()

    print_banner()

    # Lazy import เพื่อให้ CLI แสดง Banner ทันที
    from src.service.rag_service import TokyoRAGService
    service = TokyoRAGService()

    if args.clear_cache:
        service.clear_cache()

    if args.query:
        print(f"\n🔍 กำลังประมวลผลคำถาม: '{args.query}' ในโหมด [{args.mode.upper()}]...")
        resp = service.answer_query(query=args.query, mode=args.mode)
        format_rag_output(resp)
    else:
        interactive_session(service, mode=args.mode)


if __name__ == "__main__":
    main()
