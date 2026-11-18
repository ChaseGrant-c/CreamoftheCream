# Cream of the Cream

A private focus list. You keep a short roster of people, save the posts worth reading, and open the day on two panels: today's posts, then the people in rotation.

Django runs on Render. Supabase holds accounts and the Postgres database.

## Pages

- Today (`/`) shows the top posts of the day, then popular people underneath.
- People (`/people/`) is an alphabetical contact list with favorites and search.
- A person (`/people/<id>/`) shows their name, profile links, description, private notes, and saved posts.

Until Supabase keys are set, a local sample roster is available from the sign-in page.

## Run it locally

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py runserver
```

Open http://127.0.0.1:8000 and choose **Browse the sample roster**.

Copy `.env.example` to `.env` when you have Supabase values. `.env` stays off git.

## Environment variables

| Name | Where | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | Render generates it | Django session signing |
| `DEBUG` | `false` on Render | Turns off the sample roster |
| `DATABASE_URL` | Supabase → Project Settings → Database | Postgres connection string. Use the session pooler (port 5432) and include `sslmode=require`. Postgres 15 or newer. |
| `SUPABASE_URL` | Supabase → Project Settings → API | Auth API |
| `SUPABASE_ANON_KEY` | Supabase → Project Settings → API | Auth from the Django server. This key is public by design. Do not use the service role key. |
| `ALLOWED_HOSTS` | Your `*.onrender.com` host | Comma-separated |
| `CSRF_TRUSTED_ORIGINS` | `https://your-app.onrender.com` | Comma-separated, with the scheme |
| `TIME_ZONE` | Default `America/Denver` | Decides which posts count as today |

`render.yaml` is the Render blueprint. After the first deploy migrates the tables, run `supabase/rls.sql` in the Supabase SQL editor.

## Feeds

Profile links for LinkedIn, Instagram, Facebook, X, Threads, and TikTok are stored and opened as links. The app does not log in to those sites or pull their feeds. A public RSS or Atom URL, such as a newsletter or blog, can be checked from a person's page. Posts can also be pasted by hand.

## What is still needed

1. A Supabase project: project URL, anon key, and the Postgres connection string. Put the database URL in Render or a local `.env`. Do not send the service role key.
2. Whether Supabase email confirmation is on. If it is, new accounts must confirm before they can sign in.
3. A Render account connected to this repo, then the env vars above.
4. Where this repo should live online (Cursor or GitHub). It is separate from `data5570_mycode` and has no remote yet.
