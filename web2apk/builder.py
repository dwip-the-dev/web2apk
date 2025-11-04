import os
import json
import shutil
import requests
import subprocess
from pathlib import Path
from slugify import slugify

class Web2APKBuilder:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.sdk_path = self.get_android_sdk_path()
        
    def get_android_sdk_path(self):
        """Get Android SDK path from environment variables"""
        sdk_path = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
        if not sdk_path:
            raise Exception("ANDROID_HOME environment variable not set")
        return Path(sdk_path)
    
    def get_latest_build_tools(self):
        """Get the latest build tools version"""
        build_tools_dir = self.sdk_path / "build-tools"
        versions = [d.name for d in build_tools_dir.iterdir() if d.is_dir()]
        if not versions:
            raise Exception("No build tools found in Android SDK")
        return sorted(versions)[-1]  
    
    def validate_website(self, website):
        """Validate if the website is accessible."""
        try:
            response = requests.get(website, timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def create_android_project(self, config):
        """Create complete Android project structure"""
        project_path = Path(config['output_dir']) / slugify(config['app_name'])
        

        dirs = [
            "app/src/main/res/drawable",
            "app/src/main/res/values",
            "app/src/main/res/layout",
            f"app/src/main/java/{config['package_name'].replace('.', '/')}",
            "app/src/main/assets",
            "app/src/main/res/drawable-hdpi",
            "app/src/main/res/drawable-mdpi",
            "app/src/main/res/drawable-xhdpi",
            "app/src/main/res/drawable-xxhdpi",
            "app/src/main/res/drawable-xxxhdpi",
            "gradle/wrapper",
        ]
        
        for dir_path in dirs:
            (project_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        return project_path
    
    def generate_android_manifest(self, config):
        """Generate AndroidManifest.xml"""
        return f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />

    <application
        android:allowBackup="true"
        android:icon="@drawable/ic_launcher"
        android:label="{config['app_name']}"
        android:theme="@style/AppTheme"
        android:usesCleartextTraffic="true"
        tools:targetApi="28">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:configChanges="orientation|screenSize"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>'''
    
    def generate_main_activity(self, config):
        """Generate MainActivity.java - FIXED: removed deprecated setAppCacheEnabled"""
        return f'''package {config['package_name']};

import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {{
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webview);
        
        // Enable JavaScript
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webSettings.setDatabaseEnabled(true);
        webSettings.setLoadWithOverviewMode(true);
        webSettings.setUseWideViewPort(true);
        webSettings.setBuiltInZoomControls(true);
        webSettings.setDisplayZoomControls(false);
        webSettings.setSupportZoom(true);
        webSettings.setDefaultFixedFontSize(14);
        webSettings.setDefaultFontSize(14);
        
        // Cache settings (removed deprecated setAppCacheEnabled)
        webSettings.setCacheMode(WebSettings.LOAD_DEFAULT);
        
        // Set user agent
        webSettings.setUserAgentString("Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36");

        webView.setWebViewClient(new WebViewClient() {{
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {{
                view.loadUrl(url);
                return true;
            }}
            
            @Override
            public void onPageFinished(WebView view, String url) {{
                super.onPageFinished(view, url);
                // Inject CSS to improve mobile experience
                view.loadUrl("javascript:(function() {{ " +
                    "var viewport = document.querySelector('meta[name=viewport]'); " +
                    "if (!viewport) {{ " +
                    "    viewport = document.createElement('meta'); " +
                    "    viewport.name = 'viewport'; " +
                    "    document.head.appendChild(viewport); " +
                    "}} " +
                    "viewport.content = 'width=device-width, initial-scale=1.0'; " +
                    "}})()");
            }}
        }});
        
        webView.loadUrl("{config['website']}");
    }}

    @Override
    public void onBackPressed() {{
        if (webView.canGoBack()) {{
            webView.goBack();
        }} else {{
            super.onBackPressed();
        }}
    }}
}}'''
    
    def generate_layout(self):
        """Generate activity_main.xml"""
        return '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <WebView
        android:id="@+id/webview"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

</LinearLayout>'''
    
    def generate_strings_xml(self, config):
        """Generate strings.xml"""
        return f'''<resources>
    <string name="app_name">{config['app_name']}</string>
</resources>'''
    
    def generate_styles_xml(self):
        """Generate styles.xml"""
        return '''<resources>
    <style name="AppTheme" parent="Theme.AppCompat.Light.DarkActionBar">
        <item name="colorPrimary">#2196F3</item>
        <item name="colorPrimaryDark">#1976D2</item>
        <item name="colorAccent">#FF4081</item>
    </style>
</resources>'''
    
    def generate_app_build_gradle(self, config):
        """Generate app/build.gradle - FIXED: added namespace"""
        return f'''plugins {{
    id 'com.android.application'
}}

android {{
    namespace "{config['package_name']}"
    compileSdkVersion 33
    buildToolsVersion "{config['build_tools_version']}"

    defaultConfig {{
        applicationId "{config['package_name']}"
        minSdkVersion 21
        targetSdkVersion 33
        versionCode {config['version_code']}
        versionName "{config['version']}"
    }}

    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
        debug {{
            minifyEnabled false
            debuggable true
        }}
    }}
    
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}
}}

dependencies {{
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'androidx.webkit:webkit:1.7.0'
}}'''
    
    def generate_project_build_gradle(self):
        """Generate project build.gradle"""
        return '''buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:7.4.2'
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

task clean(type: Delete) {
    delete rootProject.buildDir
}'''
    
    def generate_gradle_wrapper_properties(self):
        """Generate gradle-wrapper.properties"""
        return '''distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-7.5-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists'''
    
    def copy_icon(self, icon_path, project_path):
        """Copy app icon to all density folders"""
        icon_sizes = {
            'drawable-mdpi': 48,
            'drawable-hdpi': 72,
            'drawable-xhdpi': 96,
            'drawable-xxhdpi': 144,
            'drawable-xxxhdpi': 192
        }
        
        for folder, size in icon_sizes.items():
            dest_dir = project_path / "app/src/main/res" / folder
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_file = dest_dir / "ic_launcher.png"
            shutil.copy2(icon_path, dest_file)
    
    def run_gradle_build(self, project_path):
        """Run Gradle build to generate APK"""

        gradle_cmd = ["gradle", "assembleRelease", "--warning-mode", "all"]
        
        print(f"🏗️  Running: {' '.join(gradle_cmd)}")
        print(f"📁 In directory: {project_path}")
        

        try:
            result = subprocess.run(
                gradle_cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300 
            )
            
            if result.returncode != 0:
                print(f"❌ Build failed with return code: {result.returncode}")
                if result.stdout:
                    print(f"📝 Build output: {result.stdout}")
                if result.stderr:
                    print(f"❌ Build errors: {result.stderr}")
                raise Exception(f"Gradle build failed")
            
            print("✅ Build completed successfully!")
            if result.stdout:
                print(f"📝 Build output: {result.stdout}")
            return True
            
        except subprocess.TimeoutExpired:
            raise Exception("Gradle build timed out after 5 minutes")
        except FileNotFoundError:
            raise Exception("Gradle not found. Please install Gradle: sudo apt install gradle")
        except Exception as e:
            raise Exception(f"Build process failed: {str(e)}")
    
    def create_gradle_wrapper(self, project_path):
        """Create minimal gradle wrapper files"""
        wrapper_dir = project_path / "gradle/wrapper"
        wrapper_dir.mkdir(parents=True, exist_ok=True)
        

        gradlew_file = project_path / "gradlew"
        gradlew_content = '''#!/bin/bash
# Use system gradle
exec gradle "$@"
'''
        gradlew_file.write_text(gradlew_content)
        gradlew_file.chmod(0o755)
        

        gradlew_bat = project_path / "gradlew.bat"
        gradlew_bat.write_text('''@echo off
@rem Use system gradle
gradle %*
''')
    
    def sign_apk(self, apk_path, keystore_path, keystore_password, key_alias):
        """Sign an APK file with provided keystore"""
        try:
            apk_path = Path(apk_path)
            keystore_path = Path(keystore_path)
            
            if not keystore_path.exists():
                raise Exception(f"Keystore file not found: {keystore_path}")
            
            if not apk_path.exists():
                raise Exception(f"APK file not found: {apk_path}")
            

            signed_apk_path = apk_path.parent / f"{apk_path.stem}-signed{apk_path.suffix}"
            

            build_tools_dir = self.sdk_path / "build-tools"
            latest_build_tools = sorted([d.name for d in build_tools_dir.iterdir() if d.is_dir()])[-1]
            apksigner_path = build_tools_dir / latest_build_tools / "apksigner"
            

            sign_cmd = [
                str(apksigner_path),
                "sign",
                "--ks", str(keystore_path),
                "--ks-pass", f"pass:{keystore_password}",
                "--key-pass", f"pass:{keystore_password}",
                "--ks-key-alias", key_alias,
                "--out", str(signed_apk_path),
                str(apk_path)
            ]
            
            print(f"🔐 Signing APK with: {keystore_path.name}")
            result = subprocess.run(sign_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"APK signing failed: {result.stderr}")
            
            print(f"✅ APK signed successfully: {signed_apk_path.name}")
            return str(signed_apk_path)
            
        except Exception as e:
            raise Exception(f"APK signing error: {str(e)}")

    def create_keystore(self, keystore_path, password, alias, distinguished_name):
        """Create a new keystore for signing"""
        try:
            keystore_path = Path(keystore_path)
            

            keystore_path.parent.mkdir(parents=True, exist_ok=True)
            

            dn_string = f"CN={distinguished_name.get('name', 'Unknown')}, " \
                       f"OU={distinguished_name.get('unit', 'Unknown')}, " \
                       f"O={distinguished_name.get('organization', 'Unknown')}, " \
                       f"L={distinguished_name.get('city', 'Unknown')}, " \
                       f"ST={distinguished_name.get('state', 'Unknown')}, " \
                       f"C={distinguished_name.get('country', 'US')}"
            
            keytool_cmd = [
                "keytool",
                "-genkey",
                "-v",
                "-keystore", str(keystore_path),
                "-alias", alias,
                "-keyalg", "RSA",
                "-keysize", "2048",
                "-validity", "10000",
                "-dname", dn_string,
                "-storepass", password,
                "-keypass", password
            ]
            
            print(f"🔐 Creating new keystore: {keystore_path}")
            result = subprocess.run(keytool_cmd, capture_output=True, text=True, input=f"{password}\n")
            
            if result.returncode != 0:
                raise Exception(f"Keystore creation failed: {result.stderr}")
            
            print(f"✅ Keystore created successfully: {keystore_path}")
            return str(keystore_path)
            
        except Exception as e:
            raise Exception(f"Keystore creation error: {str(e)}")

    def build_apk(self, website, package_name, app_name, icon_path, output_dir, version, version_code, 
                  keystore_path=None, keystore_password=None, key_alias=None):
        """Main method to build APK with optional signing"""
        

        if not self.validate_website(website):
            raise Exception(f"Website {website} is not accessible")
        

        build_tools_version = self.get_latest_build_tools()
        
        config = {
            'website': website,
            'package_name': package_name,
            'app_name': app_name,
            'output_dir': output_dir,
            'version': version,
            'version_code': version_code,
            'build_tools_version': build_tools_version
        }
        

        project_path = self.create_android_project(config)
        print(f"📁 Project created at: {project_path}")
        

        files = {
            "app/src/main/AndroidManifest.xml": self.generate_android_manifest(config),
            f"app/src/main/java/{package_name.replace('.', '/')}/MainActivity.java": self.generate_main_activity(config),
            "app/src/main/res/layout/activity_main.xml": self.generate_layout(),
            "app/src/main/res/values/strings.xml": self.generate_strings_xml(config),
            "app/src/main/res/values/styles.xml": self.generate_styles_xml(),
            "app/build.gradle": self.generate_app_build_gradle(config),
            "build.gradle": self.generate_project_build_gradle(),
            "gradle/wrapper/gradle-wrapper.properties": self.generate_gradle_wrapper_properties(),
            "settings.gradle": f"include ':app'",
            "gradle.properties": "org.gradle.jvmargs=-Xmx2048m\nandroid.useAndroidX=true\nandroid.enableJetifier=true"
        }
        

        for file_path, content in files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            print(f"📄 Created: {file_path}")
        

        self.create_gradle_wrapper(project_path)
        print("📦 Gradle wrapper created")
        

        self.copy_icon(icon_path, project_path)
        print("🖼️  Icon copied")
        

        print("🚀 Starting APK build...")
        self.run_gradle_build(project_path)
        

        print("🔍 Looking for generated APK...")
        

        possible_apk_locations = [
            "app/build/outputs/apk/release/app-release-unsigned.apk",  
            "app/build/outputs/apk/release/app-release.apk",
            "app/build/outputs/apk/debug/app-debug-unsigned.apk",
            "app/build/outputs/apk/debug/app-debug.apk", 
        ]
        
        apk_path = None
        for location in possible_apk_locations:
            check_path = project_path / location
            if check_path.exists():
                apk_path = check_path
                print(f"✅ Found APK at: {apk_path}")
                break
        

        if not apk_path:
            print("🔍 Searching recursively for APK files...")
            apk_files = list(project_path.glob("**/*.apk"))
            if apk_files:
                apk_path = apk_files[0]
                print(f"✅ Found APK at: {apk_path}")
            else:
                raise Exception("APK file not found after successful build")
        

        final_apk_name = f"{slugify(app_name)}-v{version}.apk"
        final_apk_path = Path(output_dir) / final_apk_name
        shutil.copy2(apk_path, final_apk_path)
        

        file_size = final_apk_path.stat().st_size / (1024 * 1024)  
        
        print(f"🎉 APK built successfully!")
        print(f"📦 Output: {final_apk_path}")
        print(f"📱 File size: {file_size:.2f} MB")
        print(f"🌐 Website: {website}")
        print(f"📋 Package: {package_name}")
        

        if keystore_path and keystore_password and key_alias:
            print("🔐 Starting APK signing...")
            signed_apk_path = self.sign_apk(
                final_apk_path, 
                keystore_path, 
                keystore_password, 
                key_alias
            )
            print(f"✅ Signed APK: {signed_apk_path}")
            return signed_apk_path
        else:
            print(f"🔐 Note: This is an unsigned APK. You can sign it for production use.")
            return str(final_apk_path)

def main():
    builder = Web2APKBuilder()
    print("Web2APK Builder - Real APK Generator")

if __name__ == "__main__":
    main()
