import os
import shutil
import subprocess
from pathlib import Path

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
    <array>
        <dict>
            <key>Hour</key>
            <integer>10</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>16</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>
</dict>
</plist>'''
    
    resources_dir = Path("resources")
    resources_dir.mkdir(exist_ok=True)
    
    plist_path = resources_dir / "com.user.wakeschedule.plist"
    with open(plist_path, 'w') as f:
        f.write(plist_content)
    
    return plist_path

def create_run_checker():
    """Create the run-checker.sh script."""
    script_content = '''#!/bin/bash

# Wait for network connectivity
wait_for_network() {
    while ! ping -c 1 google.com &> /dev/null; do
        echo "Waiting for network connection..."
        sleep 5
    done
}

# Path to your Python script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure we have network before running
wait_for_network

# Run the campsite checker
python3 main.py

'''
    
    script_path = Path("run-checker.sh")
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    return script_path

def setup_launch_agent():
    """Set up the launch agent for scheduled wake."""
    launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
    launch_agents_dir.mkdir(parents=True, exist_ok=True)
    
    # Create plist file
    plist_source = create_plist()
    plist_dest = launch_agents_dir / "com.user.wakeschedule.plist"
    shutil.copy2(plist_source, plist_dest)
    
    # Set correct permissions
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
    cron_command = f'0 10,16 * * * {script_path} >> ~/Library/Logs/website-checker.log 2>&1'
    
    try:
        # Get existing crontab
        existing = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        crontab = existing.stdout if existing.returncode == 0 else ""
        
        # Add our job if it's not already there
        if cron_command not in crontab:
            with open("temp_cron", "w") as f:
                f.write(crontab + cron_command + "\n")
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
    
    log_file = log_dir / "website-checker.log"
    log_file.touch()
    print("✅ Log file created at", log_file)

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        subprocess.run(["python3", "-c", "import playwright"], check=True)
    except subprocess.CalledProcessError:
        print("Installing playwright...")
        subprocess.run(["pip3", "install", "playwright"], check=True)
        subprocess.run(["playwright", "install"], check=True)
    print("✅ Dependencies verified")

def main():
    """Run the complete setup process."""
    print("Setting up Website Checker...")
    
    # Create necessary directories
    os.makedirs("screenshots", exist_ok=True)
    
    # Create run-checker script
    run_checker_path = create_run_checker()
    run_checker_path.chmod(0o755)
    
    # Run setup steps
    check_dependencies()
    setup_launch_agent()
    setup_cron()
    setup_logs()
    
    print("\n✨ Setup complete! TinyAlert will run on the specified cron job")

if __name__ == "__main__":
    main()