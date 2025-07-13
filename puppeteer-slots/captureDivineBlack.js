const puppeteer = require("puppeteer");

function delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

async function findCanvasInFrames(frames) {
    for (const frame of frames) {
        try {
            const canvas = await frame.$("canvas");
            if (canvas) {
                return { frame, canvas };
            }
        } catch {
            // ignore inaccessible frames
        }
        const childFrames = frame.childFrames();
        if (childFrames.length) {
            const result = await findCanvasInFrames(childFrames);
            if (result) return result;
        }
    }
    return null;
}

(async () => {
    const browser = await puppeteer.launch({ headless: false, defaultViewport: null });
    const page = await browser.newPage();

    await page.goto(
        "https://cdn-3.launcher.a8r.games/index.html?fullscreen=false&options=eyJsYXVuY2hfb3B0aW9ucyI6eyJnYW1lX3VybCI6Imh0dHBzOi8vZ3Byb3V0ZXIuZ3Jvb3ZlZ2FtaW5nLmNvbS9nYW1lP2FjY291bnRpZD1cdTAwMjZjb3VudHJ5PVx1MDAyNmRldmljZV90eXBlPWRlc2t0b3BcdTAwMjZob21ldXJsPWh0dHBzJTNBJTJGJTJGbmF0Y2FzaW5mby5jb20lMkZlbiUyRmNhc2lubyUyRmdhbWUlMkZleGl0XHUwMDI2aXNfdGVzdF9hY2NvdW50PWZhbHNlXHUwMDI2bGljZW5zZT1DdXJhY2FvXHUwMDI2bm9nc2N1cnJlbmN5PUVVUlx1MDAyNm5vZ3NnYW1laWQ9ODIxMDAyNTZcdTAwMjZub2dzbGFuZz1lbl9VU1x1MDAyNm5vZ3Ntb2RlPWRlbW9cdTAwMjZub2dzb3BlcmF0b3JpZD0zMTkxXHUwMDI2c2Vzc2lvbmlkPWNiMjNiMzUyLTU1MWYtNDhjYy05MTc3LTQ5NzZiYzhkZDI4YiIsInN0cmF0ZWd5IjoiaWZyYW1lIn0sImxhdW5jaGVyX3ZlcnNpb24iOiJtYXN0ZXIiLCJsb2JieV90b2tlbiI6IjFmY2I1MmRiLTJmNTAtNGZmMC05YmI4LWE5Zjg2ODAifQ%3D%3D",
        { waitUntil: "networkidle2", timeout: 0 },
    );

    await delay(20000); // wait for game to fully load

    const result = await findCanvasInFrames(page.frames());

    if (!result) {
        console.log("❌ No canvas found in any frame.");
        await browser.close();
        return;
    }

    const { frame, canvas } = result;

    console.log("✅ Canvas found in frame:", frame.url());

    await canvas.screenshot({ path: "canvas_before_clicks.png" });
    console.log("📸 Screenshot saved as canvas_before_clicks.png");

    // First click coords
    const firstClickX = 550;
    const firstClickY = 468;

    await page.mouse.click(firstClickX, firstClickY);
    console.log(`🎯 Clicked canvas at (${firstClickX}, ${firstClickY})`);

    await delay(3000); // wait 3 seconds

    // Get canvas bounding box again to calculate bottom center for Play button click
    const box = await canvas.boundingBox();
    if (!box) {
        console.log("⚠️ Unable to get bounding box of canvas for second click.");
        await browser.close();
        return;
    }

    const secondClickX = box.x + box.width / 2;
    const secondClickY = box.y + box.height - 20; // 20 px above bottom edge

    await page.mouse.click(secondClickX, secondClickY);
    console.log(`🎯 Clicked Play button at (${secondClickX.toFixed(1)}, ${secondClickY.toFixed(1)})`);

    await delay(5000); // wait 5 seconds for game to start/render

    // Final screenshot after clicks
    await canvas.screenshot({ path: "canvas_after_clicks.png" });
    console.log("📸 Screenshot saved as canvas_after_clicks.png");

    await browser.close();
})();

