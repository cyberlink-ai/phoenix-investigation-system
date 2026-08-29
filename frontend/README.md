# Phoenix Frontend

React + Vite scaffold. Current `Dashboard.jsx` is a **functional scaffold**,
not the final design — it exists to prove the frontend can drive the real
backend logic (camera list, Investigation Path Planner). The actual
investigation-console UI (per docs/phoenix_master_prompt.md Phase 10) is a
dedicated design pass, to be done deliberately rather than left as Tailwind
defaults — see the `console` color tokens in `tailwind.config.js` as a
starting point only.

## Run locally

```bash
cd frontend
npm install
cp .env.example .env   # set VITE_API_BASE_URL if backend isn't on localhost:8000
npm run dev
```

Visit `http://localhost:5173`. Make sure the backend is running first
(see `../backend/README.md`).

## Deploy to Vercel

1. Push this repo to GitHub.
2. Import the repo in Vercel, set the **root directory** to `frontend`.
3. Vercel auto-detects the Vite build (`npm run build`, output `dist`) via `vercel.json`.
4. Set the environment variable `VITE_API_BASE_URL` in the Vercel project
   settings to your deployed backend URL (Render/Railway/Fly — see
   `../backend/README.md`).
5. Deploy. The site will be reachable from phone, laptop, or any device via
   the Vercel URL.
