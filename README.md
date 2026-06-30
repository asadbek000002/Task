## 🧰 Texnologiyalar

FastAPI PostgreSQL Redis Celery SQLAlchemy Alembic Docker & Docker Compose
Pre-commit (black, isort, tests)
___
## 📦 Talablar

Loyihani ishga tushirish uchun quyidagilar o‘rnatilgan bo‘lishi kerak:

Docker

Docker Compose

Git

Python lokal muhitda o‘rnatilgan bo‘lishi shart emas. Barcha servislar Docker ichida ishlaydi.
___

## Loyhani ishga tushirish

1. Repozitoriyani klonlash
```commandline
git clone <repository_url>
cd <project_name>
```
2. Servislarni ishga tushirish
```commandline
docker compose up -d --build
```
3. Migratsiyalarni qo‘llash
```commandline
docker compose exec web alembic upgrade head
```
---

## API hujjatlari

API ishga tushgandan so‘ng quyidagi manzillar orqali foydalanishingiz mumkin:

API: http://localhost:8055

Swagger UI: http://localhost:8055/docs

ReDoc: http://localhost:8055/redoc

---
## Email Verification

Ro‘yxatdan o‘tishda haqiqiy email manzil kiriting.
Tizim foydalanuvchining email manziliga tasdiqlash havolasini yuboradi. Hisobni aktivlashtirish uchun emaildagi havolani ochish kerak.

---


## 🎯 Pre-commit ishlatish
1️⃣ Pre-commit o‘rnatish (lokal)
```commandline
pip install pre-commit
```
---
2️⃣ Hook’larni faollashtirish
```commandline
pre-commit install
```

---
### 🔍 Pre-commit tekshiruvlari

isort – import tartibi

black – kod formatlash

trailing whitespace

backend testlar

Commit vaqtida avtomatik ishlaydi 🚀

---
## 🗂️ Project structure
```commandline
.
├── apps/
│   ├── comments/
│   ├── email/
│   ├── users/
│   └── posts/
├── core/
│   ├── database.py
│   ├── celery.py
│   └── core.py
├── docs/
├── tests/
├── .env
├── .pre-commit-config.yaml
├── docker-compose.yml
├── Dockerfile
├── main.py
└── README.md

```

## Inactive userlarni tozalashni test qilish

```commandline
Testlash uchun:

Fayl: apps/users/router.py – qator 38
expires_at = datetime.now(timezone.utc) + timedelta(seconds=10)  # test uchun 10 sekund

Fayl: core/celery.py – qator 22
"schedule": 10.0, # test uchun 10 sekund

Shu o‘zgartirish bilan inactive userlar test vaqtida tez tozalanadi.
```


### Postman Collection
Yuklab olish uchun [bu yerni bosing](docs/postman_collection.json))

## ❗️register-da haqiyqi email kirgazing tastiqlash uchun emailga url manzil boradi


## Asosiy imkoniyatlar
```
JWT Authentication
Email Verification
User Profile Management
Posts CRUD
Comments CRUD
Post Likes
Search & Filtering
Pagination
Redis
Celery Worker
Celery Beat
Automatic Cleanup of Expired Unverified Users
Dockerized Infrastructure
```
