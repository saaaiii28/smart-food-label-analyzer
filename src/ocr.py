import cv2
import easyocr

reader = easyocr.Reader(['en'])

def extract_text(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return "Image is too blurry"

    # Resize if small (OCR prefers larger, clearer text)
    h, w = image.shape[:2]
    if w < 1000:
        scale = 1000 / w
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Check blurriness
    fm = cv2.Laplacian(gray, cv2.CV_64F).var()
    if fm < 5.0:  # Lowered threshold slightly as Laplacian varies with scale
        return "Image is too blurry"

    # Contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    processed = clahe.apply(gray)

    # Denoising
    processed = cv2.fastNlMeansDenoising(processed, None, 10, 7, 21)

    # Use paragraph=True to join words into lines correctly
    result = reader.readtext(processed, paragraph=True, detail=0)

    text = " ".join(result)

    return text