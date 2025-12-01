# Complete Taiga Fix Guide

## Current Errors Diagnosed

### 1. 500 Error - Creating Projects Fails
**Error Messages:**
- `vhost taiga not found`
- `User taiga does not exist`

**Root Cause:** RabbitMQ containers have old credentials and the user/vhost weren't properly created.

### 2. 404 Error - User Storage API
**Error Message:**
- `GET /api/v1/user-storage/dont_ask_premise_newsletter 404 (Not Found)`
- `{"_error_message": "No StorageEntry matches the given query."}`

**Root Cause:** Database migrations haven't been run to create user-storage tables.

### 3. Gravatar Tracking Prevention
**Warning:** Browser blocking Gravatar third-party storage (non-critical, cosmetic only).

---

## Solutions - Choose Your Path

### 🚀 Path 1: Complete Reset (RECOMMENDED - Fastest & Cleanest)

**Best for:** Fresh start with guaranteed working configuration

**Time:** 3-5 minutes

**Data Loss:** Only RabbitMQ message queues (database and projects are SAFE)

```bash
cd /www/kairuiads/project

# Run the automated reset script
bash reset-rabbitmq.sh

# After reset completes, run migrations
bash fix-user-storage.sh

# Verify everything works
bash verify-fix.sh
```

**What this does:**
1. Stops all services
2. Removes RabbitMQ data volumes
3. Restarts with fresh RabbitMQ using correct credentials from .env
4. Creates user 'taiga' and vhost 'taiga' automatically
5. Runs database migrations for user-storage

---

### 🔧 Path 2: Manual Fix (If Reset Not Desired)

**Best for:** Want to keep existing RabbitMQ queues (usually unnecessary)

**Time:** 5-10 minutes

**Data Loss:** None

```bash
cd /www/kairuiads/project

# Fix RabbitMQ manually (creates user and vhost)
bash fix-rabbitmq-vhost.sh

# Wait for services to restart
sleep 20

# Run migrations for user-storage
bash fix-user-storage.sh

# Verify everything works
bash verify-fix.sh
```

**What this does:**
1. Creates 'taiga' user with password A52290120a in both RabbitMQ containers
2. Creates 'taiga' vhost if it doesn't exist
3. Sets proper permissions
4. Restarts affected services
5. Runs database migrations

---

### 🐛 Path 3: Step-by-Step Manual Commands

**Best for:** Debugging or understanding what's happening

**Time:** 10-15 minutes

#### Step 1: Fix RabbitMQ Events Container

```bash
cd /www/kairuiads/project

# Create user
docker exec project-taiga-events-rabbitmq-1 rabbitmqctl add_user taiga A52290120a

# Make user admin
docker exec project-taiga-events-rabbitmq-1 rabbitmqctl set_user_tags taiga administrator

# Create vhost (if not exists)
docker exec project-taiga-events-rabbitmq-1 rabbitmqctl add_vhost taiga

# Set permissions
docker exec project-taiga-events-rabbitmq-1 rabbitmqctl set_permissions -p taiga taiga ".*" ".*" ".*"

# Verify
docker exec project-taiga-events-rabbitmq-1 rabbitmqctl list_users
docker exec project-taiga-events-rabbitmq-1 rabbitmqctl list_vhosts
docker exec project-taiga-events-rabbitmq-1 rabbitmqctl list_permissions -p taiga
```

#### Step 2: Fix RabbitMQ Async Container

```bash
# Create user
docker exec project-taiga-async-rabbitmq-1 rabbitmqctl add_user taiga A52290120a

# Make user admin
docker exec project-taiga-async-rabbitmq-1 rabbitmqctl set_user_tags taiga administrator

# Create vhost (if not exists)
docker exec project-taiga-async-rabbitmq-1 rabbitmqctl add_vhost taiga

# Set permissions
docker exec project-taiga-async-rabbitmq-1 rabbitmqctl set_permissions -p taiga taiga ".*" ".*" ".*"

# Verify
docker exec project-taiga-async-rabbitmq-1 rabbitmqctl list_users
docker exec project-taiga-async-rabbitmq-1 rabbitmqctl list_vhosts
docker exec project-taiga-async-rabbitmq-1 rabbitmqctl list_permissions -p taiga
```

#### Step 3: Restart Services

```bash
docker compose restart taiga-back taiga-events taiga-async
sleep 20
```

#### Step 4: Run Database Migrations

```bash
bash taiga-manage.sh migrate
```

#### Step 5: Verify

```bash
# Check logs
docker logs project-taiga-back-1 --tail 50 | grep -i "error\|rabbitmq"

# Should see no RabbitMQ errors
```

