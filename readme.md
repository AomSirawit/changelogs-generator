# Changelog Generator

สคริปต์สร้าง Changelog อัตโนมัติด้วย Google Gemini AI

## คำอธิบาย

สคริปต์นี้จะดึงข้อมูล Git commits ของคุณในแต่ละวัน แล้วใช้ AI (Google Gemini) วิเคราะห์และสร้างเป็น Changelog ที่มีรูปแบบสม่ำเสมอโดยอัตโนมัติ โดยจะเรียนรู้รูปแบบการเขียนจากไฟล์ Changelog ที่ผ่านมา

## ความสามารถ

- ✅ ดึง Git commits อัตโนมัติตามช่วงเวลาที่กำหนด
- ✅ รองรับ Workday Logic (ถ้ารันก่อนตี 5 จะนับเป็นของวันก่อนหน้า)
- ✅ สร้าง Changelog ด้วย Google Gemini AI
- ✅ เรียนรู้รูปแบบการเขียนจากไฟล์ตัวอย่างที่มีอยู่
- ✅ บันทึกไฟล์และเพิ่มเข้า Git staging area อัตโนมัติ

## ข้อกำหนดเบื้องต้น

1. Python 3.x
2. Git repository ที่มี commit history
3. Google Gemini API Key

## การติดตั้ง

1. ติดตั้ง dependencies:
```bash
pip install google-generativeai
```

2. ตั้งค่า API Key:
```bash
export GEMINI_API_KEY='your-api-key-here'
```

หรือเพิ่มในไฟล์ `.bashrc` / `.zshrc` เพื่อให้ใช้งานถาวร:
```bash
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

## การใช้งาน

รันสคริปต์ด้วยคำสั่ง:
```bash
python script.py
```

สคริปต์จะ:
1. คำนวณวันที่ทำงาน (ถ้ารันก่อนตี 5 จะนับเป็นของวันก่อนหน้า)
2. ดึง Git commits ตั้งแต่เที่ยงคืนของวันนั้น
3. ส่งข้อมูลให้ Gemini AI วิเคราะห์
4. สร้างไฟล์ Changelog ที่ `laravel/docs/planning/operations/changelogs/YYYY-MM-DD-Aom.md`
5. เพิ่มไฟล์เข้า Git staging area อัตโนมัติ

## การตั้งค่า

แก้ไขค่าคงที่ในสคริปต์ตามต้องการ:

```python
OUTPUT_DIR = "laravel/docs/planning/operations/changelogs"  # โฟลเดอร์ที่จะบันทึกไฟล์
FILE_SUFFIX = "-Aom.md"  # ส่วนท้ายของชื่อไฟล์
CUTOFF_HOUR = 5  # เวลาตัดยอดวัน (ตี 5)
```

## Workday Logic

สคริปต์ใช้ตรรกะพิเศษในการกำหนดวันที่:
- ถ้ารันสคริปต์ **ก่อนตี 5** → จะนับเป็น Changelog ของ **วันก่อนหน้า**
- ถ้ารันสคริปต์ **หลังตี 5** → จะนับเป็น Changelog ของ **วันนั้น**

ระบบนี้เหมาะสำหรับคนที่ทำงานข้ามคืนและต้องการให้ commit ที่ทำตอนดึกนับรวมกับวันทำงานเดียวกัน

## ตัวอย่างการใช้งาน

```bash
$ python script.py
======================================================================
เริ่มต้นการสร้าง Changelog อัตโนมัติ
======================================================================

[ข้อมูลวันที่]
- วันที่ทำงาน: 2026-03-09
- ดึงข้อมูลตั้งแต่: 2026-03-09 00:00:00

[Git] กำลังดึงประวัติ Commit จาก Git Repository...
[Git] พบ Commit ทั้งหมด: 15 รายการ

[AI] กำลังประมวลผลข้อมูลโดย Gemini AI...
[AI] อ่านไฟล์ Changelog ตัวอย่างเพื่อเรียนรูปแบบการเขียน...
[AI] วิเคราะห์และสรุป Commit เป็น Changelog...
[AI] สร้างเนื้อหา Changelog สำเร็จ

[ไฟล์] กำลังบันทึกและเพิ่มเข้า Git...
[Git] เพิ่มไฟล์เข้า Staging Area สำเร็จ

======================================================================
สำเร็จ! Changelog ถูกสร้างเรียบร้อยแล้ว
======================================================================
ไฟล์ที่สร้าง: laravel/docs/planning/operations/changelogs/2026-03-09-Aom.md
สถานะ: พร้อม Commit (ไฟล์อยู่ใน Staging Area แล้ว)

ขั้นตอนถัดไป: รัน 'git commit' และ 'git push' เพื่ออัปโหลดไฟล์
```

## การแก้ปัญหา

### ไม่พบ API Key
```
[ข้อผิดพลาด] ไม่พบ Environment Variable 'GEMINI_API_KEY'
```
**แก้ไข:** ตั้งค่า environment variable `GEMINI_API_KEY`

### ไม่พบ Commit
```
[ผลลัพธ์] ไม่พบ Commit ใดๆ ของคุณในช่วงเวลาที่กำหนด
```
**สาเหตุ:** 
- ยังไม่มี commit ในช่วงเวลาที่กำหนด
- ชื่อผู้ใช้ Git ไม่ตรงกับผู้ commit

### ไม่สามารถประมวลผลด้วย AI ได้
```
[ข้อผิดพลาด] ไม่สามารถประมวลผลด้วย AI ได้
```
**แก้ไข:** 
- ตรวจสอบ API Key ว่าถูกต้อง
- ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
- ตรวจสอบโควต้าการใช้งาน Gemini API

## หมายเหตุ

- สคริปต์จะใช้ `git config user.name` เพื่อดึง commit ของคุณเท่านั้น
- ไฟล์ Changelog จะถูก `git add` อัตโนมัติ คุณแค่ต้อง commit และ push
- AI จะเรียนรู้จากไฟล์ Changelog ล่าสุด 1 ไฟล์ (ปรับได้ที่ `limit=1` ในฟังก์ชัน `get_previous_changelogs`)

## License

MIT
