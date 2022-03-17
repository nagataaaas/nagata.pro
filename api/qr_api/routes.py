from io import BytesIO
from urllib.parse import unquote_plus

from PIL import Image
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from .qr import chrome_style_qrcode, instagram_style_qrcode
from .scheme import QRCodeRequest

router = APIRouter(
    tags=["qrcode"],
    responses={404: {"description": "Not found"}},
)


@router.post("/chrome")
async def qr_chrome(req: QRCodeRequest):
    return create_streaming_response(chrome_style_qrcode(unquote_plus(req.text)))


@router.post("/instagram")
async def qr_instagram(req: QRCodeRequest):
    return create_streaming_response(instagram_style_qrcode(unquote_plus(req.text)))


def create_streaming_response(image: Image) -> StreamingResponse:
    image_io = BytesIO()
    image.save(image_io, "PNG")
    image_io.seek(0)
    return StreamingResponse(image_io, media_type="image/png")
