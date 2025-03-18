import os
import shutil
import subprocess
from pathlib import Path

# Alert schedule - add or remove times as needed!
ALERT_TIMES = [
    {"hour": 11, "minute": 0},  # 11:00 AM
    {"hour": 17, "minute": 0},  # 5:00 PM
    {"hour": 21, "minute": 0},  # 9:00 PM
    # Add more times here in the same format
    # {"hour": 14, "minute": 30},  # 2:30 PM
]

def setup_environment():
    """Set up environment file with necessary credentials and settings."""
    env_file = Path(".env")
    env_contents = []
    
    # Get Python interpreter path
    try:
        python_path = subprocess.check_output(['which', 'python3'], text=True).strip()
        print(f"Found Python interpreter: {python_path}")
    except subprocess.CalledProcessError:
        print("⚠️  Could not automatically detect Python path")
        python_path = input("Please enter path to Python interpreter: ").strip() or "/usr/bin/python3"
    
    env_contents.append(f'PYTHON_PATH="{python_path}"')
    
    # Check if GMAIL_SMTP_APP_PASSWORD is already set
    gmail_pass = os.getenv("GMAIL_SMTP_APP_PASSWORD")
    if not gmail_pass:
        print("\n⚠️  GMAIL_SMTP_APP_PASSWORD not found in environment")
        gmail_pass = input("Please enter your Gmail App Password: ").strip()
    
    env_contents.append(f'GMAIL_SMTP_APP_PASSWORD="{gmail_pass}"')
    
    # Write to .env file
    with open(env_file, 'w') as f:
        f.write('\n'.join(env_contents) + '\n')
    
    # Set restrictive permissions (only owner can read/write)
    env_file.chmod(0o600)
    print("✅ Environment file created with secure permissions")
    return env_file

def create_plist():
    """Create the launch agent plist file."""
    plist_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.wakeschedule</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/caffeinate</string>
        <string>-i</string>
        <string>-t</string>
        <string>300</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>'''
    
    # add each alert time to the plist
    for time in ALERT_TIMES:
        plist_content += f'''
        <dict>
            <key>Hour</key>
            <integer>{time["hour"]}</integer>
            <key>Minute</key>
            <integer>{time["minute"]}</integer>
        </dict>'''
    
    plist_content += '''
    </array>
</dict>
</plist>'''
    
    resources_dir = Path("resources")
    resources_dir.mkdir(exist_ok=True)
    
    plist_path = resources_dir / "com.user.wakeschedule.plist"
    with open(plist_path, 'w') as f:
        f.write(plist_content)
    
    return plist_path

def setup_launch_agent():
    """Set up the launch agent for scheduled wake."""
    launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
    launch_agents_dir.mkdir(parents=True, exist_ok=True)
    
    # Create plist file
    plist_source = create_plist()
    plist_dest = launch_agents_dir / "com.user.wakeschedule.plist"
    shutil.copy2(plist_source, plist_dest)
    
    # Set perms
    plist_dest.chmod(0o644)
    
    # Load the launch agent
    try:
        subprocess.run(["launchctl", "unload", str(plist_dest)], capture_output=True)
        subprocess.run(["launchctl", "load", str(plist_dest)], check=True)
        print("✅ Launch agent installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error loading launch agent: {e}")

def setup_cron():
    """Set up the cron jobs."""
    script_path = Path.cwd() / "run-checker.sh"
    
    # Create cron schedule string
    minutes = [str(t['minute']) for t in ALERT_TIMES]
    hours = [str(t['hour']) for t in ALERT_TIMES]
    
    minute_str = ','.join(set(minutes))  # Use set to remove duplicates
    hour_str = ','.join(set(hours))      # Use set to remove duplicates
    
    cron_command = f'{minute_str} {hour_str} * * * {script_path.absolute()} >> ~/Library/Logs/tiny-alert.log 2>&1'
    print(f"Setting up cron schedule: '{minute_str} {hour_str} * * *'")
    
    try:
        # Get existing crontab
        existing = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        crontab = existing.stdout if existing.returncode == 0 else ""
        
        # Ensure crontab ends with newline
        if crontab and not crontab.endswith('\n'):
            crontab += '\n'
        
        # Add our job if it's not already there
        if script_path.name not in crontab:  # Check for script name instead of exact command
            with open("temp_cron", "w") as f:
                f.write(crontab + cron_command + "\n")
            
            # Verify the temp file
            with open("temp_cron", "r") as f:
                print("New crontab contents:")
                print(f.read())
            
            subprocess.run(["crontab", "temp_cron"], check=True)
            os.remove("temp_cron")
            print("✅ Cron jobs installed successfully")
        else:
            print("✅ Cron jobs already installed")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error setting up cron jobs: {e}")

def setup_logs():
    """Set up logging directory."""
    log_dir = Path.home() / "Library" / "Logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "tiny-alert.log"
    if log_file.exists():
        log_file.unlink()
    
    log_file.touch()
    print("✅ Log file created at", log_file)

def check_dependencies():
    """Verify Python installation and basic requirements."""
    try:
        subprocess.run(["python3", "--version"], check=True)
        print("✅ Python 3 is installed")
    except subprocess.CalledProcessError:
        print("⚠️  Python 3 is not installed")
        exit(1)

def main():
    """Run the complete setup process."""
    print("Setting up Tiny Alert...")
    
    os.makedirs("screenshots", exist_ok=True)
    check_dependencies()
    setup_environment()
    
    Path("run-checker.sh").chmod(0o755)
    
    setup_launch_agent()
    setup_cron()
    setup_logs()
    
    print("\n✨ Setup complete! TinyAlert will run at the following times:")
    for time in ALERT_TIMES:
        print(f"   - {time['hour']:02d}:{time['minute']:02d}")

if __name__ == "__main__":
    main()