// const puppeteer = require("puppeteer");

// function delay(ms) {
//     return new Promise((resolve) => setTimeout(resolve, ms));
// }

// async function findCanvasInFrames(frames) {
//     for (const frame of frames) {
//         try {
//             const canvas = await frame.$("canvas");
//             if (canvas) {
//                 return { frame, canvas };
//             }
//         } catch {
//             // ignore inaccessible frames
//         }
//         const childFrames = frame.childFrames();
//         if (childFrames.length) {
//             const result = await findCanvasInFrames(childFrames);
//             if (result) return result;
//         }
//     }
//     return null;
// }

// (async () => {
//     const browser = await puppeteer.launch({ headless: false, defaultViewport: null });
//     const page = await browser.newPage();

//     await page.goto(
//         "https://cdn-3.launcher.a8r.games/index.html?fullscreen=false&options=eyJsYXVuY2hfb3B0aW9ucyI6eyJnYW1lX3VybCI6Imh0dHBzOi8vZ3Byb3V0ZXIuZ3Jvb3ZlZ2FtaW5nLmNvbS9nYW1lP2FjY291bnRpZD1cdTAwMjZjb3VudHJ5PVx1MDAyNmRldmljZV90eXBlPWRlc2t0b3BcdTAwMjZob21ldXJsPWh0dHBzJTNBJTJGJTJGbmF0Y2FzaW5mby5jb20lMkZlbiUyRmNhc2lubyUyRmdhbWUlMkZleGl0XHUwMDI2aXNfdGVzdF9hY2NvdW50PWZhbHNlXHUwMDI2bGljZW5zZT1DdXJhY2FvXHUwMDI2bm9nc2N1cnJlbmN5PUVVUlx1MDAyNm5vZ3NnYW1laWQ9ODIxMDAyNTZcdTAwMjZub2dzbGFuZz1lbl9VU1x1MDAyNm5vZ3Ntb2RlPWRlbW9cdTAwMjZub2dzb3BlcmF0b3JpZD0zMTkxXHUwMDI2c2Vzc2lvbmlkPWNiMjNiMzUyLTU1MWYtNDhjYy05MTc3LTQ5NzZiYzhkZDI4YiIsInN0cmF0ZWd5IjoiaWZyYW1lIn0sImxhdW5jaGVyX3ZlcnNpb24iOiJtYXN0ZXIiLCJsb2JieV90b2tlbiI6IjFmY2I1MmRiLTJmNTAtNGZmMC05YmI4LWE5Zjg2ODAifQ%3D%3D",
//         { waitUntil: "networkidle2", timeout: 0 }
//     );

//     await delay(10000); // wait for game to fully load

//     const result = await findCanvasInFrames(page.frames());

//     if (!result) {
//         console.log("❌ No canvas found in any frame.");
//         await browser.close();
//         return;
//     }

//     const { frame, canvas } = result;

//     console.log("✅ Canvas found in frame:", frame.url());

//     await canvas.screenshot({ path: "canvas.png" });
//     console.log("📸 Screenshot saved as canvas.png");

//     const box = await canvas.boundingBox();
//     if (!box) {
//         console.log("⚠️ Unable to get bounding box of canvas.");
//         await browser.close();
//         return;
//     }

//     const centerX = box.x + box.width / 2;
//     const centerY = box.y + box.height / 2;

//     // Click offsets around center (px)
//     const clickOffsets = [
//         [0, 0],
//         [-50, 0],
//         [50, 0],
//         [0, -50],
//         [0, 50],
//         [-50, -50],
//         [50, -50],
//         [-50, 50],
//         [50, 50],
//     ];

//     for (const [dx, dy] of clickOffsets) {
//         const clickX = centerX + dx;
//         const clickY = centerY + dy;
//         await page.mouse.click(clickX, clickY);
//         console.log(`🎯 Clicked canvas at (${clickX.toFixed(1)}, ${clickY.toFixed(1)})`);
//         await delay(1500); // wait 1.5 seconds between clicks
//     }

//     await delay(5000); // wait a bit after clicks for any reaction

//     await browser.close();
// })();
