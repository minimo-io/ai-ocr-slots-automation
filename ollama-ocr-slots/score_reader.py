import os, sys
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

    # --- SCORE CROPPING REGION CONFIGURATION ---
    # These values define the rectangular area (x1, y1, x2, y2) of the image
    # where the game score is expected to appear. Adjust these ratios
    # to precisely target your score and exclude unwanted text (like clocks).

    # x1_crop: Starting X-coordinate (left edge of the crop)
    # 0 means the very left edge of the original image.
    x1_crop = 0

    # x2_crop: Ending X-coordinate (right edge of the crop)
    # int(w * 0.5) means crop up to 50% of the image's total width (the left half).
    # Adjust 0.5 (e.g., to 0.4 for left 40%, or 0.6 for slightly more than half)
    # if the score is further right or needs less width.
    x2_crop = int(w * 0.5)

    # y1_crop: Starting Y-coordinate (top edge of the crop)
    # int(h * 0.1) means start cropping 10% down from the top of the image.
    # This is useful to cut off elements like clocks or headers that appear at the top.
    # Adjust 0.1 (e.g., to 0.05 for 5% down, or 0.15 for 15% down)
    # if the score is higher/lower or the unwanted text is larger/smaller.
    y1_crop = int(h * 0.1)

    # y2_crop: Ending Y-coordinate (bottom edge of the crop)
    # int(h * 0.9) means stop cropping 10% up from the bottom of the image.
    # This helps exclude footers or other UI elements at the bottom.
    # Adjust 0.9 (e.g., to 0.95 for 5% up, or 0.8 for 20% up)
    # if the score is closer to the bottom or other unwanted elements exist.
    y2_crop = int(h * 0.9)

    print(f"Cropping image to region: (x1={x1_crop}, y1={y1_crop}, x2={x2_crop}, y2={y2_crop})")

    # Ensure crop coordinates are within the actual image boundaries to prevent errors.
    x1_crop = max(0, x1_crop)
    y1_crop = max(0, y1_crop)
    x2_crop = min(w, x2_crop)
    y2_crop = min(h, y2_crop)

    # Validate the calculated crop dimensions.
    if x1_crop >= x2_crop or y1_crop >= y2_crop:
        print("Warning: Custom crop region results in an empty or invalid image. Adjust crop coordinates carefully.")
        return "Invalid custom crop region."

    # Perform the actual image cropping using OpenCV's array slicing.
    cropped_image = cv_image_original[y1_crop:y2_crop, x1_crop:x2_crop]

    # Check if the cropped image is empty after slicing.
    if cropped_image.shape[0] == 0 or cropped_image.shape[1] == 0:
        print("Warning: Cropped image is empty after custom crop. This might indicate incorrect crop coordinates.")
        return "Empty cropped image after crop."

    # Save the cropped image to disk for easy visualization and debugging.
    # Open 'cropped_score_region.png' in an image viewer to verify the crop.
    output_cropped_path = "cropped_score_region.png"
    cv2.imwrite(output_cropped_path, cropped_image)
    print(f"Saved cropped image to: {output_cropped_path}")

    print("Sending custom cropped region to EasyOCR for text detection and recognition.")

    try:
        # Convert the cropped image to grayscale, which can improve OCR accuracy.
        gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)

        # Perform OCR on the grayscale cropped image.
        # `allowlist='0123456789.'` tells EasyOCR to only recognize digits and periods.
        # If your score can have commas (e.g., 1,234.56), add ',' to the allowlist.
        # `detail=0` returns only the recognized text strings.
        results = reader.readtext(gray_image, allowlist='0123456789.', detail=0)

        # Concatenate all recognized text into a single string for easier regex processing.
        string_results = [str(item) for item in results if isinstance(item, (str, int, float))]
        full_ocr_text = " ".join(string_results)

        if full_ocr_text:
            print(f"EasyOCR raw text from custom cropped region: '{full_ocr_text}'")

            # --- NUMBER EXTRACTION AND FILTERING LOGIC ---
            # This is the core logic for identifying the 'score' from all detected numbers.
            # Adjust this regular expression and filtering criteria based on the
            # specific format and characteristics of your game's score.

            # Regular expression to find number candidates:
            # - `\b\d+\.\d{2}\b`: Matches numbers with one or more digits, a decimal point, and exactly two digits after it (e.g., "1000.00", "25.00"). The \b ensures whole word matches.
            # - `|`: OR
            # - `\b\d+\b`: Matches whole numbers (integers, e.g., "603", "4").
            numbers_candidates = re.findall(r'\b\d+\.\d{2}\b|\b\d+\b', full_ocr_text)

            print(f"Raw number candidates from regex: {numbers_candidates}")

            final_score_candidates = []
            for num_str in numbers_candidates:
                # Length-based filter: Ensures candidates are within a reasonable length for your score.
                # '1000.00' is 7 characters long. '99999.99' would be 8.
                # Adjust `1` and `7` based on the typical min/max length of your actual score.
                if 1 <= len(num_str) <= 7:
                    final_score_candidates.append(num_str)

            final_score = "No suitable score found." # Default return value if no score is identified.

            if final_score_candidates:
                # Prioritization logic:
                # 1. Prefer numbers that contain a decimal point (like "1000.00").
                decimal_scores = [s for s in final_score_candidates if '.' in s]
                # 2. Consider integers if no decimal numbers are found.
                integer_scores = [s for s in final_score_candidates if '.' not in s]

                if decimal_scores:
                    # If multiple decimal scores, pick the longest one (common for main scores).
                    final_score = max(decimal_scores, key=len)
                elif integer_scores:
                    # If no decimal scores, pick the longest integer score.
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

    # Path to your game screenshot image.
    image_file = 'game_screenshot.png'

    # Call the function to read the score.
    score = read_game_score_custom_crop(image_file)

    # Print the extracted score or a failure message.
    if score is not None:
        print(f"\nExtracted Score: {score}")
    else:
        print("Failed to extract score.")
