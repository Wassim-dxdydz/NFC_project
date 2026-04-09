# NFC Inventory Management System

A Python application designed to track and manage product stock using NFC tags. This project provides a bridge between physical NFC hardware and a local SQLite database, allowing for real-time inventory updates.

---

## 📋 Features

- **Automated Scanning**: Detects NFC tags and retrieves their Unique ID (UID).
- **Product Registration**: Register new items with descriptions, dates, and quantities.
- **Stock Control**: Quick "Update" (remove) or "Restock" (add) functions via terminal.
- **Data Persistence**: Uses a local SQLite database to store all product history.
- **Visual Feedback**: Cleanly formatted console output for product details and stock status.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following:

1. **Python 3.10+**  
   👉 https://www.python.org/downloads/

2. **NFC Reader**  
   A PC/SC compatible reader (e.g., ACR122U)

3. **System Drivers (Linux/Debian)**  
   Required for the `pyscard` library to communicate with the USB reader:

```bash
sudo apt-get update
sudo apt-get install libpcsclite-dev pcscd
sudo systemctl enable --now pcscd
```

---

## 🚀 Installation Step-by-Step

### 1. Clone the Project

```bash
git clone https://github.com/Wassim-dxdydz/NFC_project.git
cd NFC_project
```

---

### 2. Create a Virtual Environment

It is highly recommended to use an environment to avoid library conflicts:

```bash
# Create the environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

---

### 3. Install Dependencies

Ensure you have a `requirements.txt` file in your directory containing `pyscard`. Then run:

```bash
pip install -r requirements.txt
```

---

### 4. Database Setup

The database is initialized automatically the first time you run the script.  
No manual SQL execution is required.

---

## 📖 Usage Instructions

### ▶️ Running the App

Make sure your environment is activated and your NFC reader is plugged in, then run:

```bash
python main.py
```

---

### 🔄 Operational Workflow

#### 1. Detection
- The app will wait for 30 seconds.
- Place your NFC tag on the reader.

#### 2. Registration (New Tag)
If the tag is unknown, the terminal will prompt you to enter:
- Product Name & Description
- Production & Expiration dates (Format: `YYYY-MM-DD`)
- Initial Quantity

#### 3. Stock Management (Existing Tag)
If the tag is already in the database:
- Press `u` → Update/Remove quantity (e.g., selling an item)
- Press `r` → Restock/Add quantity
- Press `Enter` → View product details and exit

---

## 📂 Project Structure

```
nfc_project/
│
├── main.py                  # Entry point (app loop + scanning timeout)
├── database.py              # Product dataclass + SQLite CRUD operations
├── nfc_reader_writer.py     # NFC hardware communication + logic
├── requirements.txt         # Project dependencies
└── .gitignore               # Ignored files (venv, DB, cache)
```

---

## ⚙️ Requirements

Your `requirements.txt` file should contain:

```
pyscard
```

---

## 🛡️ Security & Privacy Notes

- The `.gitignore` file ensures that:
  - `nfc_products.db` (local database)
  - `venv/` (virtual environment)
  - `__pycache__/` (Python cache)

are **not uploaded** to your repository.

This keeps your inventory data private and your repository clean.

---

## ✅ Summary

This project enables:
- Seamless interaction between NFC hardware and software
- Real-time inventory tracking
- Simple and efficient stock management via terminal

---

🚀 Happy building!