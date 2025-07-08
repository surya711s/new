from  playwright.async_api import async_playwright
import asyncio

async def play():
    async with async_playwright() as s:
        browser = await s.chromium.launch(headless=False)
        pages = await browser.new_page()

        #navigation
        await pages.goto("https://www.youtube.com")
        
        await pages.wait_for_timeout(10000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(play())
            


        