# RiceCare Platform

![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=black)
![MongoDB](https://img.shields.io/badge/MongoDB-6+-47A248?logo=mongodb&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-5+-646CFF?logo=vite&logoColor=white)

RiceCare Platform เป็นระบบเว็บแอปพลิเคชันสำหรับการจัดการและวิเคราะห์ข้อมูลด้านการดูแลข้าว  
พัฒนาโดยแยกสถาปัตยกรรม **Backend (FastAPI)** และ **Frontend (React + Vite)** อย่างชัดเจน  
รองรับระบบผู้ใช้หลายบทบาท พร้อมระบบยืนยันตัวตนและกำหนดสิทธิ์การเข้าถึง

---

## System Overview

### Architecture
![Architecture Diagram](https://raw.githubusercontent.com/ashleymcnamara/gophers/master/ARCHITECTURE.png)

- Frontend ติดต่อ Backend ผ่าน REST API
- Backend จัดการ Authentication และ Authorization
- ข้อมูลผู้ใช้จัดเก็บใน MongoDB
- ใช้ HttpOnly Cookie สำหรับความปลอดภัย

---

# Backend (FastAPI)

![FastAPI Logo](https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png)

## Features
- REST API ด้วย FastAPI
- Authentication ด้วย JWT (HttpOnly Cookie)
- Password Hashing ด้วย Argon2
- รองรับการอัปเกรด hash จาก bcrypt → argon2 อัตโนมัติ
- Role-based Access Control (admin / researcher)
- เชื่อมต่อ MongoDB

---

## Backend Structure

```text
ricecare_fastapi_lib/
├── app/
│   ├── core/
│   │   ├── auth.py              # JWT + Cookie handling
│   │   ├── password_hasher.py   # Argon2 / bcrypt verify
│   │   └── mongo.py             # MongoDB connection
│   ├── routers/
│   │   ├── auth_api.py          # Login / Register / Me
│   │   └── admin_api.py         # Protected APIs
│   └── main.py                  # FastAPI entry point
├── requirements.txt
└── .env.example
