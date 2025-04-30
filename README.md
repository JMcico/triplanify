# Triplanify

**Triplanify** is a backend service project built with FastAPI, designed to integrate with Azure Agent for thread and message handling.

---

## 📋 Requirements

- **Python Version**: `3.12`
- **Package Management**: `pip` (It is recommended to use a virtual environment.)

---

## 🚀 Quick Start

1. **Clone the Repository**

```bash
git clone https://github.com/jmcico/triplanify.git
cd triplanify
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Install Azure CLI and get authentification**
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Get authentification
azd login
```

4. **Deploy and Run the Backend Service**

Start the Uvicorn server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- The service will be available at: `http://127.0.0.1:8000`
- Access API documentation:
  - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
  - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📚 Additional Notes

- Currently, the project includes two primary endpoints: `/api/thread` and `/api/message`.

---

## 🛠️ Development and Contribution

If you wish to contribute, please ensure that your code follows the project’s style guidelines and is properly tested before submitting a pull request.

---
