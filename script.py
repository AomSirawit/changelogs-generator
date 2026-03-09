import os
import subprocess
import datetime
import glob
import google.generativeai as genai

# ตั้งค่าพื้นฐาน 
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("[ข้อผิดพลาด] ไม่พบ Environment Variable 'GEMINI_API_KEY'")
    print("กรุณาตั้งค่า API Key ก่อนรันสคริปต์: export GEMINI_API_KEY='your-api-key'")
    exit(1)

genai.configure(api_key=API_KEY)

# ตั้งค่า Path และชื่อไฟล์ตามโครงสร้างโปรเจค
OUTPUT_DIR = "laravel/docs/planning/operations/changelogs"
FILE_SUFFIX = "-Aom.md"
CUTOFF_HOUR = 5 # ตั้งเวลาตัดยอดวัน (ตี 5) ถ้ารันก่อนตี 5 จะนับเป็นของเมื่อวาน

# Template สำหรับ AI
PROMPT_TEMPLATE = """
คุณคือผู้ช่วยเขียน Changelog แบบมืออาชีพ
วันที่ปัจจุบันคือ: {work_date}

กรุณานำข้อมูล Git Commits ของวันนี้ไปสรุปและเขียนเป็น Changelog 
โดยให้ยึดรูปแบบ โครงสร้าง หัวข้อ และสไตล์การเขียนจาก "ตัวอย่างไฟล์ Changelog ที่ผ่านมา" อย่างเคร่งครัด
**สำคัญมาก: ให้ใช้วันที่ ({work_date}) ในการเขียนเนื้อหา ห้ามคัดลอกวันที่จากไฟล์ตัวอย่างเด็ดขาด**

{previous_examples}

--- ข้อมูล Git Commits ของวันนี้ ---
{git_logs}

กรุณาสร้างเนื้อหาสำหรับไฟล์ Changelog ของวันนี้ออกมาตามรูปแบบตัวอย่างได้เลย
"""

# ฟังก์ชันจัดการเรื่องเวลา (Workday Logic)
def get_workday_info():
    """คำนวณหาวันที่ทำงานจริง และเวลาเริ่มนับ Commit"""
    now = datetime.datetime.now()
    
    # ถ้ารันสคริปต์ก่อนเวลา CUTOFF_HOUR (เช่น รันตอนตี 2)
    if now.hour < CUTOFF_HOUR:
        # ให้นับวันที่เป็นของ "เมื่อวาน"
        work_date = now.date() - datetime.timedelta(days=1)
    else:
        # ถ้ารันหลังตี 5 ไปแล้ว ก็นับเป็นของ "วันนี้" ตามปกติ
        work_date = now.date()
        
    work_date_str = work_date.strftime("%Y-%m-%d")
    
    # กำหนดให้ดึง Commit ตั้งแต่เที่ยงคืนของวันที่คำนวณได้
    since_time = f"{work_date_str} 00:00:00"
    
    return work_date_str, since_time

# ฟังก์ชันหลัก
def get_today_git_logs(since_time):
    """ดึง Git log ตามเวลา since_time ที่กำหนด"""
    try:
        author = subprocess.check_output(['git', 'config', 'user.name']).decode('utf-8').strip()
        log_command = [
            'git', 'log', 
            f'--since="{since_time}"', 
            f'--author={author}', 
            '--oneline', 
            '--no-merges'
        ]
        return subprocess.check_output(log_command).decode('utf-8').strip()
    except subprocess.CalledProcessError:
        return None

