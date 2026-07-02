from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import aiohttp
from pathlib import Path

app = FastAPI()

# تنظیمات
TELEGRAM_BOT_TOKEN = "8316342765:AAGweEHWcSUHXDVp-4oi-lFZvZrryvooOVc"
CHAT_ID = 8019629674
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

# سرو کردن فایل‌های static (HTML)
static_dir = Path(__file__).parent
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

@app.post("/upload")
async def upload_image(image: UploadFile = File(...), prize: str = Form(None)):
    try:
        # خواندن عکس
        image_data = await image.read()
        
        # متن پیام (جایزه برنده)
        caption = f"🎉 برنده: {prize} تومان!" if prize else "🎉 برنده شد!"
        
        # ارسال به تلگرام
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('chat_id', str(CHAT_ID))
            data.add_field('photo', image_data, filename='winner.jpg')
            data.add_field('caption', caption)
            data.add_field('parse_mode', 'HTML')
            
            async with session.post(TELEGRAM_API_URL, data=data) as resp:
                result = await resp.json()
                
                if result.get('ok'):
                    return JSONResponse({
                        "success": True,
                        "message": "عکس برنده‌ای برای بات ارسال شد"
                    })
                else:
                    return JSONResponse({
                        "success": False,
                        "error": result.get('description', 'خطای تلگرام')
                    }, status_code=400)
                    
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
