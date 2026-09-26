import asyncio
from playwright.async_api import async_playwright

async def run_job_bot(role, location, email, password, resume_link=None):
    print(f"[*] Initializing bot for {role} in {location}...")
    
    async with async_playwright() as p:
        # headless=False so you can see if a Captcha pops up during testing
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # 1. Navigate directly to the login page
            print("[*] Navigating to LinkedIn login...")
            await page.goto("https://www.linkedin.com/login")

            # 2. Type the credentials
            print("[*] Entering credentials...")
            await page.fill("input#username", email)
            await page.fill("input#password", password)
            
            # 3. Click the Sign In button
            await page.click("button[type='submit']")
            await page.wait_for_load_state('networkidle')
            
            # 4. Check for security checkpoints
            if "checkpoint" in page.url or "challenge" in page.url:
                print("[-] Security check triggered! You have 30 seconds to solve the puzzle on screen.")
                await asyncio.sleep(30)
            
            # 5. Proceed to job search
            print("[+] Login complete! Navigating to job search...")
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={role}&location={location}"
            await page.goto(search_url)

            await asyncio.sleep(5) # Simulating execution time
            return True

        except Exception as e:
            print(f"[-] Bot crashed during execution: {e}")
            return False
            
        finally:
            await context.close()
            await browser.close()
            print("[*] Playwright session closed.")

# Local testing block
if __name__ == "__main__":
    # Test this locally by pasting your actual email and password here
    asyncio.run(run_job_bot("Civil Engineer", "Dubai", "YOUR_EMAIL", "YOUR_PASSWORD"))