import os
import click
import subprocess
from pathlib import Path
from .builder import Web2APKBuilder

def check_android_sdk():
    """Check if Android SDK is available"""
    sdk_path = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    if not sdk_path or not os.path.exists(sdk_path):
        return False
    

    build_tools_dir = Path(sdk_path) / "build-tools"
    if not build_tools_dir.exists():
        return False
    

    versions = [d.name for d in build_tools_dir.iterdir() if d.is_dir()]
    if not versions:
        return False
    
    return True

@click.group()
def cli():
    """Web2APK - Convert websites to Android APK files"""
    pass

@cli.command()
@click.option('--website', prompt='🌐 Website address', help='The website URL to convert')
@click.option('--package-name', prompt='📦 Package name', help='Android package name (e.g., com.example.myapp)')
@click.option('--app-name', prompt='📱 App name', help='Name of your Android app')
@click.option('--icon', prompt='🖼️  Icon path', help='Path to app icon (PNG format, min 512x512)')
@click.option('--output-dir', default='./build', help='Output directory for APK')
@click.option('--version', default='1.0.0', help='App version')
@click.option('--version-code', default=1, help='App version code')
@click.option('--keystore-path', help='Full path to keystore file for signing (e.g., /home/user/keystore.jks)')
@click.option('--keystore-password', help='Keystore password', hide_input=True)
@click.option('--key-alias', help='Key alias in keystore')
@click.option('--sdk-path', help='Android SDK path (auto-detected from ANDROID_HOME)')
def build(website, package_name, app_name, icon, output_dir, version, version_code,
         keystore_path, keystore_password, key_alias, sdk_path):
    """Convert websites to Android APK files with optional signing."""
    
    click.echo(click.style("🚀 Web2APK - Website to APK Converter", fg="green", bold=True))
    click.echo("=" * 50)
    

    if not check_android_sdk():
        click.echo(click.style("❌ Error: Android SDK not found!", fg="red"))
        click.echo("Please install Android SDK and set ANDROID_HOME environment variable")
        click.echo("Or specify SDK path with --sdk-path")
        return
    

    if not website.startswith(('http://', 'https://')):
        website = 'https://' + website
    
    if not os.path.exists(icon):
        click.echo(click.style(f"❌ Error: Icon file '{icon}' not found!", fg="red"))
        return
    

    signing_params = [keystore_path, keystore_password, key_alias]
    has_some_signing_params = any(signing_params)
    has_all_signing_params = all(signing_params)
    
    if has_some_signing_params and not has_all_signing_params:
        click.echo(click.style("❌ Error: Signing requires all of --keystore-path, --keystore-password, and --key-alias", fg="red"))
        return
    
    if has_all_signing_params:
        if not os.path.exists(keystore_path):
            click.echo(click.style(f"❌ Error: Keystore file '{keystore_path}' not found!", fg="red"))
            return
        click.echo(click.style("🔐 APK will be signed after build", fg="yellow"))
    

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    try:
        builder = Web2APKBuilder()
        
        click.echo(click.style("📦 Building APK...", fg="yellow"))
        click.echo("This may take a few minutes...")
        
        apk_path = builder.build_apk(
            website=website,
            package_name=package_name,
            app_name=app_name,
            icon_path=icon,
            output_dir=output_dir,
            version=version,
            version_code=version_code,
            keystore_path=keystore_path,
            keystore_password=keystore_password,
            key_alias=key_alias
        )
        
        click.echo(click.style("✅ APK built successfully!", fg="green"))
        click.echo(click.style(f"📁 Output APK: {apk_path}", fg="blue"))
        click.echo(click.style(f"📱 App: {app_name}", fg="cyan"))
        click.echo(click.style(f"🌐 Website: {website}", fg="cyan"))
        
        if has_all_signing_params:
            click.echo(click.style("🔐 APK is signed and ready for production", fg="green"))
        else:
            click.echo(click.style("🔐 Note: APK is unsigned (development only)", fg="yellow"))
            click.echo(click.style("   Use --keystore-path, --keystore-password, and --key-alias to sign", fg="yellow"))
        
    except Exception as e:
        click.echo(click.style(f"❌ Error building APK: {str(e)}", fg="red"))
        if click.confirm('Show detailed error?'):
            import traceback
            traceback.print_exc()

