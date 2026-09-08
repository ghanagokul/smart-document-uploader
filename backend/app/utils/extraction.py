import io
import boto3
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
from app.utils.s3 import BUCKET_NAME as S3_BUCKET

s3_client = boto3.client("s3")


def extract_text(s3_key: str) -> str:
    obj = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
    file_bytes = obj["Body"].read()

    if s3_key.lower().endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")

    if s3_key.lower().endswith(".pdf"):
        pages = convert_from_bytes(file_bytes)
        text_parts = [pytesseract.image_to_string(page) for page in pages]
        return "\n".join(text_parts)

    # png/jpg/jpeg etc.
    image = Image.open(io.BytesIO(file_bytes))
    return pytesseract.image_to_string(image)