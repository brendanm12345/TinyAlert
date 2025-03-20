# Recording Browser Workflows

This guide explains how to record and customize browser workflows for TinyAlert.

## Recording a New Workflow

1. Start the Playwright recorder:
```bash
playwright codegen --save-storage=auth.json --output workflow.py <your-starting-url>
```

2. Perform your workflow in the browser that opens. Playwright will record your actions.

3. When finished, the code will be saved to `workflow.py`.

## Customizing the Workflow

### Adding Assertions

The key to making TinyAlert work is adding an assertion that will fail when your target condition is met. Here are some common patterns:

1. Text-based assertions:
```python
# Alert when text appears
expect(page.locator(".status")).not_to_contain_text("Sold Out")

# Alert when text disappears
expect(page.locator(".status")).to_contain_text("Sold Out")
```

2. Element-based assertions:
```python
# Alert when element appears
expect(page.locator(".available-item")).to_be_visible()

# Alert when element count changes
expect(page.locator(".item-card")).to_have_count(0)
```

### Using Saved Authentication

If your workflow requires login, you can:

1. Record the workflow with `--save-storage`:
```bash
playwright codegen --save-storage=auth.json <url>
```
You can also load a save storage state using the `--load-storage=auth.json` flag to avoid redoing login workflows.

2. Later runs will use the saved auth:
```python
context = browser.new_context(storage_state="auth.json")
```

## Tips and Tricks

- Use `page.wait_for_timeout(1000)` if pages need extra time to load
- Add error handling for expected conditions
- Test your workflow both with and without headless mode
- Regular `playwright codegen` output might need cleanup
- Consider adding retry logic for flaky elements

## Example Workflow

Here's a complete example that checks for concert tickets:

```python
def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    
    # Load saved auth if available
    context_options = {}
    if os.path.exists("auth.json"):
        context_options["storage_state"] = "auth.json"
    
    context = browser.new_context(**context_options)
    page = context.new_page()
    
    try:
        # Navigate to ticket page
        page.goto("https://ticketing-site.com/event")
        
        # Wait for content to load
        page.wait_for_selector(".ticket-status")
        
        # This will raise an exception when tickets are available
        expect(page.locator(".ticket-status")).to_contain_text("Sold Out")
        
    except Exception as e:
        print("Tickets found!")
        page.screenshot(path="tickets.png")
        return True
    finally:
        context.close()
        browser.close()
    return False
```