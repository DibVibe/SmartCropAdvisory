"""
🖼️ Image Preprocessing for Disease Detection
Utilities for processing plant disease images
"""

import cv2
import numpy as np
import os
from pathlib import Path
import logging
from PIL import Image, ImageEnhance
import albumentations as A

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImagePreprocessor:
    def __init__(self, target_size=(224, 224)):
        """
        Initialize image preprocessor

        Args:
            target_size: Target image size (width, height)
        """
        self.target_size = target_size
        self.augmentation_pipeline = self._create_augmentation_pipeline()

    def _create_augmentation_pipeline(self):
        """Create data augmentation pipeline"""
        return A.Compose(
            [
                A.RandomRotate90(p=0.5),
                A.Flip(p=0.5),
                A.OneOf(
                    [
                        A.GaussNoise(p=0.3),
                        A.GaussianBlur(p=0.3),
                        A.MotionBlur(p=0.3),
                    ],
                    p=0.4,
                ),
                A.OneOf(
                    [
                        A.RandomBrightnessContrast(p=0.3),
                        A.HueSaturationValue(p=0.3),
                        A.ColorJitter(p=0.3),
                    ],
                    p=0.5,
                ),
                A.ShiftScaleRotate(
                    shift_limit=0.1, scale_limit=0.1, rotate_limit=15, p=0.5
                ),
                A.RandomCrop(width=200, height=200, p=0.3),
                A.Resize(self.target_size[0], self.target_size[1]),
            ]
        )

    def load_and_preprocess(self, image_path, apply_augmentation=False):
        """
        Load and preprocess a single image

        Args:
            image_path: Path to the image file
            apply_augmentation: Whether to apply data augmentation

        Returns:
            Preprocessed image array
        """
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                logger.error(f"❌ Could not load image: {image_path}")
                return None

            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Basic preprocessing
            image = self._basic_preprocessing(image)

            # Apply augmentation if requested
            if apply_augmentation:
                augmented = self.augmentation_pipeline(image=image)
                image = augmented["image"]
            else:
                # Just resize without augmentation
                image = cv2.resize(image, self.target_size)

            # Normalize pixel values
            image = image.astype(np.float32) / 255.0

            return image

        except Exception as e:
            logger.error(f"❌ Error processing {image_path}: {e}")
            return None

    def _basic_preprocessing(self, image):
        """Apply basic preprocessing steps"""
        # Remove noise
        image = cv2.bilateralFilter(image, 9, 75, 75)

        # Enhance contrast
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        image = cv2.merge([l, a, b])
        image = cv2.cvtColor(image, cv2.COLOR_LAB2RGB)

        return image

    def detect_and_crop_leaf(self, image):
        """
        Detect and crop the main leaf area from the image

        Args:
            image: Input image array

        Returns:
            Cropped leaf image
        """
        # Convert to HSV for better plant detection
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

        # Define range for green colors (leaves)
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])

        # Create mask
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # Morphological operations to clean the mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Find the largest contour (main leaf)
            largest_contour = max(contours, key=cv2.contourArea)

            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(largest_contour)

            # Add some padding
            padding = 20
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image.shape[1] - x, w + 2 * padding)
            h = min(image.shape[0] - y, h + 2 * padding)

            # Crop the image
            cropped = image[y : y + h, x : x + w]

            return cropped if cropped.size > 0 else image

        return image

    def enhance_disease_features(self, image):
        """
        Enhance features that are important for disease detection

        Args:
            image: Input image array

        Returns:
            Enhanced image
        """
        # Convert to PIL for easier manipulation
        pil_image = Image.fromarray((image * 255).astype(np.uint8))

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(1.2)

        # Enhance color
        enhancer = ImageEnhance.Color(pil_image)
        pil_image = enhancer.enhance(1.1)

        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(pil_image)
        pil_image = enhancer.enhance(1.1)

        # Convert back to numpy array
        enhanced = np.array(pil_image) / 255.0

        return enhanced

    def batch_process_directory(self, input_dir, output_dir, apply_augmentation=True):
        """
        Process all images in a directory

        Args:
            input_dir: Input directory path
            output_dir: Output directory path
            apply_augmentation: Whether to apply augmentation
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}

        processed_count = 0

        for image_file in input_path.rglob("*"):
            if image_file.suffix.lower() in image_extensions:
                # Create corresponding output directory structure
                relative_path = image_file.relative_to(input_path)
                output_file = output_path / relative_path
                output_file.parent.mkdir(parents=True, exist_ok=True)

                # Process image
                processed_image = self.load_and_preprocess(
                    image_file, apply_augmentation=apply_augmentation
                )

                if processed_image is not None:
                    # Save processed image
                    processed_image_uint8 = (processed_image * 255).astype(np.uint8)
                    cv2.imwrite(
                        str(output_file),
                        cv2.cvtColor(processed_image_uint8, cv2.COLOR_RGB2BGR),
                    )
                    processed_count += 1

                    if processed_count % 100 == 0:
                        logger.info(f"📸 Processed {processed_count} images...")

        logger.info(f"✅ Completed processing {processed_count} images")

    def create_augmented_dataset(self, input_dir, output_dir, augmentation_factor=3):
        """
        Create augmented dataset from original images

        Args:
            input_dir: Input directory with original images
            output_dir: Output directory for augmented dataset
            augmentation_factor: Number of augmented versions per original image
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}

        for image_file in input_path.rglob("*"):
            if image_file.suffix.lower() in image_extensions:
                # Load original image
                original_image = cv2.imread(str(image_file))
                if original_image is None:
                    continue

                original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

                # Create output directory structure
                relative_path = image_file.relative_to(input_path)
                class_output_dir = output_path / relative_path.parent
                class_output_dir.mkdir(parents=True, exist_ok=True)

                # Save original
                original_name = relative_path.stem + "_original" + relative_path.suffix
                cv2.imwrite(
                    str(class_output_dir / original_name),
                    cv2.cvtColor(original_image, cv2.COLOR_RGB2BGR),
                )

                # Create augmented versions
                for i in range(augmentation_factor):
                    augmented = self.augmentation_pipeline(image=original_image)
                    augmented_image = augmented["image"]

                    augmented_name = (
                        f"{relative_path.stem}_aug_{i}{relative_path.suffix}"
                    )
                    cv2.imwrite(
                        str(class_output_dir / augmented_name),
                        cv2.cvtColor(augmented_image, cv2.COLOR_RGB2BGR),
                    )

        logger.info(f"✅ Created augmented dataset with factor {augmentation_factor}")


def main():
    """Main function for testing image preprocessing"""
    logger.info("🖼️ Testing Image Preprocessing...")

    # Create preprocessor
    preprocessor = ImagePreprocessor()

    # Create sample directories
    os.makedirs("../../Data/sample_images", exist_ok=True)
    os.makedirs("../../Data/processed_images", exist_ok=True)

    logger.info("✅ Image preprocessing utilities ready!")


if __name__ == "__main__":
    main()
