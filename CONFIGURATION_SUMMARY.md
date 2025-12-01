# Taiga Configuration Update Summary

## Date: 2025-12-01

---

## Changes Made

### 1. Environment Configuration (.env)

Updated the following critical configuration values:

| Variable | Old Value | New Value |
|----------|-----------|-----------|
| `SECRET_KEY` | `taiga-prod-secret-key-change-this-to-random-50-chars` | `kairui-2025-XyZ9pQm7nB4vL8hK3wF6jR1cA5sD0eG2tN4uP` |
| `POSTGRES_PASSWORD` | `taiga-strong-password-change-this` | `A52290120a` |
| `RABBITMQ_PASS` | `rabbitmq-strong-password-change-this` | `A52290120a` |
| `RABBITMQ_ERLANG_COOKIE` | `unique-erlang-cookie-change-this-to-random-value` | `kairui2025erlangcookieXyZ9pQm7` |

**Unchanged (already correct):**
- `TAIGA_DOMAIN`: `kairui.lhwebs.com`
- `TAIGA_SCHEME`: `https`
- `WEBSOCKETS_SCHEME`: `wss`
- `AUTO_ASSIGN_ADMIN_USERNAME`: `adsadmin`
- `AUTO_ASSIGN_ADMIN_EMAIL`: `lhweave@gmail.com`

---

## Problem Identified

**Root Cause:** RabbitMQ vhost "taiga" was not created during container initialization.

**Error Message:**
```
amqp.exceptions.NotAllowed: Connection.open: (530) NOT_ALLOWED - vhost taiga not found
```

**Impact:**
- Creating projects (Kanban or Scrum) returned 500 Internal Server Error
- WebSocket connection to `wss://kairui.lhwebs.com/events` failed
- Real-time events were not working

---

## Solution Provided

### Files Created:

1. **`fix-rabbitmq-vhost.sh`** - Automated fix script
   - Creates missing 'taiga' vhost in both RabbitMQ containers
   - Sets proper permissions
   - Restarts affected services

2. **`verify-fix.sh`** - Verification script
   - Checks container status
   - Verifies vhost creation
   - Reviews logs for errors

3. **`FIX_INSTRUCTIONS.md`** - Detailed manual instructions
   - Step-by-step fix procedures
   - Multiple options (quick fix, manual, complete reset)
   - Verification steps
   - Troubleshooting guide

---

## Next Steps for Server Administrator

### On Your Server (`/www/kairuiads/project`):

**Step 1: Apply the fix**
```bash
cd /www/kairuiads/project
bash fix-rabbitmq-vhost.sh
```

**Step 2: Wait for services to restart** (10-20 seconds)

**Step 3: Verify the fix**
```bash
bash verify-fix.sh
```

**Step 4: Test in browser**
- Go to https://kairui.lhwebs.com
- Login and try creating a new project
- Should work without 500 error

---

## Expected Results After Fix

✅ Projects can be created successfully (Kanban & Scrum)
✅ WebSocket connection works (`wss://kairui.lhwebs.com/events`)
✅ Real-time events function properly
✅ No "vhost taiga not found" errors in logs
✅ All containers running with "Up" status

---

## Credentials Summary

**Database:**
- User: `taiga`
- Password: `A52290120a`

**RabbitMQ:**
- User: `taiga`
- Password: `A52290120a`
- Vhost: `taiga`

**Admin User:**
- Username: `adsadmin`
- Email: `lhweave@gmail.com`
- Password: `A52290120a`

---

## Important Notes

1. **Password Security**: The password `A52290120a` is now set for all services. Ensure this is kept secure.

2. **Database Data**: The quick fix (Option A) preserves existing data. If you want a fresh start, use Option C in `FIX_INSTRUCTIONS.md`.

3. **Backup Recommendation**: Before making any changes, consider backing up:
   ```bash
   docker exec project-taiga-db-1 pg_dump -U taiga taiga > taiga_backup_$(date +%Y%m%d).sql
   ```

4. **Service Dependencies**: The fix requires Docker Compose to be available on the server.

---

## Troubleshooting

If the fix doesn't work:

1. **Check logs:**
   ```bash
   docker logs project-taiga-back-1 --tail 100
   docker logs project-taiga-events-rabbitmq-1 --tail 100
   ```

2. **Verify containers are running:**
   ```bash
   docker compose ps
   ```

3. **Check if config was applied:**
   ```bash
   grep RABBITMQ_PASS .env
   ```

4. **Try manual fix** as described in `FIX_INSTRUCTIONS.md`

---

## Support

For detailed instructions, refer to:
- `FIX_INSTRUCTIONS.md` - Complete fix guide
- Original error logs - Provided by user
- Taiga documentation - https://docs.taiga.io/

---

**Configuration updated by:** Claude Code
**Date:** 2025-12-01
**Project:** Taiga Docker Deployment for kairui.lhwebs.com
