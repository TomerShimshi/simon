this project is a Simon color-sequence memory game to help a stroke survivor practice memory, in Hebrew

## Run locally

```
pip install -r requirements-dev.txt
python main.py
```

## Test

```
pytest
```

## Deploy as a web app (Render)

The app can run as a hosted web app instead of an installed Android app, so
updates go live immediately with no reinstalling on the device.

1. Push this repo to GitHub (already set up as the `origin` remote).
2. In the [Render dashboard](https://dashboard.render.com), choose
   **New > Blueprint** and point it at this repo -- it will read
   `render.yaml` and create the web service automatically.
3. Once deployed, Render gives you a URL like
   `https://simon-xxxx.onrender.com` -- that's what to open/bookmark on the
   device that will play the game.

Locally, the same web entrypoint can be run with:

```
uvicorn web:app --host 0.0.0.0 --port 8000
```

### Persistent progress storage (Upstash Redis)

Render's free tier has no persistent disk -- its filesystem resets on every
restart/redeploy, which would otherwise wipe progress history each time the
app is updated. All progress stores go through `src/simon/kv_store.py`,
which uses a free Upstash Redis database when configured, falling back to
local JSON files (in `.local_data/`) for local development.

To set it up:

1. Create a free account at [upstash.com](https://upstash.com) (no credit
   card required) and create a Redis database (any region close to Render's
   is fine -- exact region doesn't matter much for this app's tiny traffic).
2. On the database's page, find the **REST API** section and copy the
   `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` values.
3. In the Render dashboard, open the `simon` service -> **Environment** ->
   add both as environment variables with those exact names.
4. Redeploy (Render redeploys automatically on the next git push, or use
   **Manual Deploy** in the dashboard to apply the new env vars immediately
   without waiting for a code change).

Without these two environment variables set, the app falls back to local
JSON files automatically -- so `python main.py` and local testing need no
Upstash account at all.

## Build the Android App Bundle (.aab)

Requires Docker. First time only, generate a signing keystore (keep it
forever -- losing it means future updates can't be installed over the old one
without uninstalling first):

```
keytool -genkeypair -v -keystore keystore/release.keystore -alias simon \
  -keyalg RSA -keysize 2048 -validity 10000
```

Then build:

```
APK_PASSWORD=yourpassword ./docker/build_aab.sh
```

Output lands at `build/aab/app.aab`, ready to upload to Google Play Console
(Testing → Internal testing → Create new release).
