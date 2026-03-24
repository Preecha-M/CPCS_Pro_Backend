# คู่มือสำหรับผู้ใช้งาน (งานวิจัย): Pull และ Run ผ่าน Docker

เอกสารนี้จัดทำสำหรับผู้ใช้งานปลายทางที่ต้องการรันระบบเพื่อทดสอบ/ใช้งานเชิงงานวิจัย โดยไม่ต้อง build โค้ดเอง

---

## 1) ข้อกำหนดเบื้องต้น

- ติดตั้ง Docker Engine บนเครื่องแล้ว
- สามารถใช้งานคำสั่ง `docker` ได้

ตรวจสอบสถานะ:

```bash
docker --version
docker info
```

หากพบปัญหา `permission denied /var/run/docker.sock`:

```bash
sudo usermod -aG docker $USER
newgrp docker
docker info
```

---

## 2) เตรียมไฟล์ตัวแปรแวดล้อม (`.env`)

สร้างไฟล์ชื่อ `.env` ในโฟลเดอร์ที่ต้องการรันระบบ แล้วกำหนดค่าอย่างน้อยดังนี้:

```env
MONGODB_URI=<your_mongodb_uri>
MONGODB_DB=riceapp
LINE_CHANNEL_ACCESS_TOKEN=<your_line_access_token>
LINE_CHANNEL_SECRET=<your_line_secret>
```

หมายเหตุ:
- แนะนำใช้ MongoDB Atlas สำหรับการทดสอบข้ามเครื่อง
- ไม่ควรเผยแพร่ไฟล์ `.env` ต่อสาธารณะ

---

## 3) Pull image จาก Docker Hub


```bash
docker pull preecha01/ricecare-backend:latest
docker pull preecha01/ricecare-frontend:latest
```

---

## 4) Run ระบบ (เปิดเว็บได้ทันที)

ระบบ frontend ต้องเชื่อมต่อ backend ผ่านชื่อ service `backend` จึงต้องอยู่ใน Docker network เดียวกัน

สร้าง network:

```bash
docker network create ricecare-net
```

รัน backend:

```bash
docker run -d \
  --name backend \
  --network ricecare-net \
  -p 8000:8000 \
  --env-file .env \
  preecha01/ricecare-backend:latest
```

รัน frontend:

```bash
docker run -d \
  --name frontend \
  --network ricecare-net \
  -p 80:80 \
  preecha01/ricecare-frontend:latest
```

---

## 5) การเข้าถึงระบบ

- หน้าเว็บหลัก: `http://localhost`
- ตรวจสอบ backend: `http://localhost:8000/health`

---

## 6) การตรวจสอบสถานะและบันทึกการทำงาน

ตรวจสอบ container:

```bash
docker ps
```

ดู log ล่าสุด:

```bash
docker logs --tail=200 backend
docker logs --tail=200 frontend
```

---

## 7) การปิดระบบหลังใช้งานวิจัย

```bash
docker stop frontend backend
docker rm frontend backend
docker network rm ricecare-net
```

---

## 8) ข้อเสนอแนะสำหรับการอ้างอิงผลการทดลอง

- ควรระบุ image tag ที่ใช้จริง (เช่น `1.0.0`) ในรายงาน เพื่อความสามารถในการทำซ้ำผลลัพธ์
- ควรบันทึกวันเวลาในการทดสอบ และค่า environment ที่สำคัญ (ยกเว้นข้อมูลลับ)
