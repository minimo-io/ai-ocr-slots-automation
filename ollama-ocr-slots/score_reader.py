import torch

# Monkey patch torch.load to enforce weights_only=True for security and silence warning
_original_torch_load = torch.load

def torch_load_weights_only(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = True
    return _original_torch_load(*args, **kwargs)

torch.load = torch_load_weights_only

import os
import re
import cv2
import easyocr

def read_game_score_custom_crop(image_path):
    """
    Crops a specific region of the image where the game score is expected to be
    and uses EasyOCR to read the score, handling decimal points.

    Args:
        image_path (str): The file path to the game screenshot image (e.g., 'game_screenshot.png').

    Returns:
        str: The extracted score as a string (e.g., '1000.00'), or an error message
             if the image is not found, invalid, or no suitable score is detected.
    """
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return None

    cv_image_original = cv2.imread(image_path)
    if cv_image_original is None:
        print(f"Error: Could not load image with OpenCV at {image_path}. Check file path and integrity.")
        return None

    h, w, _ = cv_image_original.shape
    print(f"Original image dimensions: Width={w}, Height={h}")

    x1_crop = 0
    x2_crop = int(w * 0.5)
    y1_crop = int(h * 0.1)
    y2_crop = int(h * 0.9)

    print(f"Cropping image to region: (x1={x1_crop}, y1={y1_crop}, x2={x2_crop}, y2={y2_crop})")

    x1_crop = max(0, x1_crop)
    y1_crop = max(0, y1_crop)
    x2_crop = min(w, x2_crop)
    y2_crop = min(h, y2_crop)

    if x1_crop >= x2_crop or y1_crop >= y2_crop:
        print("Warning: Custom crop region results in an empty or invalid image. Adjust crop coordinates carefully.")
        return "Invalid custom crop region."

    cropped_image = cv_image_original[y1_crop:y2_crop, x1_crop:x2_crop]

    if cropped_image.shape[0] == 0 or cropped_image.shape[1] == 0:
        print("Warning: Cropped image is empty after custom crop. This might indicate incorrect crop coordinates.")
        return "Empty cropped image after crop."

    output_cropped_path = "cropped_score_region.png"
    cv2.imwrite(output_cropped_path, cropped_image)
    print(f"Saved cropped image to: {output_cropped_path}")

    print("Sending custom cropped region to EasyOCR for text detection and recognition.")

    try:
        gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        results = reader.readtext(gray_image, allowlist='0123456789.', detail=0)

        string_results = [str(item) for item in results if isinstance(item, (str, int, float))]
        full_ocr_text = " ".join(string_results)

        if full_ocr_text:
            print(f"EasyOCR raw text from custom cropped region: '{full_ocr_text}'")

            numbers_candidates = re.findall(r'\b\d+\.\d{2}\b|\b\d+\b', full_ocr_text)
            print(f"Raw number candidates from regex: {numbers_candidates}")

            final_score_candidates = []
            for num_str in numbers_candidates:
                if 1 <= len(num_str) <= 7:
                    final_score_candidates.append(num_str)

            final_score = "No suitable score found."

            if final_score_candidates:
                decimal_scores = [s for s in final_score_candidates if '.' in s]
                integer_scores = [s for s in final_score_candidates if '.' not in s]

                if decimal_scores:
                    final_score = max(decimal_scores, key=len)
                elif integer_scores:
                    final_score = max(integer_scores, key=len)

                print(f"Final score candidates after filtering: {final_score_candidates}")
            else:
                print("No suitable numerical score found after advanced filtering and prioritization.")

            return final_score

        else:
            print("EasyOCR found no text in the custom cropped region.")
            return "No text found by EasyOCR."

    except Exception as e:
        print(f"An unexpected error occurred during EasyOCR processing: {e}")
        return None


if __name__ == "__main__":

    # Initialize EasyOCR reader once.
    reader = easyocr.Reader(['en'], gpu=True)

    image_file = 'game_screenshot.png'

    print("Firing things up...")
    score = read_game_score_custom_crop(image_file)

    if score is not None:
        print(f"\nExtracted Score: {score}")
    else:
        print("Failed to extract score.")
