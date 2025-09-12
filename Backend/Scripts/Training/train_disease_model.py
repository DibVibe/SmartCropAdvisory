"""
🌾 Disease Detection Model Training
CNN-based plant disease classification using PlantVillage dataset
"""

import tensorflow as tf
import numpy as np
import os
import cv2
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import logging
from pathlib import Path

keras = tf.keras
layers = tf.keras.layers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiseaseModelTrainer:
    def __init__(
        self,
        data_dir="../../Data/datasets/plant_village",
        model_save_path="../Models/disease_model.h5",
        image_size=(224, 224),
    ):
        """
        Initialize the disease detection model trainer

        Args:
            data_dir: Path to PlantVillage dataset
            model_save_path: Path to save trained model
            image_size: Input image dimensions
        """
        self.data_dir = data_dir
        self.model_save_path = model_save_path
        self.image_size = image_size
        self.model = None
        self.label_encoder = LabelEncoder()
        self.class_names = []

    def load_and_preprocess_data(self):
        """Load and preprocess plant disease images"""
        logger.info("🔄 Loading and preprocessing disease dataset...")

        images = []
        labels = []

        # Disease categories from PlantVillage dataset
        disease_categories = [
            "Apple_Black_rot",
            "Apple_Cedar_apple_rust",
            "Apple_healthy",
            "Cherry_healthy",
            "Cherry_Powdery_mildew",
            "Corn_Gray_leaf_spot",
            "Corn_Common_rust",
            "Corn_Northern_Leaf_Blight",
            "Corn_healthy",
            "Grape_Black_rot",
            "Grape_Esca",
            "Grape_Leaf_blight",
            "Grape_healthy",
            "Peach_Bacterial_spot",
            "Peach_healthy",
            "Potato_Early_blight",
            "Potato_Late_blight",
            "Potato_healthy",
            "Rice_Brown_spot",
            "Rice_Hispa",
            "Rice_Leaf_blast",
            "Rice_Neck_blast",
            "Strawberry_Leaf_scorch",
            "Strawberry_healthy",
            "Tomato_Bacterial_spot",
            "Tomato_Early_blight",
            "Tomato_Late_blight",
            "Tomato_Leaf_Mold",
            "Tomato_Septoria_leaf_spot",
            "Tomato_Spider_mites",
            "Tomato_Target_Spot",
            "Tomato_Yellow_Leaf_Curl_Virus",
            "Tomato_mosaic_virus",
            "Tomato_healthy",
            "Wheat_Brown_rust",
            "Wheat_Healthy",
            "Wheat_Yellow_rust",
        ]

        self.class_names = disease_categories

        # Create sample data if dataset not found
        if not os.path.exists(self.data_dir):
            logger.warning(
                "⚠️ Dataset not found. Creating synthetic data for demonstration..."
            )
            return self._create_synthetic_data()

        # Load real dataset
        for category in disease_categories:
            category_path = os.path.join(self.data_dir, category)
            if os.path.exists(category_path):
                for img_file in os.listdir(category_path)[:500]:  # Limit for demo
                    if img_file.lower().endswith((".png", ".jpg", ".jpeg")):
                        img_path = os.path.join(category_path, img_file)
                        img = cv2.imread(img_path)
                        if img is not None:
                            img = cv2.resize(img, self.image_size)
                            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                            images.append(img)
                            labels.append(category)

        return np.array(images), np.array(labels)

    def _create_synthetic_data(self):
        """Create synthetic data for demonstration purposes"""
        logger.info("🎨 Creating synthetic dataset...")

        np.random.seed(42)
        num_samples_per_class = 100
        images = []
        labels = []

        for class_name in self.class_names:
            for _ in range(num_samples_per_class):
                # Create synthetic leaf-like images with patterns
                img = np.random.randint(0, 255, (*self.image_size, 3), dtype=np.uint8)

                # Add some leaf-like patterns
                if "healthy" in class_name.lower():
                    img[:, :, 1] = np.clip(img[:, :, 1] + 50, 0, 255)  # More green
                else:
                    img[:, :, 0] = np.clip(img[:, :, 0] + 30, 0, 255)  # More red/brown

                images.append(img)
                labels.append(class_name)

        return np.array(images), np.array(labels)

    def create_cnn_model(self, num_classes):
        """Create CNN architecture for disease detection"""
        logger.info("🏗️ Building CNN architecture...")

        model = keras.Sequential(
            [
                # Data augmentation layers
                layers.RandomFlip("horizontal"),
                layers.RandomRotation(0.1),
                layers.RandomZoom(0.1),
                # Rescaling
                layers.Rescaling(1.0 / 255),
                # Convolutional base
                layers.Conv2D(
                    32, (3, 3), activation="relu", input_shape=(*self.image_size, 3)
                ),
                layers.MaxPooling2D((2, 2)),
                layers.BatchNormalization(),
                layers.Conv2D(64, (3, 3), activation="relu"),
                layers.MaxPooling2D((2, 2)),
                layers.BatchNormalization(),
                layers.Conv2D(128, (3, 3), activation="relu"),
                layers.MaxPooling2D((2, 2)),
                layers.BatchNormalization(),
                layers.Conv2D(256, (3, 3), activation="relu"),
                layers.MaxPooling2D((2, 2)),
                layers.BatchNormalization(),
                # Classifier head
                layers.GlobalAveragePooling2D(),
                layers.Dropout(0.5),
                layers.Dense(512, activation="relu"),
                layers.BatchNormalization(),
                layers.Dropout(0.3),
                layers.Dense(num_classes, activation="softmax", name="predictions"),
            ]
        )

        return model

    def train_model(self, epochs=50, batch_size=32, validation_split=0.2):
        """Train the disease detection model"""
        logger.info("🚀 Starting model training...")

        # Load data
        X, y = self.load_and_preprocess_data()
        logger.info(f"📊 Loaded {len(X)} samples with {len(self.class_names)} classes")

        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        y_categorical = keras.utils.to_categorical(y_encoded)

        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X,
            y_categorical,
            test_size=validation_split,
            random_state=42,
            stratify=y_encoded,
        )

        # Create model
        self.model = self.create_cnn_model(len(self.class_names))

        # Compile model
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss="categorical_crossentropy",
            metrics=["accuracy", "top_3_accuracy"],
        )

        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5),
            keras.callbacks.ModelCheckpoint(
                self.model_save_path, save_best_only=True, monitor="val_accuracy"
            ),
        ]

        # Train model
        logger.info(f"🎯 Training for {epochs} epochs with batch size {batch_size}")
        history = self.model.fit(
            X_train,
            y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_val, y_val),
            callbacks=callbacks,
            verbose=1,
        )

        # Save model and metadata
        self._save_model_metadata()

        logger.info(f"✅ Model training completed! Saved to {self.model_save_path}")
        return history

    def _save_model_metadata(self):
        """Save model metadata and class names"""
        import pickle

        metadata = {
            "class_names": self.class_names,
            "label_encoder": self.label_encoder,
            "image_size": self.image_size,
            "model_architecture": "CNN",
            "num_classes": len(self.class_names),
        }

        metadata_path = self.model_save_path.replace(".h5", "_metadata.pkl")
        with open(metadata_path, "wb") as f:
            pickle.dump(metadata, f)

        logger.info(f"💾 Model metadata saved to {metadata_path}")

    def evaluate_model(self, X_test, y_test):
        """Evaluate model performance"""
        logger.info("📊 Evaluating model performance...")

        if self.model is None:
            logger.error("❌ Model not trained yet!")
            return

        y_pred = self.model.predict(X_test)
        y_pred_classes = np.argmax(y_pred, axis=1)
        y_true_classes = np.argmax(y_test, axis=1)

        from sklearn.metrics import classification_report, accuracy_score

        accuracy = accuracy_score(y_true_classes, y_pred_classes)
        report = classification_report(
            y_true_classes,
            y_pred_classes,
            target_names=self.class_names,
            zero_division=0,
        )

        logger.info(f"🎯 Test Accuracy: {accuracy:.4f}")
        logger.info(f"📋 Classification Report:\n{report}")

        return accuracy, report


def main():
    """Main training function"""
    logger.info("🌾 Starting Disease Detection Model Training...")

    # Create Models directory if it doesn't exist
    os.makedirs("../Models", exist_ok=True)

    # Initialize trainer
    trainer = DiseaseModelTrainer()

    # Train model
    history = trainer.train_model(epochs=20, batch_size=16)  # Reduced for demo

    logger.info("🎉 Training completed successfully!")

    # Plot training history
    if history:
        plt.figure(figsize=(12, 4))

        plt.subplot(1, 2, 1)
        plt.plot(history.history["accuracy"], label="Training Accuracy")
        plt.plot(history.history["val_accuracy"], label="Validation Accuracy")
        plt.title("Model Accuracy")
        plt.xlabel("Epoch")
        plt.ylabel("Accuracy")
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.plot(history.history["loss"], label="Training Loss")
        plt.plot(history.history["val_loss"], label="Validation Loss")
        plt.title("Model Loss")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.legend()

        plt.tight_layout()
        plt.savefig("../Models/disease_training_history.png")
        logger.info("📈 Training history plot saved!")


if __name__ == "__main__":
    main()
