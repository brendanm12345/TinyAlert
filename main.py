import os
import smtplib
from email.mime.text import MIMEText
import traceback
from playwright.sync_api import Playwright, sync_playwright, expect

def run(playwright: Playwright, headless: bool = True) -> None:
    """Runs your browser workflow as a playright script and send and email if your assertion fails."""
    browser = playwright.chromium.launch(headless=headless)
    context = browser.new_context()
    page = context.new_page()
    
    try:
        ################ START BROWSER WORKFLOW HERE ###############
        # Replace with your own Playwright script that raises an
        # exception when the condition you're looking for is met.
        # The example below checks for campsite availability.
        #
        # Hint: Run `playwright codegen <your starting url>` 
        # to transcribe your browser workflow into code.
        page.goto("https://www.reservecalifornia.com/Web/")
        page.get_by_role("combobox", name="Enter to search city or park").click()
        page.get_by_role("combobox", name="Enter to search city or park").fill("pfe")
        page.get_by_role("option", name="park Pfeiffer Big Sur SP").click()
        page.get_by_text("Select Arrival - End Date").click()
        page.get_by_label("Choose Friday, March 28th,").click()
        page.get_by_label("Choose Saturday, March 29th,").click()
        page.get_by_role("button", name="— Select one").click()
        page.get_by_role("option", name="Camping", exact=True).click()
        page.get_by_role("button", name="Show Results").click()
        page.locator("a").filter(has_text="miles away0Available SitesPfeiffer Big Sur SPPfeiffer Big Sur State Park has 1,").click()
        # this assertion checks for the text "There are 0 facilities available...". If this text is not present, we get an email alert!
        expect(page.locator("#facilitysearch")).to_contain_text("There are 0 facilities available based on your search.")
        print("Target condition not met.")
        ################ END BROWSER WORKFLOW HERE ###############

    except Exception as e:
        print("Target condition met!")
        screenshot_path = "screenshots/condition_met.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        return True
    finally:
        context.close()
        browser.close()
    return False

def send_email(sender: str, recipients: list, subject: str, message: str):
    password = os.getenv("GMAIL_SMTP_APP_PASSWORD")
    if not password:
        raise ValueError("GMAIL_SMTP_APP_PASSWORD environment variable not set")

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ', '.join(recipients)

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender, password)
    server.sendmail(sender, recipients, msg.as_string())
    server.quit()
    print("Email sent successfully")

def main(sender: str, recipients: list, subject: str, message: str, headless: bool = True):
    try:
        with sync_playwright() as playwright:
            if run(playwright, headless):
                send_email(sender, recipients, subject, message)
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    sender = "sender-email"
    recipients = ["recipient-1-email"]
    subject = "🏕️ ALERT: Pfeiffer Big Sur SP campsite available! Book now!"
    message = "There is a Pfeiffer Big Sur SP campsite available! Book at https://www.reservecalifornia.com/Web/ before it's gone"
    
    main(sender, recipients, subject, message, headless=True)