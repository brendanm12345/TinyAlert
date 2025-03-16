# TinyAlert: Email Alerts From Browser Workflows

Imagine this scenario. You want to go camping in Big Sur, but you check and 0 campsites are available! You know that people cancel last minute though 😈. What if you could show a program the exact browser workflow you used to check this and it could run it in the background on a cron job and send you an email when a spot frees up! Meet TinyAlert. Warning this tool does NOT use AI 🙂

## Example
![tiny-alert](https://github.com/user-attachments/assets/7e51cdf3-9546-4b99-9159-e8314546fef0)

*Note: this is an example of what would be running in the background. Not sped up.*
## Setup

1. Clone the repository and install dependencies:
```bash
git clone [https://github.com/brendanm12345/TinyAlert]
cd tiny-alert
pip install -r requirements.txt
```

2. Configure Gmail:
- Generate an App Password: Google Account > Security > 2-Step Verification > App Passwords
- Set environment variable:
```bash
export GMAIL_SMTP_APP_PASSWORD='your-app-password'
```

3. Record a browser workflow
- You can easily do this using Playwright Codegen. Please defer to the [docs](https://playwright.dev/python/docs/codegen) for instructions

4. Customize `main.py`
- Paste the playwright code for your browser workflow
- Update the email sender/recipient/message/subject information

5. Grant Required Permissions:
- Open System Settings > Privacy & Security > Full Disk Access
- Click + and add:
  - `/usr/sbin/cron`
  - `/bin/bash` (use Cmd+Shift+G to navigate)
 
6. Run setup (your cron job will be active after this):
```bash
python3 setup.py
```

## Testing

Before leaving it to run automatically, test the script:
```bash
./run-checker.sh
```
If this runs successfully and checks the website, your automated checks will work.

## Scheduling

By default, checks run at 10:00 AM and 4:00 PM. To modify:
1. Edit times in `setup.py`
2. Run `python3 setup.py` again

## Stopping the Checker
To stop all automated checks:
```bash
# remove cron jobs
crontab -l | grep -v "run-checker.sh" | crontab -

# unload launch agent
launchctl unload ~/Library/LaunchAgents/com.user.wakeschedule.plist
```

## Troubleshooting

Check logs for errors:
```bash
cat ~/Library/Logs/website-checker.log
```

If script isn't running:
1. Verify permissions (steps above)
2. Ensure Mac power settings allow wake from sleep
3. Ask your favorite frontier model

## License
MIT
