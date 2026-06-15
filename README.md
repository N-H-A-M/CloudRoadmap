# 🚀 Telegram Productivity Bot on Kubernetes

## 📖 Overview

This project deploys a Python Telegram Productivity Bot on a Kubernetes cluster using Minikube.

The bot supports:

* 📝 Notes
* ✅ Tasks
* ⏰ Reminders
* 📊 Statistics
* ☀️ Morning Briefings
* 🤖 Smart Commands (without `/`)

The application is containerized with Docker and deployed to Kubernetes with persistent PostgreSQL storage.

---

# 🏗 Architecture

```text
Telegram
    |
    v
Telegram Bot (Python)
    |
    v
PostgreSQL
    |
    v
Kubernetes (Minikube)
```

Namespaces:

```text
telegram
database
```

---

# 🛠 Technologies

* Python 3.13
* python-telegram-bot
* PostgreSQL
* Docker
* Kubernetes
* Minikube
* Persistent Volumes
* Persistent Volume Claims
* Kubernetes Secrets

---

# 👥 Team Requirements

Each developer should install:

### Required Software

* Git
* Docker Desktop
* Minikube
* kubectl
* Python 3.13+
* VS Code or IntelliJ

### Verify Installation

```bash
git --version

docker --version

kubectl version --client

minikube version

python --version
```

---

# 📂 Project Structure

```text
telegram-bot/
│
├── src/
│   └── bot.py
│
├── k8s/
│   ├── namespaces.yaml
│   │
│   ├── postgres/
│   │   ├── postgres-secret.yaml
│   │   ├── postgres-pv.yaml
│   │   ├── postgres-pvc.yaml
│   │   ├── postgres-deployment.yaml
│   │   └── postgres-service.yaml
│   │
│   └── telegram/
│       ├── telegram-secret.yaml
│       └── deployment.yaml
│
├── scripts/
│   ├── install.sh
│   ├── uninstall.sh
│   ├── status.sh
│   └── logs.sh
│
├── Dockerfile
├── requirements.txt
├── .gitignore
└── README.md
```

---

# 🔐 Telegram Bot Token

Create a bot using BotFather.

Create a local `.env` file:

```env
BOT_TOKEN=YOUR_TOKEN
```

Do NOT commit `.env` to GitHub.

Add to `.gitignore`:

```text
.env
```

---

# 🐳 Build Docker Image

```bash
docker build -t telegram-bot .
```

Run locally:

```bash
docker run --env-file .env telegram-bot
```

---

# ☸️ Start Minikube

```bash
minikube start
```

Verify:

```bash
kubectl get nodes
```

Expected:

```text
Ready
```

---

# 🚀 Installation

Run:

```bash
chmod +x scripts/install.sh

./scripts/install.sh
```

The installer will:

1. Create namespaces
2. Create secrets
3. Create PV
4. Create PVC
5. Deploy PostgreSQL
6. Create PostgreSQL service
7. Deploy Telegram Bot
8. Verify deployment

---

# 🔎 Verification

Check namespaces:

```bash
kubectl get ns
```

Check pods:

```bash
kubectl get pods -A
```

Expected:

```text
telegram-bot      Running
postgres          Running
```

Check PVC:

```bash
kubectl get pvc -A
```

Expected:

```text
Bound
```

---

# 📜 Logs

Telegram Bot:

```bash
kubectl logs deployment/telegram-bot -n telegram -f
```

PostgreSQL:

```bash
kubectl logs deployment/postgres -n database -f
```

---

# 🧪 Testing

Send messages to the bot:

```text
help

task Learn Kubernetes

show tasks

note Learn Helm

show notes

stats

morning
```

Expected:

```text
Task added
Note saved
Statistics displayed
```

---

# 🗑 Uninstall

```bash
./scripts/uninstall.sh
```

---

# 🔮 Future Improvements

* Helm Charts
* ArgoCD
* GitHub Actions
* PostgreSQL Backups
* Prometheus
* Grafana
* OpenAI Integration
* Webhooks instead of Polling
* Multi-user support
* Task Priorities
* Recurring Reminders

---

# 👨‍💻 Contributors

* Ron Nirzaaev
* Project Partner

DevOps Portfolio Project
