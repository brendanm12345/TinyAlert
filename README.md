# TinyAlert: Turn Any Browser Workflow Into an Email Alert System 🚨

Imagine this scenario: You want to go camping in Big Sur so head to https://www.reservecalifornia.com/Web/ to reserve a campsite only to find that 0 are available! You know that people cancel last minute though 😈. What if you could show a program the exact browser workflow you used to check this and it could run it in the background on a cron job and send you an email when a spot frees up! 

Meet TinyAlert: a lightweight tool that turns any browser workflow into an automated alert system in < 100 lines of code. Just record your clicks, set your schedule, and get notified when things change.

This tool is 100% AI-free 🙂

## Example
![tiny-alert](assets/tiny-alert-demo.gif)

*Note: this is an example of a browser workflow that would be run in the background. Not sped up.*

## Setup

1. Create venv, clone repository, install dependencies:
```bash
python3 -m venv venvs/tiny-alert
source venvs/tiny-alert/bin/activate
git clone https://github.com/brendanm12345/TinyAlert
cd TinyAlert
pip install -r requirements.txt
```

2. Install Playwright Browsers:
```bash
python -m playwright install
```

3. Configure Gmail:
- Generate an App Password: Google Account > Security > 2-Step Verification > App Passwords
- Set environment variable:
```bash
export GMAIL_SMTP_APP_PASSWORD='your-app-password'
```

4. Head over to [workflows/README.md](workflows/README.md) to to record your own browser workflow.
- *Note: You can also skip this step and run the demo with the example campsite checker workflow.*

5. Customize `main.py`
- Paste the playwright code for your browser workflow
- Update the email sender/recipient/message/subject information

6. Grant Required Permissions:
- Open System Settings > Privacy & Security > Full Disk Access
- Click + and add:
  - `/usr/sbin/cron`
  - `/bin/bash` (use Cmd+Shift+G to navigate)
 
7. Run setup (your cron job will be active after this):
```bash
python3 setup.py
```

## Testing

1. Verify that the cron job is active:
```bash
crontab -l  
```
You should see an output like `17,21,11 * * * /Users/...`.

2. Execute the run script manually to werify that when the cron job triggers, it will work:
```bash
./run-checker.sh
```
If this runs successfully and checks the website, your automated checks will work.

## Scheduling

By default, checks run at 11:00 AM 5:00 PM, and 9:00 PM. To modify:
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
cat ~/Library/Logs/tiny-alert.log
```
Each time your cron job triggers, you should see some output in these logs detailing what went wrong.

If script isn't running:
1. Verify permissions (steps above)
2. Ensure Mac power settings allow wake from sleep
3. Ask your favorite frontier model
4. Add GitHub issues :)

## License
MIT