@cli.command()
def create_keystore():
    """Create a new keystore for signing APKs"""
    click.echo(click.style("🔐 Create New Keystore", fg="cyan", bold=True))
    click.echo("=" * 30)
    
    keystore_path = click.prompt("📁 Keystore file path (e.g., /home/user/myapp.jks)")
    password = click.prompt("🔑 Keystore password", hide_input=True, confirmation_prompt=True)
    alias = click.prompt("🏷️  Key alias", default="myapp")
    
    click.echo("\n📝 Enter your distinguished name information:")
    name = click.prompt("   Full name", default="Unknown")
    unit = click.prompt("   Organizational Unit", default="Unknown")
    organization = click.prompt("   Organization", default="Unknown")
    city = click.prompt("   City/Locality", default="Unknown")
    state = click.prompt("   State/Province", default="Unknown")
    country = click.prompt("   Country Code (2 letters)", default="US")
    
    distinguished_name = {
        'name': name,
        'unit': unit,
        'organization': organization,
        'city': city,
        'state': state,
        'country': country
    }
    
    try:
        builder = Web2APKBuilder()
        keystore_path = builder.create_keystore(keystore_path, password, alias, distinguished_name)
        
        click.echo(click.style(f"✅ Keystore created successfully!", fg="green"))
        click.echo(click.style(f"📁 Location: {keystore_path}", fg="blue"))
        click.echo(click.style(f"🔑 Alias: {alias}", fg="cyan"))
        click.echo("\n💡 Use this keystore with:")
        click.echo(f"   --keystore-path '{keystore_path}'")
        click.echo(f"   --keystore-password '{password}'")
        click.echo(f"   --key-alias '{alias}'")
        
    except Exception as e:
        click.echo(click.style(f"❌ Error creating keystore: {str(e)}", fg="red"))

@cli.command()
def sign_existing():
    """Sign an existing APK file"""
    click.echo(click.style("🔐 Sign Existing APK", fg="cyan", bold=True))
    click.echo("=" * 25)
    
    apk_path = click.prompt("📁 APK file path to sign")
    keystore_path = click.prompt("🔐 Keystore file path")
    keystore_password = click.prompt("🔑 Keystore password", hide_input=True)
    key_alias = click.prompt("🏷️  Key alias")
    
    if not os.path.exists(apk_path):
        click.echo(click.style(f"❌ Error: APK file '{apk_path}' not found!", fg="red"))
        return
    
    if not os.path.exists(keystore_path):
        click.echo(click.style(f"❌ Error: Keystore file '{keystore_path}' not found!", fg="red"))
        return
    
    try:
        builder = Web2APKBuilder()
        signed_apk_path = builder.sign_apk(apk_path, keystore_path, keystore_password, key_alias)
        
        click.echo(click.style(f"✅ APK signed successfully!", fg="green"))
        click.echo(click.style(f"📁 Signed APK: {signed_apk_path}", fg="blue"))
        
    except Exception as e:
        click.echo(click.style(f"❌ Error signing APK: {str(e)}", fg="red"))


@click.command()
@click.option('--website', prompt='🌐 Website address', help='The website URL to convert')
@click.option('--package-name', prompt='📦 Package name', help='Android package name (e.g., com.example.myapp)')
@click.option('--app-name', prompt='📱 App name', help='Name of your Android app')
@click.option('--icon', prompt='🖼️  Icon path', help='Path to app icon (PNG format, min 512x512)')
@click.option('--output-dir', default='./build', help='Output directory for APK')
@click.option('--version', default='1.0.0', help='App version')
@click.option('--version-code', default=1, help='App version code')
@click.option('--keystore-path', help='Full path to keystore file for signing (e.g., /home/user/keystore.jks)')
@click.option('--keystore-password', help='Keystore password', hide_input=True)
@click.option('--key-alias', help='Key alias in keystore')
@click.option('--sdk-path', help='Android SDK path (auto-detected from ANDROID_HOME)')
def main(website, package_name, app_name, icon, output_dir, version, version_code,
         keystore_path, keystore_password, key_alias, sdk_path):
    """Convert websites to Android APK files with optional signing."""

    ctx = click.get_current_context()
    ctx.invoke(build, 
               website=website, 
               package_name=package_name, 
               app_name=app_name, 
               icon=icon, 
               output_dir=output_dir, 
               version=version, 
               version_code=version_code,
               keystore_path=keystore_path,
               keystore_password=keystore_password,
               key_alias=key_alias,
               sdk_path=sdk_path)

if __name__ == '__main__':
    cli()
