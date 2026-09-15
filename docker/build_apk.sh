#!/usr/bin/env bash
# Builds the Android APK inside Docker so JDK/Android SDK never touch the host.
# Usage: SIMON_KEYSTORE_PASSWORD=... ./docker/build_apk.sh
set -euo pipefail
cd "$(dirname "$0")/.."

# On Windows/Git Bash, MSYS auto-converts path-like arguments (including
# inside -v HOST:CONTAINER specs), which mangles the volume mount. Disabling
# it is a no-op on Linux/macOS.
export MSYS_NO_PATHCONV=1

if [ ! -f keystore/release.keystore ]; then
    echo "No signing keystore found at keystore/release.keystore."
    echo "Generate one first (keep it forever -- losing it means future"
    echo "updates can't be installed over the old one without uninstalling):"
    echo "  keytool -genkeypair -v -keystore keystore/release.keystore -alias simon \\"
    echo "    -keyalg RSA -keysize 2048 -validity 10000"
    exit 1
fi

docker build -f docker/android-build.Dockerfile -t simon-android-build .
docker run --rm -v "$(pwd)":/app simon-android-build \
    --org com.tomershimshi.simon \
    --arch arm64-v8a \
    --android-signing-key-store /app/keystore/release.keystore \
    --android-signing-key-store-password "${SIMON_KEYSTORE_PASSWORD:?set SIMON_KEYSTORE_PASSWORD}" \
    --android-signing-key-password "${SIMON_KEYSTORE_PASSWORD:?set SIMON_KEYSTORE_PASSWORD}" \
    --android-signing-key-alias simon \
    --yes -v

echo "APK at build/apk/app.apk"
