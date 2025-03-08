import cv2
import numpy as np
import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import argparse
from tqdm import tqdm

def correct_angle(image, verbose=False):
    # Convert to grayscale if necessary
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image

    # Apply preprocessing to improve text detection
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    try:
        return _extracted_from_correct_angle_(gray, verbose, image)
    except Exception as e:
        if verbose:
            print(f"Error in orientation detection: {str(e)}")
        # Fallback to the original method if tesseract fails
        return fallback_correct_angle(image, verbose)


# TODO Rename this here and in `correct_angle`
def _extracted_from_correct_angle_(gray, verbose, image):
    # Use pytesseract's OSD (Orientation and Script Detection) to detect rotation
    osd = pytesseract.image_to_osd(gray)
    angle = int(osd.splitlines()[1].split(':')[1].strip())

    if verbose:
        print(f"Detected orientation: {angle}°")

    # If the page is correctly oriented (0° or minor angle)
    if angle == 0:
        return image

    # Rotate the image to correct orientation
    h, w = image.shape[:2]
    center = (w // 2, h // 2)

    # Get rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    # Calculate new image dimensions
    cos = np.abs(rotation_matrix[0, 0])
    sin = np.abs(rotation_matrix[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    # Adjust matrix
    rotation_matrix[0, 2] += (new_w / 2) - center[0]
    rotation_matrix[1, 2] += (new_h / 2) - center[1]

    return cv2.warpAffine(
        image, rotation_matrix, (new_w, new_h), borderValue=(255, 255, 255)
    )

def fallback_correct_angle(image, verbose=False):
    """Fallback to traditional approach when pytesseract fails"""
    if verbose:
        print("Using fallback orientation correction method")

    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    try:
        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) < 100:
            if verbose:
                print("Not enough text detected, skipping rotation")
            return image

        rect = cv2.minAreaRect(coords)
        angle = rect[-1]

        # Adjust angle based on orientation
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        if abs(angle) < 0.5:
            return image

        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

        cos = np.abs(matrix[0, 0])
        sin = np.abs(matrix[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))

        matrix[0, 2] += (new_w / 2) - center[0]
        matrix[1, 2] += (new_h / 2) - center[1]

        return cv2.warpAffine(image, matrix, (new_w, new_h), borderValue=(255, 255, 255))
    except Exception as e:
        if verbose:
            print(f"Fallback method also failed: {str(e)}")
        return image

def correct_pdf_orientation(input_pdf, output_pdf, dpi=200, verbose=False):
    """
    Correct the orientation of all pages in a PDF file
    """
    print(f"Converting {input_pdf} to images...")
    images = convert_from_path(input_pdf, dpi=dpi)

    print(f"Correcting orientation of {len(images)} pages...")
    corrected_images = []
    for i, img in enumerate(tqdm(images)):
        if verbose:
            print(f"\nProcessing page {i+1}/{len(images)}")
        # Convert PIL Image to numpy array for OpenCV
        img_array = np.array(img)
        # Correct the orientation
        corrected = correct_angle(img_array, verbose)
        # Convert back to PIL Image
        corrected_pil = Image.fromarray(corrected)
        corrected_images.append(corrected_pil)

    print(f"Saving corrected PDF to {output_pdf}...")
    # Save the first image
    corrected_images[0].save(
            output_pdf,
            save_all=True,
            append_images=corrected_images[1:],
            resolution=dpi,
            format="PDF"
    )
    print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Correct orientation of all pages in a PDF file')
    parser.add_argument('input_pdf', help='Path to the input PDF file')
    parser.add_argument('--output_pdf', help='Path to save the corrected PDF file')
    parser.add_argument('--dpi', type=int, default=200, help='DPI for PDF conversion')
    parser.add_argument('--verbose', action='store_true', help='Show detailed processing information')
    args = parser.parse_args()

    # If output_pdf is not specified, use input_pdf with "_corrected" suffix
    if not args.output_pdf:
        filename, ext = os.path.splitext(args.input_pdf)
        args.output_pdf = f"{filename}_corrected{ext}"

    correct_pdf_orientation(args.input_pdf, args.output_pdf, args.dpi, args.verbose)