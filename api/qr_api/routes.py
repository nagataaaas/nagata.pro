from io import BytesIO
from urllib.parse import unquote_plus

from PIL import Image
from fastapi import APIRouter
from fastapi.responses import Response

from .qr import chrome_style_qrcode, instagram_style_qrcode

router = APIRouter(
    tags=["qrcode"],
    responses={404: {"description": "Not found"}},
)


@router.get("/chrome", response_class=Response)
async def qr_chrome(text: str):
    return create_streaming_response(chrome_style_qrcode(unquote_plus(text)))


@router.get("/instagram", response_class=Response)
async def qr_instagram(text: str):
    return create_streaming_response(instagram_style_qrcode(unquote_plus(text)))


def create_streaming_response(image: Image) -> Response:
    image_io = BytesIO()
    image.save(image_io, format="PNG")
    image_io.seek(0)
    return Response(image_io.getvalue(), media_type="image/png")