def get_previous_changelogs(limit=1):
    """อ่านไฟล์ Changelog ล่าสุด เพื่อใช้เป็นตัวอย่าง"""
    example_text = ""
    search_pattern = os.path.join(OUTPUT_DIR, f"*{FILE_SUFFIX}")
    files = glob.glob(search_pattern)
    
    if not files:
        return "--- ยังไม่มีตัวอย่างไฟล์ Changelog ที่ผ่านมา ---"
        
    files.sort(reverse=True)
    recent_files = files[:limit]
    
    example_text += "--- ตัวอย่างไฟล์ Changelog ที่ผ่านมา ---\n"
    for file in recent_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                example_text += f"\n[อ้างอิงจากไฟล์ {os.path.basename(file)}]\n{content}\n"
        except Exception as e:
            print(f"[คำเตือน] ไม่สามารถอ่านไฟล์ตัวอย่าง {file} สาเหตุ: {e}")
            
    example_text += "--------------------------------------\n"
    return example_text

def generate_changelog(logs, work_date_str):
    """ส่งข้อมูลให้ AI ประมวลผล"""
    examples = get_previous_changelogs(limit=1)
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = PROMPT_TEMPLATE.format(
        work_date=work_date_str,
        previous_examples=examples, 
        git_logs=logs
    )
    
    response = model.generate_content(prompt)
    return response.text

def save_and_track_changelog(content, work_date_str):
    """บันทึกไฟล์และสั่ง git add"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    filename = f"{work_date_str}{FILE_SUFFIX}"
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    try:
        subprocess.run(['git', 'add', file_path], check=True)
        print(f"[Git] เพิ่มไฟล์เข้า Staging Area สำเร็จ: {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"[ข้อผิดพลาด] ไม่สามารถรันคำสั่ง git add ได้")
        print(f"รายละเอียด: {e}")
        
    return file_path

# การทำงานหลัก (Main)
if __name__ == "__main__":
    print("="*70)
    print("เริ่มต้นการสร้าง Changelog อัตโนมัติ")
    print("="*70)
    
    # คำนวณหาวันที่ทำงานจริง
    work_date_str, since_time = get_workday_info()
    print(f"\n[ข้อมูลวันที่]")
    print(f"- วันที่ทำงาน: {work_date_str}")
    print(f"- ดึงข้อมูลตั้งแต่: {since_time}")
    
    print(f"\n[Git] กำลังดึงประวัติ Commit จาก Git Repository...")
    logs = get_today_git_logs(since_time)
    
    if not logs:
        print(f"\n[ผลลัพธ์] ไม่พบ Commit ใดๆ ของคุณในช่วงเวลาที่กำหนด")
        print(f"ช่วงเวลาที่ตรวจสอบ: ตั้งแต่ {since_time} เป็นต้นไป")
        exit(0)
    
    commit_count = len(logs.split('\n'))
    print(f"[Git] พบ Commit ทั้งหมด: {commit_count} รายการ")
        
    print(f"\n[AI] กำลังประมวลผลข้อมูลโดย Gemini AI...")
    print(f"[AI] อ่านไฟล์ Changelog ตัวอย่างเพื่อเรียนรูปแบบการเขียน...")
    print(f"[AI] วิเคราะห์และสรุป Commit เป็น Changelog...")
    try:
        changelog_content = generate_changelog(logs, work_date_str)
    except Exception as e:
        print(f"\n[ข้อผิดพลาด] ไม่สามารถประมวลผลด้วย AI ได้")
        print(f"รายละเอียด: {e}")
        print(f"กรุณาตรวจสอบ API Key และการเชื่อมต่ออินเทอร์เน็ต")
        exit(1)
    
    print(f"[AI] สร้างเนื้อหา Changelog สำเร็จ")
    
    print(f"\n[ไฟล์] กำลังบันทึกและเพิ่มเข้า Git...")
    saved_path = save_and_track_changelog(changelog_content, work_date_str)
    
    print("\n" + "="*70)
    print("สำเร็จ! Changelog ถูกสร้างเรียบร้อยแล้ว")
    print("="*70)
    print(f"ไฟล์ที่สร้าง: {saved_path}")
    print(f"สถานะ: พร้อม Commit (ไฟล์อยู่ใน Staging Area แล้ว)")
    print("\nขั้นตอนถัดไป: รัน 'git commit' และ 'git push' เพื่ออัปโหลดไฟล์")