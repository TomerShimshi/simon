FROM eclipse-temurin:17-jdk-jammy

ENV ANDROID_SDK_ROOT=/opt/android-sdk \
    PATH=/opt/android-sdk/cmdline-tools/latest/bin:/opt/android-sdk/platform-tools:$PATH \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl unzip git python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Android command-line tools (SDK manager)
RUN mkdir -p ${ANDROID_SDK_ROOT}/cmdline-tools \
    && curl -sSL -o /tmp/cmdline-tools.zip \
        https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip \
    && unzip -q /tmp/cmdline-tools.zip -d ${ANDROID_SDK_ROOT}/cmdline-tools \
    && mv ${ANDROID_SDK_ROOT}/cmdline-tools/cmdline-tools ${ANDROID_SDK_ROOT}/cmdline-tools/latest \
    && rm /tmp/cmdline-tools.zip

RUN yes | sdkmanager --licenses > /dev/null \
    && sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"

RUN pip3 install --no-cache-dir flet

# Flutter is downloaded fresh into this container by `flet build`; git then
# refuses to trust it because the extracted files aren't "owned" the way git
# expects inside the container filesystem. Safe here since the container is
# single-purpose and disposable.
RUN git config --global --add safe.directory '*'

# Pre-warm the Flutter SDK download into this image layer (installs to
# /root/flutter, outside of /app so the bind mount at `docker run` time
# doesn't hide it) so real builds don't redownload/reinstall it every time.
RUN mkdir -p /tmp/warmup && cd /tmp/warmup \
    && echo 'import flet as ft' > main.py \
    && echo 'def main(page: ft.Page): pass' >> main.py \
    && echo 'ft.run(main)' >> main.py \
    && flet build apk --org com.example.warmup --yes || true \
    && rm -rf /tmp/warmup

WORKDIR /app
ENTRYPOINT ["flet", "build", "apk"]
