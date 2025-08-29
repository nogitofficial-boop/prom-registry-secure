# 🎉 IITD Prom Registry (Secure)

A tiny, secure web app to collect **Name**, **Instagram ID**, **Entry Number**, and **Gender** for prom matching.
Data is stored **encrypted at rest** in a local SQLite database; only you (with the admin token + passphrase) can export decrypted data.

## 🔐 Privacy & Security (at a glance)
- **Encryption at rest**: All submitted fields are encrypted using Fernet with a key **derived from your `SECRET_PASSPHRASE`**.
- **Private admin export**: Decrypted CSV is only available via a **Bearer token** (`ADMIN_TOKEN`).
- **No analytics / no logs of plaintext**.
- **CORS disabled** (not needed for this simple form).
- Optional **secure headers**.

---

## 🚀 Quick Start (Local)

### 1) Download & enter the folder
```bash
unzip prom-registry-secure.zip -d prom-registry-secure
cd prom-registry-secure
```

### 2) Create your secrets
Copy the example and edit:
```bash
cp .env.example .env
# open .env and set ADMIN_TOKEN and SECRET_PASSPHRASE to strong values
```

> **Tip**: Make tokens quickly:
> ```bash
> python - <<'PY'
> import secrets; print("ADMIN_TOKEN=", secrets.token_urlsafe(48))
> PY
> ```

### 3) Install & run
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000 --workers 1
```
Open: http://127.0.0.1:8000

### 4) Export decrypted CSV (admin only)
Use your `ADMIN_TOKEN` in the **Authorization** header:
```bash
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" http://127.0.0.1:8000/admin/export -o submissions.csv
```
Or open in the browser (it will prompt for the token):
http://127.0.0.1:8000/admin/export

You can also check the current count:
```bash
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" http://127.0.0.1:8000/admin/count
```

---

## 🐳 Run with Docker (recommended for deployment)

```bash
docker build -t prom-registry-secure .
docker run -p 8000:8000 --env-file .env prom-registry-secure
```
Open: http://127.0.0.1:8000

> On a server, run behind **HTTPS** (Caddy, Nginx, or a managed platform). Always keep `.env` private!

---

## 🌐 Deploy (Render / Railway / Fly.io / VPS)

- **Render** / **Railway**: Use a Python service or Docker; add environment variables `ADMIN_TOKEN` and `SECRET_PASSPHRASE`. Expose port 8000.
- **VPS (Ubuntu)**: Install Docker, copy repo, set `.env`, and run `docker run ...`. Put Nginx/Caddy in front for HTTPS.
- **Vercel** not ideal because it’s a long-running server with SQLite on disk.

**Important**: Keep your `.env` secret and never commit it. To back up data, copy the `data/` folder (it contains the encrypted `submissions.db`).

---

## 🔎 How data is stored
- SQLite file at `data/submissions.db`
- Table: `submissions(id, name_enc, instagram_enc, entry_enc, gender_enc, created_at)`
- All fields except `id` and `created_at` are **encrypted**.
- Export route decrypts **on the fly** using your `SECRET_PASSPHRASE`.

> Even if the DB file leaks, without your passphrase the data remains unreadable.

---

## 🧰 File Structure
```
.
├── app
│   ├── main.py            # FastAPI app
│   ├── db.py              # SQLite init + queries
│   ├── security.py        # Key derivation, encryption/decryption, admin auth
│   ├── templates
│   │   ├── index.html     # The form
│   │   └── success.html   # Thank-you page
│   └── static
│       └── styles.css     # Minimal clean styling
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

---

## 🧪 Test locally
1. Submit a few entries via `/`.
2. Export with your admin token to verify CSV contents:
    ```bash
    curl -H "Authorization: Bearer $ADMIN_TOKEN" http://127.0.0.1:8000/admin/export
    ```

---

## 🧯 Troubleshooting
- **403 / Unauthorized**: Check you passed the correct `Authorization: Bearer <token>` header and that `.env` is loaded.
- **Encryption error**: Ensure `SECRET_PASSPHRASE` is set in `.env` and you restarted the app after editing.
- **SQLite locked**: Keep `--workers 1` (single worker) or use Dockerfile's default CMD.

---

## 📜 License
MIT — customize as you like. Good luck with the prom! 🎈
