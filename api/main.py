import os

import uvicorn
from fastapi import FastAPI

from api_info import about
from qr_api.routes import router as qrcode_router

app = FastAPI(**about)

app.include_router(qrcode_router, prefix="/qr")


@app.get("/")
async def root():
    return {"health": "ok"}


@app.get("/.well-known/acme-challenge/{filename}")
async def well_known(filename: str):
    challenge_dir = '/var/www/html/.well-known/acme-challenge'
    if filename in os.listdir(challenge_dir):
        with open(f"{challenge_dir}/{filename}", 'r') as f:
            return f.read()


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
