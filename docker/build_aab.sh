#!/usr/bin/env bash
# Builds the Android App Bundle (.aab) required for Play Console submission,
# inside Docker so JDK/Android SDK never touch the host.
# Usage: APK_PASSWORD=... ./docker/build_aab.sh [build-number]
# build-number must increase on every Play Console upload (Play rejects a
# repeat); defaults to 1 for the first release.
set -euo pipefail
cd "$(dirname "$0")/.."

BUILD_NUMBER="${1:-1}"

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

KEYSTORE_PASSWORD="${APK_PASSWORD:-${SIMON_KEYSTORE_PASSWORD:?set APK_PASSWORD (or SIMON_KEYSTORE_PASSWORD)}}"

docker build -f docker/android-build.Dockerfile -t simon-android-build .
docker run --rm --entrypoint flet -v "$(pwd)":/app simon-android-build \
    build aab \
    --org com.tomershimshi.simon \
    --android-signing-key-store /app/keystore/release.keystore \
    --android-signing-key-store-password "$KEYSTORE_PASSWORD" \
    --android-signing-key-password "$KEYSTORE_PASSWORD" \
    --android-signing-key-alias simon \
    --build-number "$BUILD_NUMBER" \
    --yes -v

echo "AAB at build/aab/app.aab"
