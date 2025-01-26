from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image

processor = AutoImageProcessor.from_pretrained("/home/ubuntu/CanaryDeployment/classifier-deployment/models/emotions-classifier/processor", use_fast=True)
model = AutoModelForImageClassification.from_pretrained("/home/ubuntu/CanaryDeployment/classifier-deployment/models/emotions-classifier/model")

image = Image.open("/home/ubuntu/CanaryDeployment/classifier-deployment/test_images/emotion-classifier-sample.png")
image = image.convert('RGB') 
inputs = processor(images=image, return_tensors="pt")

outputs = model(**inputs)
logits = outputs.logits

predicted_class_idx = logits.argmax(-1).item()
print(f"Emotion Classification - Predicted class: {model.config.id2label[predicted_class_idx]}")

print('-----------------')

processor = AutoImageProcessor.from_pretrained("/home/ubuntu/CanaryDeployment/classifier-deployment/models/hand-gestures-classifier/processor", use_fast=True)
model = AutoModelForImageClassification.from_pretrained("/home/ubuntu/CanaryDeployment/classifier-deployment/models/hand-gestures-classifier/model")

image = Image.open("/home/ubuntu/CanaryDeployment/classifier-deployment/test_images/hand-gesture-sample.png")
image = image.convert('RGB') 
inputs = processor(images=image, return_tensors="pt")

outputs = model(**inputs)
logits = outputs.logits

predicted_class_idx = logits.argmax(-1).item()
print(f"Hand Gesture Classification - Predicted class: {model.config.id2label[predicted_class_idx]}")

print('-----------------')

processor = AutoImageProcessor.from_pretrained("/home/ubuntu/CanaryDeployment/classifier-deployment/models/faces-age-detection/processor", use_fast=True)
model = AutoModelForImageClassification.from_pretrained("/home/ubuntu/CanaryDeployment/classifier-deployment/models/faces-age-detection/model")

image = Image.open("/home/ubuntu/CanaryDeployment/classifier-deployment/test_images/age-group-sample.png")
image = image.convert('RGB') 
inputs = processor(images=image, return_tensors="pt")

outputs = model(**inputs)
logits = outputs.logits

predicted_class_idx = logits.argmax(-1).item()
print(f"Faces Age Detection - Predicted class: {model.config.id2label[predicted_class_idx]}")