---

## Verification Checklist

After running any fix path, verify with:

```bash
bash verify-fix.sh
```

**Expected results:**

✅ **Container Status:**
- All containers show "Up" or "running"

✅ **RabbitMQ Users:**
- User "taiga" exists in both containers
- User has "administrator" tag

✅ **RabbitMQ Vhosts:**
- Vhost "taiga" exists in both containers

✅ **RabbitMQ Permissions:**
- User "taiga" has full permissions (.*) on vhost "taiga"

✅ **Backend Logs:**
- No "vhost taiga not found" errors
- No "User taiga does not exist" errors

✅ **Web Interface:**
- Creating projects works (no 500 error)
- WebSocket connects to wss://kairui.lhwebs.com/events
- No 404 on /api/v1/user-storage endpoints

---

## Testing Your Fix

### 1. Test Project Creation

1. Go to https://kairui.lhwebs.com
2. Login with your credentials
3. Click "New Project"
4. Fill in project details
5. Choose Kanban or Scrum
6. Click "Create"
7. **Should succeed without 500 error**

### 2. Check Browser Console

1. Open browser DevTools (F12)
2. Go to Console tab
3. Refresh page
4. **Should NOT see:**
   - 500 errors on /api/v1/projects
   - 404 on /api/v1/user-storage/dont_ask_premise_newsletter

### 3. Check WebSocket Connection

1. In DevTools, go to Network tab
2. Filter by "WS" (WebSocket)
3. Look for connection to `events`
4. **Should show:** Connected (101 Switching Protocols)

---

## Troubleshooting

### If "User taiga already exists" Error

This means the user was created with wrong password. Delete and recreate:

```bash
# Delete old user
docker exec project-taiga-events-rabbitmq-1 rabbitmqctl delete_user taiga
docker exec project-taiga-async-rabbitmq-1 rabbitmqctl delete_user taiga

# Then run fix script again
bash fix-rabbitmq-vhost.sh
```

### If Services Won't Start

Check logs for specific errors:

```bash
docker logs project-taiga-back-1 --tail 100
docker logs project-taiga-events-1 --tail 100
docker logs project-taiga-events-rabbitmq-1 --tail 50
docker logs project-taiga-async-rabbitmq-1 --tail 50
```

### If Migration Fails

Ensure backend container is running:

```bash
docker ps | grep taiga-back
docker logs project-taiga-back-1 --tail 50
```

Then try migration again:

```bash
bash taiga-manage.sh migrate
```

### If Still Getting 500 Errors

1. Check all containers are running:
   ```bash
   docker compose ps
   ```

2. Restart all services:
   ```bash
   docker compose restart
   ```

3. Wait 30 seconds, then try again

4. If still failing, try complete reset:
   ```bash
   bash reset-rabbitmq.sh
   ```

---

## What Each Script Does

### `fix-rabbitmq-vhost.sh`
- Creates RabbitMQ user 'taiga' with password from .env
- Creates vhost 'taiga'
- Sets permissions
- Restarts affected services
- **Use when:** User/vhost are missing

### `reset-rabbitmq.sh`
- Completely removes RabbitMQ data volumes
- Reinitializes RabbitMQ from scratch
- Uses credentials from .env automatically
- **Use when:** Clean slate is desired or manual fix failed

### `fix-user-storage.sh`
- Runs Django database migrations
- Creates user-storage tables
- **Use when:** Getting 404 on user-storage API

### `verify-fix.sh`
- Checks all aspects of the fix
- Shows users, vhosts, permissions
- Reviews logs for errors
- **Use when:** Want to verify fix worked

---

## Files Modified

### `.env`
Updated with secure credentials:
- `SECRET_KEY`: kairui-2025-XyZ9pQm7nB4vL8hK3wF6jR1cA5sD0eG2tN4uP
- `POSTGRES_PASSWORD`: A52290120a
- `RABBITMQ_PASS`: A52290120a
- `RABBITMQ_ERLANG_COOKIE`: kairui2025erlangcookieXyZ9pQm7

---

## Expected Timeline

**Path 1 (Reset):** 3-5 minutes
**Path 2 (Manual Fix):** 5-10 minutes
**Path 3 (Step-by-Step):** 10-15 minutes

After completion, your Taiga instance should be fully functional with:
- Working project creation
- Functional WebSocket events
- No API errors
- Complete user-storage functionality

---

## Summary

**Recommended action:**

```bash
cd /www/kairuiads/project
bash reset-rabbitmq.sh
bash fix-user-storage.sh
bash verify-fix.sh
```

Then test creating a project at https://kairui.lhwebs.com

**That's it!**
