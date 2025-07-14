import asyncio
from playwright.async_api import async_playwright, Frame, Locator
from typing import Union, List, Tuple # Import Union, List, and Tuple

async def find_canvas_in_frames(frames: List[Frame]) -> Union[Tuple[Frame, Locator], None]:
    """
    Recursively searches for a 'canvas' element within a list of Frame objects and their children.

    Args:
        frames (List[Frame]): A list of Playwright Frame objects to search within.

    Returns:
        Union[Tuple[Frame, Locator], None]: A tuple containing the Frame and the
                                            found canvas Locator, or None if no canvas is found.
    """
    for frame in frames:
        try:
            # Playwright uses locators for element selection. .first ensures we get the first one.
            canvas = frame.locator("canvas").first
            if await canvas.is_visible(): # Check if the canvas element exists and is visible
                return frame, canvas
        except Exception:
            # Ignore inaccessible frames or elements not found (e.g., frame not fully loaded)
            pass

        # Recursively search in child frames (Frame objects have child_frames())
        child_frames = frame.child_frames
        if child_frames: # child_frames is a property, not a method, so no parentheses needed
            result = await find_canvas_in_frames(child_frames)
            if result:
                return result
    return None

async def main():
    """
    Main asynchronous function to launch the browser, navigate, interact with a canvas,
    take screenshots, and close the browser.
    """
    async with async_playwright() as p:
        # Launch Chromium browser in non-headless mode with no default viewport
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Navigate to the URL and wait until the network is idle
        print("Navigating to URL...")
        await page.goto(
            "https://cdn-3.launcher.a8r.games/index.html?fullscreen=false&options=eyJsYXVuY2hfb3B0aW9ucyI6eyJnYW1lX3VybCI6Imh0dHBzOi8vZ3Byb3V0ZXIuZ3Jvb3ZlZ2FtaW5nLmNvbS9nYW1lP2FjY291bnRpZD1cdTAwMjZjb3VudHJ5PVx1MDAyNmRldmljZV90eXBlPWRlc2t0b3BcdTAwMjZob21ldXJsPWh0dHBzJTNBJTJGJTJGbmF0Y2FzaW5mby5jb20lMkZlbiUyRmNhc2lubyUyRmdhbWUlMkZleGl0XHUwMDI2aXNfdGVzdF9hY2NvdW50PWZhbHNlXHUwMDI2bGljZW5zZT1DdXJhY2FvXHUwMDI2bm9nc2N1cnJlbmN5PUVVUlx1MDAyNm5vZ3NnYW1laWQ9ODIxMDAyNTZcdTAwMjZub2dzbGFuZz1lbl9VU1x1MDAyNm5vZ3Ntb2RlPWRlbW9cdTAwMjZub2dzb3BlcmF0b3JpZD0zMTkxXHUwMDI2c2Vzc2lvbmlkPWNiMjNiMzUyLTU1MWYtNDhjYy05MTc3LTQ5NzZiYzhkZDI4YiIsInN0cmF0ZWd5IjoiaWZyYW1lIn0sImxhdW5jaGVyX3ZlcnNpb24iOiJtYXN0ZXIiLCJsb2JieV90b2tlbiI6IjFmY2I1MmRiLTJmNTAtNGZmMC05YmI4LWE5Zjg2ODAifQ%3D%3D",
            wait_until="networkidle",
            timeout=0 # No timeout
        )

        print("Waiting for game to fully load (20 seconds)...")
        await asyncio.sleep(20) # wait for game to fully load

        # Get all Frame objects on the page and find the canvas within them
        all_frames = page.frames # page.frames returns a list of Frame objects
        result = await find_canvas_in_frames(all_frames)

        if not result:
            print("❌ No canvas found in any frame.")
            await browser.close()
            return

        frame, canvas = result

        print(f"✅ Canvas found in frame: {frame.url}")

        # Take a screenshot of the canvas before clicks
        await canvas.screenshot(path="canvas_before_clicks.png")
        print("📸 Screenshot saved as canvas_before_clicks.png")

        # First click coordinates
        first_click_x = 550
        first_click_y = 468

        # Click on the page at the specified coordinates
        await page.mouse.click(first_click_x, first_click_y)
        print(f"🎯 Clicked canvas at ({first_click_x}, {first_click_y})")

        print("Waiting for 3 seconds...")
        await asyncio.sleep(3) # wait 3 seconds

        # Get canvas bounding box again to calculate bottom center for Play button click
        box = await canvas.bounding_box()
        if not box:
            print("⚠️ Unable to get bounding box of canvas for second click.")
            await browser.close()
            return

        # Calculate coordinates for the second click (bottom center of the canvas, 20px up)
        second_click_x = box["x"] + box["width"] / 2
        second_click_y = box["y"] + box["height"] - 20

        # Click the "Play" button area
        await page.mouse.click(second_click_x, second_click_y)
        print(f"🎯 Clicked Play button at ({second_click_x:.1f}, {second_click_y:.1f})")

        print("Waiting for 5 seconds for game to start/render...")
        await asyncio.sleep(5) # wait 5 seconds for game to start/render

        # Final screenshot after clicks
        await canvas.screenshot(path="canvas_after_clicks.png")
        print("📸 Screenshot saved as canvas_after_clicks.png")

        await browser.close()
        print("Browser closed.")

if __name__ == "__main__":
    asyncio.run(main())
