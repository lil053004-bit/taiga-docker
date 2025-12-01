# Taiga RabbitMQ Fix Instructions

## Problem Summary

The error `vhost taiga not found` occurs because RabbitMQ containers were started but the vhost was not properly created during initialization.

## What Has Been Done

✓ Updated `.env` file with correct credentials:
- `SECRET_KEY`: Updated to secure 50-character key
- `POSTGRES_PASSWORD`: Changed to `A52290120a`
- `RABBITMQ_PASS`: Changed to `A52290120a`
- `RABBITMQ_ERLANG_COOKIE`: Updated to secure random value
- Domain configuration: Already correct (`kairui.lhwebs.com`)

## Fix Steps (Execute on Your Server)

### Option A: Quick Fix (Recommended - Preserves Existing Data)

Run the automated fix script:

```bash
cd /www/kairuiads/project
bash fix-rabbitmq-vhost.sh
```

This script will:
1. Check container status
2. Create the 'taiga' vhost in both RabbitMQ containers
3. Set proper permissions
4. Restart related services

**Wait 10-20 seconds after running, then test creating a project.**

---

### Option B: Manual Fix (If Script Fails)

Execute these commands one by one:

```bash
cd /www/kairuiads/project

# Step 1: Fix events RabbitMQ
docker exec project-taiga-events-rabbitmq-1 rabbitmqctl add_vhost taiga
docker exec project-taiga-events-rabbitmq-1 rabbitmqctl set_permissions -p taiga taiga ".*" ".*" ".*"

# Step 2: Fix async RabbitMQ
docker exec project-taiga-async-rabbitmq-1 rabbitmqctl add_vhost taiga
docker exec project-taiga-async-rabbitmq-1 rabbitmqctl set_permissions -p taiga taiga ".*" ".*" ".*"

# Step 3: Restart services
docker compose restart taiga-back taiga-events taiga-async

# Step 4: Verify vhosts exist
docker exec project-taiga-events-rabbitmq-1 rabbitmqctl list_vhosts
docker exec project-taiga-async-rabbitmq-1 rabbitmqctl list_vhosts
```

---

### Option C: Complete Reset (If You Want Fresh Start)

⚠️ **WARNING: This will delete ALL existing data!**

```bash
cd /www/kairuiads/project

# Stop all services
docker compose down

# Remove data volumes
docker volume rm project_taiga-db-data
docker volume rm project_taiga-events-rabbitmq-data
docker volume rm project_taiga-async-rabbitmq-data

# Start fresh
bash launch-taiga.sh

# Wait 30 seconds for initialization
sleep 30

# Create superuser
bash taiga-manage.sh createsuperuser
# Username: adsadmin
# Email: lhweave@gmail.com
# Password: A52290120a
```

---

## Verification Steps

After applying the fix:

### 1. Check Container Status
```bash
docker compose ps
```
All containers should be "Up" or "running".

### 2. Check RabbitMQ Vhosts
```bash
docker exec project-taiga-events-rabbitmq-1 rabbitmqctl list_vhosts
docker exec project-taiga-async-rabbitmq-1 rabbitmqctl list_vhosts
```
Both should show "taiga" vhost.

### 3. Check Backend Logs
```bash
docker logs project-taiga-back-1 --tail 50
```
Should NOT show "vhost taiga not found" errors.

### 4. Test in Browser
1. Go to https://kairui.lhwebs.com
2. Login with your user
3. Try creating a new project (Kanban or Scrum)
4. Should succeed without 500 error
5. Open browser DevTools (F12) → Network tab
6. Check WebSocket connection to `wss://kairui.lhwebs.com/events` - should be connected

---

## Why This Happened

The RabbitMQ containers have an environment variable `RABBITMQ_DEFAULT_VHOST=taiga` which should automatically create the vhost during first startup. However, if:

1. Containers were stopped/restarted before full initialization
2. Previous startup had configuration errors
3. Data volumes were in an inconsistent state

...then the vhost may not have been created, causing the 500 error when creating projects.

---

## After Fix Success

Once the fix is applied and working:

1. **WebSocket connection** will work properly
2. **Creating projects** (Kanban/Scrum) will succeed
3. **Real-time events** will function correctly
4. No more 500 errors related to RabbitMQ

---

## Need Help?

If you encounter any issues:

1. Check the logs:
   ```bash
   docker logs project-taiga-back-1 --tail 100
   docker logs project-taiga-events-1 --tail 100
   docker logs project-taiga-events-rabbitmq-1 --tail 100
   ```

2. Make sure all containers are running:
   ```bash
   docker compose ps
   ```

3. Verify the .env file was updated correctly:
   ```bash
   grep -E "(SECRET_KEY|POSTGRES_PASSWORD|RABBITMQ)" .env
   ```
