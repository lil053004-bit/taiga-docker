# Quick Fix Guide - RabbitMQ vhost Error

## Problem
Creating projects returns: **500 Internal Server Error**
Error: `vhost taiga not found`

---

## ⚡ Quick Fix (3 steps)

### 1️⃣ Run the fix script
```bash
cd /www/kairuiads/project
bash fix-rabbitmq-vhost.sh
```

### 2️⃣ Wait 20 seconds
```bash
sleep 20
```

### 3️⃣ Verify the fix
```bash
bash verify-fix.sh
```

---

## ✅ Test

Go to https://kairui.lhwebs.com and try creating a new project.

**It should work now!**

---

## 📋 What Was Fixed

✓ Updated `.env` with correct passwords
✓ Created RabbitMQ vhost "taiga"
✓ Set proper permissions
✓ Restarted services

---

## ❌ If Still Not Working

See detailed instructions in: **`FIX_INSTRUCTIONS.md`**

Or check logs:
```bash
docker logs project-taiga-back-1 --tail 50
```

---

## 📞 Credentials

- Username: `adsadmin`
- Email: `lhweave@gmail.com`
- Password: `A52290120a`
- Domain: `kairui.lhwebs.com`

---

**Updated:** 2025-12-01
