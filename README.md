# 🧱 Web2APK

**Turn any website into an Android app — straight from your terminal ⚡**

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue?style=for-the-badge)]()
[![License](https://img.shields.io/github/license/dwip-the-dev/web2apk?style=for-the-badge)]()

---

## 🚀 Overview

**Web2APK** lets you convert any website into a working Android `.apk` directly from your terminal — no Android Studio, no bloat, no BS.
Just one command and your website becomes a full-blown Android app with icon, splash, signing, and all that good stuff 💀🔥

---

## 🧩 Installation

```bash
# Clone the repo
git clone https://github.com/dwip-the-dev/web2apk.git
cd web2apk

# Install in editable mode
pip install -e .
```

---

## ✅ Prerequisites Checklist

Before running Web2APK, make sure you’ve got:

| Requirement     | Command to check    |
| --------------- | ------------------- |
| **Python 3.7+** | `python3 --version` |
| **Java JDK 8+** | `java -version`     |
| **Android SDK** | Set `$ANDROID_HOME` |
| **Gradle**      | `gradle --version`  |

---

## ⚙️ Setup Android SDK

```bash
# Download Android Command Line Tools
mkdir -p ~/android-sdk
cd ~/android-sdk
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
unzip commandlinetools-linux-9477386_latest.zip
mkdir cmdline-tools
mv tools cmdline-tools/latest

# Add to ~/.bashrc or ~/.zshrc
echo 'export ANDROID_HOME="$HOME/android-sdk"' >> ~/.bashrc
echo 'export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Install required components
yes | sdkmanager --licenses
sdkmanager "platform-tools" "build-tools;34.0.0" "platforms;android-33"
```

---

## 🧠 Test Installation

```bash
web2apk --help
```

---

## 💥 Advanced Usage (All Options)

### 🏗️ Build an APK

```bash
web2apk --website "https://example.com" \
        --package-name "com.example.myapp" \
        --app-name "My Cool App" \
        --icon "/path/to/icon.png" \
        --output-dir "./my-apks" \
        --version "1.0.0" \
        --version-code 1
```

---

### 🔐 With APK Signing (For Production)

```bash
# Create a keystore
web2apk --create-keystore

# Build with signing
web2apk --website "https://example.com" \
        --package-name "com.example.myapp" \
        --app-name "My App" \
        --icon "./icon.png" \
        --keystore-path "/home/user/myapp.jks" \
        --keystore-password "mypassword" \
        --key-alias "myapp"
```

---

### 🧾 Sign an Existing APK

```bash
web2apk --sign-existing "/path/to/app.apk" \
        --keystore-path "/home/user/myapp.jks" \
        --keystore-password "mypassword" \
        --key-alias "myapp"
```

---

## 🖼️ Creating an Icon

```bash
# Create a simple icon using ImageMagick
sudo apt install imagemagick
convert -size 512x512 xc:blue -fill white -draw 'circle 256,256 256,100' icon.png
```

---

## 🧰 Troubleshooting

### 1️⃣ Android SDK not found

```bash
export ANDROID_HOME="$HOME/android-sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
```

Verify:

```bash
echo $ANDROID_HOME
sdkmanager --list
```

### 2️⃣ Gradle not found

```bash
sudo apt install gradle  # Ubuntu/Debian
brew install gradle      # macOS
```

### 3️⃣ Java not found

```bash
sudo apt install openjdk-11-jdk
```

### 4️⃣ Build takes too long

First build downloads components (5–10 mins still maybe depends upon internet and ur pc).

Later builds: 1–2 mins (maybe?.. cuz if you got a 1990 pc ur cooked af)⚡

---

## 📱 Testing Your APK

```bash
# Install on connected Android device
adb install build/my-cool-app-v1.0.0.apk
```

or open with your emulator
---

## 🏁 What You Get

✅ Fully working Android APK

✅ Native WebView wrapper

✅ Back button navigation

✅ Mobile viewport optimization

✅ Signed & ready for Play Store

---

## 🤘 Author

**Dwip**
🔥 16-year-old developer on a mission to automate everything.
🔗 [github.com/dwip-the-dev](https://github.com/dwip-the-dev)

---

## 🧾 License

[MIT License](LICENSE) — free to use, modify, and ship or whatever you idc.
