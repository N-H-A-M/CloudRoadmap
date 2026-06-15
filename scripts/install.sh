scripts/install.sh
#!/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "========================================="
echo " Telegram Bot Kubernetes Installer"
echo "========================================="
echo -e "${NC}"

# ------------------------------------
# Check Dependencies
# ------------------------------------

for cmd in docker kubectl minikube; do
    if ! command -v $cmd &> /dev/null
    then
        echo -e "${RED}$cmd is not installed${NC}"
        exit 1
    fi
done

echo -e "${GREEN}All dependencies found${NC}"

# ------------------------------------
# Start Minikube
# ------------------------------------

if ! minikube status | grep -q "Running"; then
    echo -e "${YELLOW}Starting Minikube...${NC}"
    minikube start
else
    echo -e "${GREEN}Minikube already running${NC}"
fi

# ------------------------------------
# Enable Minikube Storage
# ------------------------------------

minikube addons enable storage-provisioner
minikube addons enable default-storageclass

# ------------------------------------
# Show Context
# ------------------------------------

echo
echo -e "${BLUE}Current Context${NC}"
kubectl config current-context

kubectl get nodes

# ------------------------------------
# DockerHub Login
# ------------------------------------

echo
echo -e "${BLUE}DockerHub Configuration${NC}"

read -p "DockerHub Username: " DOCKER_USER
read -sp "DockerHub Password: " DOCKER_PASS
echo

echo "$DOCKER_PASS" | docker login \
    -u "$DOCKER_USER" \
    --password-stdin

if [ $? -ne 0 ]; then
    echo -e "${RED}Docker login failed${NC}"
    exit 1
fi

# ------------------------------------
# Create Namespaces
# ------------------------------------

echo
echo -e "${YELLOW}Creating Namespaces...${NC}"

kubectl apply -f k8s/namespaces.yaml

# ------------------------------------
# Create Secrets
# ------------------------------------

echo
echo -e "${BLUE}Creating Kubernetes Secrets${NC}"

read -sp "Telegram Bot Token: " BOT_TOKEN
echo

read -p "Postgres User: " POSTGRES_USER
read -sp "Postgres Password: " POSTGRES_PASSWORD
echo

kubectl create secret generic postgres-secret \
    --from-literal=POSTGRES_DB=telegramdb \
    --from-literal=POSTGRES_USER="$POSTGRES_USER" \
    --from-literal=POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
    -n database \
    --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic postgres-secret \
    --from-literal=POSTGRES_USER="$POSTGRES_USER" \
    --from-literal=POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
    -n telegram \
    --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic telegram-secret \
    --from-literal=BOT_TOKEN="$BOT_TOKEN" \
    -n telegram \
    --dry-run=client -o yaml | kubectl apply -f -

# Verify Secrets

kubectl get secret postgres-secret -n database
kubectl get secret postgres-secret -n telegram
kubectl get secret telegram-secret -n telegram

echo -e "${GREEN}Secrets Created${NC}"

# ------------------------------------
# Build Docker Image
# ------------------------------------

echo
echo -e "${YELLOW}Building Docker Image...${NC}"

docker build -t telegram-bot .

if [ $? -ne 0 ]; then
    echo -e "${RED}Docker build failed${NC}"
    exit 1
fi

# ------------------------------------
# Tag Docker Image
# ------------------------------------

echo
echo -e "${YELLOW}Tagging Docker Image...${NC}"

docker tag telegram-bot \
    $DOCKER_USER/telegram-bot:latest

# ------------------------------------
# Push Docker Image
# ------------------------------------

echo
echo -e "${YELLOW}Pushing Docker Image...${NC}"

docker push \
    $DOCKER_USER/telegram-bot:latest

if [ $? -ne 0 ]; then
    echo -e "${RED}Docker push failed${NC}"
    exit 1
fi

# ------------------------------------
# Update Deployment Image
# ------------------------------------

sed -i "s|image: .*|image: $DOCKER_USER/telegram-bot:latest|g" \
k8s/telegram/deployment.yaml

# ------------------------------------
# Deploy RBAC
# ------------------------------------

kubectl apply -f k8s/telegram/serviceaccount.yaml
kubectl apply -f k8s/telegram/role.yaml
kubectl apply -f k8s/telegram/rolebinding.yaml

# ------------------------------------
# Deploy PostgreSQL
# ------------------------------------

echo
echo -e "${YELLOW}Deploying PostgreSQL...${NC}"

kubectl apply -f k8s/postgres/postgres-pv.yaml
kubectl apply -f k8s/postgres/postgres-pvc.yaml
kubectl apply -f k8s/postgres/postgres-deployment.yaml
kubectl apply -f k8s/postgres/postgres-service.yaml

kubectl rollout status deployment/postgres -n database

# ------------------------------------
# Deploy Telegram Bot
# ------------------------------------

echo
echo -e "${YELLOW}Deploying Telegram Bot...${NC}"

kubectl apply -f k8s/telegram/deployment.yaml

kubectl rollout status deployment/telegram-bot -n telegram

# ------------------------------------
# Status
# ------------------------------------

echo
echo -e "${GREEN}"
echo "========================================="
echo " Installation Completed Successfully"
echo "========================================="
echo -e "${NC}"

kubectl get pods -A

echo
kubectl get pvc -A

echo
kubectl get svc -A