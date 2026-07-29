# Publish to Google Play Store

Step-by-step guide to publish **AI English Teacher** on the Google Play Store.

**Cost:** $25 one-time Google Play Developer registration fee  
**Build time:** ~15–20 minutes per build (cloud build via EAS)

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| Google account | Gmail account |
| Developer account | https://play.google.com/console/signup ($25) |
| Backend API | Deployed and reachable (Render or Oracle Cloud) |
| Node.js 20+ | On your development machine |
| Expo account | Free at https://expo.dev |

---

## Step 1 — Configure API URL

Edit `mobile/.env`:

```env
EXPO_PUBLIC_API_URL=https://ai-english-teacher-api.onrender.com/api/v1
```

For Oracle Cloud VM:
```env
EXPO_PUBLIC_API_URL=http://YOUR_VM_IP/api/v1
```

Rebuild after changing this value.

---

## Step 2 — Install EAS CLI

```bash
npm install -g eas-cli
eas login
```

---

## Step 3 — Link Expo project

```bash
cd ai-english-teacher/mobile
npm install
eas init
```

This creates an EAS project and updates `app.json` with your `projectId`.

---

## Step 4 — Build production AAB

Google Play requires an **Android App Bundle** (.aab), not APK.

```bash
npm run build:android
```

Or manually:
```bash
eas build --platform android --profile production
```

- First build: EAS generates an Android keystore (save credentials — Expo stores them)
- Build runs in the cloud (~15 min)
- Download link appears in terminal and at https://expo.dev

### Test with APK first (optional)

```bash
eas build --platform android --profile preview
```

Install the APK on your phone to test before Play Store submission.

---

## Step 5 — Google Play Console setup

1. Go to https://play.google.com/console
2. **Create app**
   - App name: `AI English Teacher`
   - Default language: English
   - App or game: App
   - Free or paid: Free

3. Complete **Dashboard** checklist:

### Store listing

| Field | Suggested content |
|-------|-------------------|
| Short description | Learn English with your personal AI teacher. Practice conversations, take assessments, track progress. |
| Full description | AI English Teacher helps you improve English through interactive AI role-play conversations, placement assessments, and personalized skill tracking. Features: AI conversation practice (job interviews, travel, restaurant, business), CEFR/IELTS/PTE estimates, grammar feedback, text-to-speech, progress dashboard. |
| App icon | 512×512 PNG (use `assets/icon.png` scaled up) |
| Feature graphic | 1024×500 PNG |
| Screenshots | At least 2 phone screenshots (1080×1920 or similar) |

### Content rating

- Complete the questionnaire (likely **Everyone** or **Teen** depending on AI content)
- No violence, gambling, etc.

### Target audience

- Select age groups (13+ recommended for AI chat apps)

### Privacy policy

**Required.** Host a privacy policy URL. Minimum content:
- What data you collect (email, learning progress)
- How AI processes conversations
- Third-party services (OpenAI/Azure/Groq if used)
- Contact email

You can host on GitHub Pages or your website.

### Data safety

Declare:
- Email address collected
- App activity (learning data)
- Data encrypted in transit (HTTPS)
- Users can request deletion

---

## Step 6 — Upload AAB

1. Play Console → **Release** → **Testing** → **Internal testing** (recommended first)
2. **Create new release**
3. Upload the `.aab` file from EAS build
4. Add release notes: `Initial release — AI English practice and assessment`
5. **Review release** → **Start rollout to Internal testing**

### Add testers

Internal testing → **Testers** tab → create email list → add your Gmail

Testers get a link to install from Play Store.

---

## Step 7 — Production release

After internal testing passes:

1. **Release** → **Production** → **Create new release**
2. Upload same or newer AAB
3. Submit for review (1–7 days typically)

---

## Automated submit (optional)

If you have a Google Play service account JSON:

1. Play Console → Setup → API access → Link Google Cloud project
2. Create service account with Release Manager role
3. Download JSON → save as `mobile/google-play-service-account.json` (gitignored)
4. Submit:
   ```bash
   eas submit --platform android --profile production
   ```

---

## App signing

EAS handles signing automatically on first build. Credentials stored at:
https://expo.dev → your project → Credentials

**Do not lose these** — required for app updates.

---

## Updating the app

1. Bump version in `app.json`:
   ```json
   "version": "1.0.1",
   "android": { "versionCode": 2 }
   ```
2. Rebuild: `npm run build:android`
3. Upload new AAB to Play Console

`eas.json` has `"autoIncrement": true` for production builds — version code increments automatically.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| **Login fails on app** | Check `EXPO_PUBLIC_API_URL`; ensure backend CORS not needed for native (it's not) |
| **HTTP API on Oracle VM** | `usesCleartextTraffic: true` is set in `app.json` |
| **Build fails** | Run `npm install` locally first; check `eas build` logs |
| **Play rejects app** | Add privacy policy URL; complete content rating |
| **AI responses slow** | Render free tier cold start — use Oracle Cloud for always-on |

---

## Checklist before submission

- [ ] `EXPO_PUBLIC_API_URL` points to production API
- [ ] Register/login works on real device
- [ ] Conversation practice works
- [ ] Assessment submits successfully
- [ ] App icon and screenshots uploaded
- [ ] Privacy policy URL live
- [ ] Content rating completed
- [ ] Data safety form filled

---

## Package name

`com.aienglishteacher.app` — cannot be changed after first upload.

To use your own package name, edit `app.json` → `android.package` **before** first build.
