"""The Android app is the dashboard, bundled, and asks the phone for nothing.

These checks read the project files as text rather than building the app,
because the Android SDK is not part of this repository's test environment.
They pin the promises the app makes to the person holding the phone:

* **No permissions.** The manifest declares none. Without INTERNET the app
  cannot send anything anywhere, by design or by mistake; calling a station
  and opening its web page hand off to the dialler and the browser.
* **The pipeline's page, not another one.** The build copies
  `site/locality.html` in; the assets folder is never committed, so the
  app cannot carry a page the pipeline did not build.
* **No secrets in the repository.** Keystores, signing properties and the
  local SDK path are ignored by git.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANDROID = ROOT / "android"
MANIFEST = ANDROID / "app" / "src" / "main" / "AndroidManifest.xml"
BUILD = ANDROID / "app" / "build.gradle.kts"
ACTIVITY = ANDROID / "app" / "src" / "main" / "java" / "in" / "crimemap" / "locality" / "MainActivity.kt"
ASSETS = ANDROID / "app" / "src" / "main" / "assets"


def test_the_manifest_asks_for_no_permissions():
    text = re.sub(r"<!--.*?-->", "", MANIFEST.read_text(encoding="utf-8"), flags=re.S)
    assert "<uses-permission" not in text
    assert "android.permission." not in text
    assert 'android:allowBackup="false"' in text
    assert 'android:usesCleartextTraffic="false"' in text


def test_the_build_bundles_the_pipelines_page_and_nothing_else():
    text = BUILD.read_text(encoding="utf-8")
    assert '"../site/locality.html"' in text
    assert 'dir("src/main/assets")' in text
    assert "fonts.googleapis.com" in text and "fonts.gstatic.com" in text
    assert "dependsOn(copyDashboard)" in text
    # The page is copied in at build time; a committed copy would go stale.
    assert not ASSETS.exists() or not list(ASSETS.glob("*.html"))


def test_the_activity_serves_assets_over_https_and_hands_off_calls_and_links():
    text = ACTIVITY.read_text(encoding="utf-8")
    assert "WebViewAssetLoader" in text
    assert "https://appassets.androidplatform.net/assets/locality.html" in text
    assert "allowFileAccess = false" in text and "allowContentAccess = false" in text
    assert 'url.scheme == "tel"' in text and "Intent.ACTION_DIAL" in text
    assert "Intent.ACTION_VIEW" in text
    assert "domStorageEnabled = true" in text


def test_signing_material_and_build_outputs_are_ignored():
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    for pattern in ("*.jks", "*.keystore", "android/local.properties",
                    "android/keystore.properties", "android/app/src/main/assets/",
                    "android/app/build/", "android/.gradle/"):
        assert pattern in ignore, pattern
    assert not (ANDROID / "local.properties").exists()
    assert not (ANDROID / "keystore.properties").exists()
    assert not list(ANDROID.rglob("*.jks")) and not list(ANDROID.rglob("*.keystore"))


def test_the_wrapper_pins_a_gradle_version_the_plugin_supports():
    props = (ANDROID / "gradle" / "wrapper" / "gradle-wrapper.properties").read_text(encoding="utf-8")
    version = re.search(r"gradle-(\d+\.\d+(?:\.\d+)?)-", props).group(1)
    major, minor = (int(x) for x in version.split(".")[:2])
    assert (major, minor) >= (8, 9), version       # AGP 8.7 needs Gradle 8.9+
    assert (ANDROID / "gradlew").exists()
