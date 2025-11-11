```markdown
# 🚀 Debugging & Monitoring Tool  
A powerful, lightweight, and intelligent monitoring dashboard built using **Flask (Backend)** and **HTML/CSS/JavaScript (Frontend)**.  
This tool centralizes application logs, system metrics, alerts, and AI-based debugging suggestions.

---

## ✅ Features
### 🔍 **1. Real-Time Log Monitoring**
- Displays logs with severity levels: **INFO, WARNING, ERROR, CRITICAL**
- Filter logs by **severity**, **service**, and **timestamp**
- Search logs instantly

### ⚠️ **2. Smart Alerting System**
- Triggers alerts for:
  - High CPU usage  
  - High memory usage  
  - Disk usage issues  
  - Error / Critical logs  
- Alerts stored in JSON & shown on dashboard  
- Auto-Fix Feature ✅

### 🤖 **3. AI-Based Debugging (Simple ML Module)**
- Gives possible root causes  
- Suggests solutions based on log patterns  
- Helps faculty see AI integration

### 📊 **4. Dashboard UI**
- Clean, modern UI  
- Shows:
  - Total logs  
  - Error & critical logs  
  - Logs by severity  
  - Active alerts  
  - System stats

### 🗂️ **5. Manual Database (JSON–Based)**
Fully manual — **no PostgreSQL / no Neon DB** required.  
Stored inside:
- `backend/data/logs.json`
- `backend/data/alerts.json`
- `backend/data/system_stats.json`

---

## 🏗️ Project Folder Structure

```

Debugging-and-Monitoring-Tool/
│
├── backend/
│   ├── app.py                # Main Flask API
│   ├── ai_module.py          # AI Debugging Logic
│   ├── alerts.py             # Alert handler
│   ├── database.py           # JSON database manager
│   ├── predictive.py         # (Optional) Predictive analytics module
│   ├── system_monitor.py     # CPU/MEM/DISK status
│   ├── data/
│   │   ├── logs.json
│   │   ├── alerts.json
│   │   └── system_stats.json
│   ├── logs/
│   │   └── sample_logs.json
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── main.js
│
├── README.md
└── .gitignore

```

---

## ✅ Installation & Setup

### **1️⃣ Clone the repository**
```

git clone [https://github.com/rahulpandey7218/Debugging-and-Monitoring-Tool.git](https://github.com/rahulpandey7218/Debugging-and-Monitoring-Tool.git)
cd Debugging-and-Monitoring-Tool

```

### **2️⃣ Create & Activate Virtual Environment**
```

python -m venv venv
venv\Scripts\activate  (Windows)

```

### **3️⃣ Install dependencies**
```

pip install -r backend/requirements.txt

```

### **4️⃣ Run Backend**
```

python backend/app.py

```

Backend runs on:  
👉 http://127.0.0.1:5001/

### **5️⃣ Open Frontend**
Open this file directly in browser:
```

frontend/index.html

```

---

## ✅ API Endpoints (Important for Viva)

### 🔹 Get Logs  
```

GET /api/logs

```

### 🔹 Add Log  
```

POST /api/add-log

```

### 🔹 Get Alerts  
```

GET /api/alerts

```

### 🔹 Mark Alert Read  
```

POST /api/alerts/<id>/mark-read

```

### 🔹 Auto-Fix Alerts  
```

POST /api/alerts/<id>/auto-fix
POST /api/alerts/auto-fix-all

```

---

## 📸 Screenshots  
(Add your screenshots here after running the project)

```

![](screenshots/dashboard.png)
![](screenshots/alerts.png)
![](screenshots/logs.png)

```

---

## ✅ Technologies Used
- **Python + Flask**
- **HTML + CSS + JavaScript**
- **JSON for manual storage**
- **psutil** (system monitoring)
- **Basic ML module** for AI debugging

---

## ✅ Future Enhancements
✔ Add PostgreSQL / Neon DB  
✔ Add user authentication  
✔ Add WebSocket-based real-time updates  
✔ Mobile-responsive UI  

---

## ⭐ Contribute  
Pull requests are welcome!

---

## 📬 Contact  
**Developer:** Rahul Pandey  
GitHub: https://github.com/rahulpandey7218  
Project Repo: Debugging-and-Monitoring-Tool  

