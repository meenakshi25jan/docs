# AI English Teacher — Mobile App (Android / Google Play)

React Native mobile app built with **Expo** — connects to the same FastAPI backend as the web app.

## Features

- Login / Register (secure token storage)
- Student dashboard (CEFR, IELTS, PTE, skill scores)
- AI conversation practice (role-play scenarios)
- Text-to-speech for AI responses
- Placement assessment

## Quick start (development)

### Prerequisites

- Node.js 20+
- [Expo Go](https://expo.dev/go) app on your Android phone (for testing)
- Backend API running (Render, Oracle Cloud, or local)

### Setup

```bash
cd ai-english-teacher/mobile
npm install
cp .env.example .env
# Edit .env — set EXPO_PUBLIC_API_URL to your API
npm start
```

Scan the QR code with **Expo Go** on Android.

### API URL

| Backend | EXPO_PUBLIC_API_URL |
|---------|---------------------|
| Render (production) | `https://ai-english-teacher-api.onrender.com/api/v1` |
| Oracle Cloud VM | `http://YOUR_VM_IP/api/v1` |
| Local (Android emulator) | `http://10.0.2.2:8000/api/v1` |

---

## Publish to Google Play Store

**Full guide:** [GOOGLE_PLAY.md](./GOOGLE_PLAY.md)

### Summary

1. Create [Google Play Developer](https://play.google.com/console) account ($25 one-time)
2. Install EAS CLI: `npm install -g eas-cli`
3. Login: `eas login`
4. Configure project: `eas build:configure`
5. Build AAB: `npm run build:android`
6. Upload to Play Console → Internal testing → Production

---

## Project structure

```
mobile/
├── app/                  # Expo Router screens
│   ├── login.tsx
│   ├── register.tsx
│   └── (tabs)/
│       ├── index.tsx     # Home / dashboard
│       ├── practice.tsx  # AI conversation
│       ├── assessment.tsx
│       └── profile.tsx
├── src/
│   ├── lib/api.ts        # API client (SecureStore tokens)
│   └── constants.ts
├── app.json              # Expo config
├── eas.json              # EAS Build profiles
└── GOOGLE_PLAY.md        # Publishing guide
```

---

## Build commands

```bash
# Development (Expo Go)
npm start

# Preview APK (install directly on phone)
npm run build:preview

# Production AAB (Google Play)
npm run build:android
```

---

## Related docs

- [GOOGLE_PLAY.md](./GOOGLE_PLAY.md) — Google Play publishing
- [../RUNBOOK.md](../RUNBOOK.md) — Backend API & deployment
- [../deploy/oracle-cloud/VM_SETUP.md](../deploy/oracle-cloud/VM_SETUP.md) — Oracle Cloud VM
