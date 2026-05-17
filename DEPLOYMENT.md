# PakShop AI Deployment

PakShop AI is a FastAPI web app with a single HTML frontend and a SQLite-backed login/chat history system.

## Local Run

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

## Required Environment Variables

```env
APP_ENV=production
SITE_URL=https://your-live-domain.com
GROQ_API_KEY=your_real_groq_key
SECRET_KEY=your_long_random_secret
DATABASE_PATH=data/pakcommerce.db
```

Do not commit the real `.env` file.

## Render Deployment

1. Push the project to GitHub.
2. Create a new Render Blueprint or Web Service.
3. If using the included `render.yaml`, Render can read the build/start settings automatically.
4. Add `SITE_URL` and `GROQ_API_KEY` in the Render dashboard.
5. Keep the persistent disk enabled so `data/pakcommerce.db` survives redeploys.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

## Production Notes

- Logged-in chat history is saved in SQLite at `DATABASE_PATH`.
- For bigger traffic, move from SQLite to PostgreSQL.
- After deployment, update `SITE_URL` to the final live URL so `/sitemap.xml` is correct.
- Submit the live `/sitemap.xml` in Google Search Console for indexing.
