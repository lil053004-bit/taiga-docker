# Taiga Docker Setup

A production-ready Taiga installation with Docker Compose, featuring automatic initialization and Chinese language support.

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Domain with HTTPS configured (or modify for HTTP in `.env`)

### Installation

1. **Clone and Configure**

```bash
git clone <repository-url>
cd project
```

2. **Update Configuration**

Edit `.env` and set your domain:

```bash
TAIGA_DOMAIN=your-domain.com
```

3. **Launch Taiga**

```bash
bash launch-taiga.sh
```

Wait 60 seconds for initialization to complete.

4. **Access Taiga**

- **Main Interface**: `https://your-domain.com`
- **Admin Panel**: `https://your-domain.com/admin/`

**Default Credentials:**
- Username: `adsadmin`
- Password: `A52290120a`

**⚠️ Change the default password after first login!**

---

## Features

- **Automatic Initialization** - Superuser created on first launch
- **Chinese Language** - Default interface in Chinese
- **Auto-Assignment** - New items automatically assigned to admin
- **Custom Fields Display** - Custom fields visible on Kanban cards
- **HTTPS Ready** - Pre-configured for secure connections
- **RabbitMQ Configured** - Events and async tasks work immediately

---

## Configuration

### Environment Variables

Edit `.env` to configure:

```bash
# Domain Configuration
TAIGA_DOMAIN=your-domain.com
TAIGA_SCHEME=https

# Database
POSTGRES_USER=taiga
POSTGRES_PASSWORD=A52290120a

# RabbitMQ
RABBITMQ_USER=taiga
RABBITMQ_PASS=A52290120a
RABBITMQ_VHOST=taiga

# Admin User (auto-created)
AUTO_ASSIGN_ADMIN_USERNAME=adsadmin
AUTO_ASSIGN_ADMIN_EMAIL=your-email@example.com
```

### Nginx/Reverse Proxy

If using nginx as reverse proxy, configure it to forward to port 9090:

```nginx
location / {
    proxy_pass http://localhost:9090;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /events {
    proxy_pass http://localhost:9090/events;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}
```

---

## Management Commands

### View Logs

```bash
docker compose logs -f
```

### Check Service Status

```bash
docker compose ps
```

### Restart Services

```bash
docker compose restart
```

### Stop Services

```bash
docker compose down
```

### Database Backup

```bash
docker exec project-taiga-db-1 pg_dump -U taiga taiga > backup.sql
```

### Run Django Management Commands

```bash
bash taiga-manage.sh <command>

# Examples:
bash taiga-manage.sh migrate
bash taiga-manage.sh createsuperuser
bash taiga-manage.sh shell
```

---

## Custom Features

### Auto-Assignment

New user stories, tasks, and issues are automatically assigned to the admin user. Configure in `.env`:

```bash
AUTO_ASSIGN_ENABLED=True
AUTO_ASSIGN_ADMIN_USERNAME=adsadmin
```

### Custom Fields Display

Custom fields are automatically displayed on:
- Kanban cards
- Backlog items
- Task lists

Configure in `taiga-front/custom-fields.js`.

### Chinese Language

All users are set to Chinese (zh-Hans) by default. The system includes:
- Chinese interface translations
- Custom field labels in Chinese
- Chinese date formats

---

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker compose logs --tail 100

# Restart all services
docker compose down
bash launch-taiga.sh
```

### Can't Login to Admin Panel

The superuser is created automatically on first launch. If login fails:

```bash
# Recreate superuser
docker compose exec taiga-back python manage.py initialize_taiga

# Check user exists
docker compose exec taiga-back python manage.py shell -c \
  "from django.contrib.auth import get_user_model; \
   User = get_user_model(); \
   print(User.objects.filter(username='adsadmin').exists())"
```

### RabbitMQ Connection Errors

If you see RabbitMQ connection errors:

```bash
# Stop and remove volumes
docker compose down
docker volume rm project_taiga-events-rabbitmq-data
docker volume rm project_taiga-async-rabbitmq-data

# Restart
bash launch-taiga.sh
```

### Database Connection Issues

```bash
# Check database is running
docker compose ps taiga-db

# Check database logs
docker compose logs taiga-db --tail 50
```

### Port Already in Use

If port 9090 is already in use, edit `docker-compose.yml`:

```yaml
taiga-gateway:
  ports:
    - "8080:8080"  # Change 9090 to any available port
```

---

## Architecture

### Services

- **taiga-db** - PostgreSQL database
- **taiga-back** - Django backend API
- **taiga-async** - Celery async task worker
- **taiga-front** - Angular frontend
- **taiga-events** - WebSocket events server
- **taiga-gateway** - Nginx reverse proxy
- **taiga-protected** - Protected attachments server
- **taiga-events-rabbitmq** - RabbitMQ for events
- **taiga-async-rabbitmq** - RabbitMQ for async tasks

### Volumes

- **taiga-db-data** - Database files
- **taiga-static-data** - Static assets
- **taiga-media-data** - User uploads
- **taiga-events-rabbitmq-data** - Events queue
- **taiga-async-rabbitmq-data** - Async queue

### Custom Integration

The `taiga-custom` directory contains Django customizations:
- Auto-assignment signals
- Custom field serializers
- Management commands
- Admin interface extensions

---

## Updating

### Update Docker Images

```bash
docker compose pull
docker compose down
docker compose up -d
```

### Backup Before Updating

```bash
# Backup database
docker exec project-taiga-db-1 pg_dump -U taiga taiga > backup_$(date +%Y%m%d).sql

# Backup media files
docker cp project-taiga-back-1:/taiga-back/media ./media_backup
```

---

## Security

### Change Default Credentials

After first login, immediately change the default password:

1. Go to `https://your-domain.com/admin/`
2. Login with `adsadmin` / `A52290120a`
3. Click your username in top right
4. Select "Change password"

### Update Secret Key

Generate a new secret key and update `.env`:

```bash
SECRET_KEY="your-new-random-secret-key-here"
```

Then restart services:

```bash
docker compose restart taiga-back taiga-async
```

### HTTPS Configuration

Ensure your reverse proxy (nginx/Caddy) terminates SSL and sets:
- `X-Forwarded-Proto: https`
- `X-Forwarded-For` header
- `Host` header

---

## Support

### Documentation

- [Official Taiga Documentation](https://docs.taiga.io/)
- [Docker Setup Guide](https://github.com/taigaio/taiga-docker)

### Getting Help

- Check logs: `docker compose logs -f`
- Review `.env` configuration
- Ensure all services are running: `docker compose ps`

---

## License

This setup includes:
- Taiga: MPL-2.0 License
- Custom extensions: See `LICENSE` file

---

## Maintenance

### Weekly

- Check logs for errors: `docker compose logs --tail 100`
- Verify all services running: `docker compose ps`

### Monthly

- Backup database
- Update Docker images
- Clear old sessions: `bash taiga-manage.sh clearsessions`

### As Needed

- Monitor disk space (Docker volumes)
- Review and rotate logs
- Update custom extensions

---

**Enjoy using Taiga! 🎉**

For questions or issues, check the logs first: `docker compose logs -f`
