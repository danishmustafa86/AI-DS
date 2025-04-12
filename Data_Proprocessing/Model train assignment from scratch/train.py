from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
from pathlib import Path

def create_model(input_shape=(224, 224, 3)):
    model = models.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy'])
    return model

def train():
    # Create models directory if not exists
    Path('models').mkdir(exist_ok=True)
    
    # Data generators
    train_datagen = ImageDataGenerator(rescale=1./255)
    test_datagen = ImageDataGenerator(rescale=1./255)
    
    train_gen = train_datagen.flow_from_directory(
        'data/processed/train',
        target_size=(224, 224),
        batch_size=32,
        class_mode='binary')
    
    test_gen = test_datagen.flow_from_directory(
        'data/processed/test',
        target_size=(224, 224),
        batch_size=32,
        class_mode='binary')
    
    # Create and train model
    model = create_model()
    history = model.fit(
        train_gen,
        epochs=10,
        validation_data=test_gen)
    
    # Save model
    model.save('models/sparrow_crow_classifier.h5')
    
    # Plot training history
    plt.figure(figsize=(10, 5))
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.savefig('models/training_history.png')

if __name__ == '__main__':
    train()