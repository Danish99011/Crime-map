# Locality Crime Map for Android

The dashboard (`site/locality.html`), bundled into an app that opens it
offline and hands station phone numbers to the dialler.

The app asks for **no permissions**. It carries the whole page inside it,
reads nothing from the network, and cannot phone home: it has no INTERNET
permission to do so with. Calling a station and opening a station's own
page on mumbaipolice.gov.in both leave the app for the phone's dialler and
browser.

## Build

1. Build the dashboard from the repository root, so there is a page to bundle:

       PYTHONPATH=. python3 -m pipeline.mumbai
       PYTHONPATH=. python3 scripts/build_mumbai_stations.py
       PYTHONPATH=. python3 -m pipeline.build_locality_page

2. Open the `android/` folder in Android Studio (Ladybug or newer) and let it
   sync. It installs the Android SDK platform 35 and build tools on first
   sync. Or, with an SDK already installed and `ANDROID_HOME` set:

       cd android && ./gradlew assembleDebug

   The debug APK lands in `app/build/outputs/apk/debug/`. The build copies
   `site/locality.html` into `app/src/main/assets/` first (that folder is
   not committed), and refuses to build if the page is missing.

A release build needs a signing key. Keep it out of the repository: put the
keystore and its passwords in `android/keystore.properties` (ignored by
git) and wire it into `app/build.gradle.kts` locally. Never commit a
keystore, a `local.properties`, or a password.

## Updating the data

The page inside the app is a snapshot of the data at build time, and says
so in its footer. To ship fresher data, rebuild the page and the app. A
version that refreshes over the air needs a public host for the aggregate,
which this repository does not yet have.
