#!/bin/bash
echo "===================================="
echo "Hochzeitsanzug Landing Page Deployment"
echo "===================================="
echo ""

# Farben
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Variablen
APP_DIR="/var/www/hochzeitsanzug"
REPO_URL="https://github.com/Henninglutz/hochzeitsanzug.bettercallhenk.de.git"
BRANCH="main"
APP_PORT="${APP_PORT:-8001}"
FORCE_SYNC_WITH_REMOTE="${FORCE_SYNC_WITH_REMOTE:-true}"

echo -e "${YELLOW}[1/6]${NC} Erstelle Verzeichnis..."
mkdir -p "$APP_DIR"
cd "$APP_DIR"

echo -e "${YELLOW}[2/6]${NC} Clone/Update Repository..."
if [ -d "$APP_DIR/.git" ]; then
    echo "Repository existiert bereits, aktualisiere..."
    git fetch origin
    git checkout "$BRANCH" 2>/dev/null || git checkout master 2>/dev/null || {
        echo -e "${RED}Weder 'main' noch 'master' Branch gefunden!${NC}"
        exit 1
    }

    if [ "$FORCE_SYNC_WITH_REMOTE" = "true" ]; then
        echo "Synchronisiere Branch hart mit origin/$BRANCH (lokale Commits werden verworfen)..."
        git reset --hard "origin/$BRANCH" || {
            echo -e "${RED}Konnte nicht auf origin/$BRANCH zurücksetzen!${NC}"
            exit 1
        }
    else
        git pull --ff-only origin "$BRANCH" || {
            echo -e "${RED}Fast-forward Pull fehlgeschlagen (Branch divergiert).${NC}"
            echo "  Tipp: FORCE_SYNC_WITH_REMOTE=true setzen oder manuell mergen/rebasen."
            exit 1
        }
    fi
else
    git clone -b $BRANCH "$REPO_URL" "$APP_DIR" 2>/dev/null || \
    git clone -b master "$REPO_URL" "$APP_DIR" || {
        echo -e "${RED}Repository konnte nicht geklont werden!${NC}"
        exit 1
    }
fi
echo -e "${GREEN}✓${NC} Repository geklont/aktualisiert"

echo -e "${YELLOW}[3/6]${NC} Prüfe Umgebungsvariablen..."
ENV_FILE="/root/.env"
if [ -f "$ENV_FILE" ]; then
    # Prüfe ob Pipedrive-Variablen vorhanden sind
    if grep -q "PIPEDRIVE_API_TOKEN" "$ENV_FILE"; then
        echo -e "${GREEN}✓${NC} PIPEDRIVE_API_TOKEN gefunden"
    else
        echo -e "${RED}WARNUNG:${NC} PIPEDRIVE_API_TOKEN fehlt in $ENV_FILE"
        echo "  Bitte hinzufügen: PIPEDRIVE_API_TOKEN=dein-token"
    fi
    if grep -q "PIPEDRIVE_COMPANY_DOMAIN" "$ENV_FILE"; then
        echo -e "${GREEN}✓${NC} PIPEDRIVE_COMPANY_DOMAIN gefunden"
    else
        echo -e "${RED}WARNUNG:${NC} PIPEDRIVE_COMPANY_DOMAIN fehlt in $ENV_FILE"
        echo "  Bitte hinzufügen: PIPEDRIVE_COMPANY_DOMAIN=bettercallhenk"
    fi
else
    echo -e "${RED}WARNUNG:${NC} $ENV_FILE nicht gefunden!"
    echo "  Erstelle die Datei mit den notwendigen Variablen."
fi

echo -e "${YELLOW}[4/6]${NC} Docker Container bauen und starten..."

# Prüfe ob Docker installiert ist
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker ist nicht installiert!${NC}"
    echo "Installiere Docker: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# Stoppe alten Container falls vorhanden
docker compose down 2>/dev/null || docker-compose down 2>/dev/null

# Baue und starte neu
APP_PORT="$APP_PORT" docker compose up -d --build 2>/dev/null || APP_PORT="$APP_PORT" docker-compose up -d --build || {
    echo -e "${RED}Docker Build fehlgeschlagen!${NC}"
    exit 1
}

# Warte auf Health Check
echo "Warte auf App-Start..."
for i in {1..15}; do
    if curl -sf "http://localhost:${APP_PORT}/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} App läuft auf Port ${APP_PORT}"
        break
    fi
    if [ $i -eq 15 ]; then
        echo -e "${RED}App antwortet nicht nach 15 Sekunden!${NC}"
        echo "Logs: docker compose logs"
        exit 1
    fi
    sleep 1
done

echo -e "${YELLOW}[5/6]${NC} Konfiguriere Nginx als Reverse Proxy..."
NGINX_CONF="/etc/nginx/conf.d/hochzeitsanzug.bettercallhenk.de.conf"

cat > "$NGINX_CONF" <<'NGINXEOF'
# Hochzeitsanzug Landing Page - Nginx Reverse Proxy to Flask/Gunicorn

server {
    listen 80;
    server_name hochzeitsanzug.bettercallhenk.de;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name hochzeitsanzug.bettercallhenk.de;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/hochzeitsanzug.bettercallhenk.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/hochzeitsanzug.bettercallhenk.de/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Proxy to Flask/Gunicorn
    location / {
        proxy_pass http://127.0.0.1:__APP_PORT__;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 10s;
        proxy_read_timeout 30s;
    }

    # Cache static assets (served by Flask but cached by Nginx)
    location /static/ {
        proxy_pass http://127.0.0.1:__APP_PORT__/static/;
        proxy_set_header Host $host;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logs
    access_log /var/log/nginx/hochzeitsanzug-access.log;
    error_log /var/log/nginx/hochzeitsanzug-error.log;
}
NGINXEOF


# Setze App-Port in Nginx-Template
sed -i "s/__APP_PORT__/${APP_PORT}/g" "$NGINX_CONF"

# Test Nginx Config
nginx -t && nginx -s reload
echo -e "${GREEN}✓${NC} Nginx konfiguriert und neugeladen"

echo -e "${YELLOW}[6/6]${NC} Prüfe Deployment..."
echo ""

# Health Check
echo "Health Check:"
curl -s "http://localhost:${APP_PORT}/health"
echo ""

# HTTPS Check
echo "HTTPS Check:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" -I https://hochzeitsanzug.bettercallhenk.de || echo "Connection failed"

# API Check
echo "API Check:"
curl -s -o /dev/null -w "POST /api/contact: %{http_code}\n" -X POST "http://localhost:${APP_PORT}/api/contact" -H "Content-Type: application/json" -d '{}' || echo "API not reachable"

echo ""
echo "===================================="
echo -e "${GREEN}Deployment abgeschlossen!${NC}"
echo "===================================="
echo ""
echo "URL: https://hochzeitsanzug.bettercallhenk.de"
echo "Logs: docker compose -f $APP_DIR/docker-compose.yml logs -f"
echo "Hinweis: FORCE_SYNC_WITH_REMOTE=$FORCE_SYNC_WITH_REMOTE | APP_PORT=$APP_PORT"
echo ""
