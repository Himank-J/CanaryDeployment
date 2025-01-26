from transformers import AutoImageProcessor, AutoModelForImageClassification

def get_processor_and_model(hf_string):
	processor = AutoImageProcessor.from_pretrained(hf_string, use_fast=True)
	model = AutoModelForImageClassification.from_pretrained(hf_string)

	return [processor, model]

def save_model_processor(model, processor, save_prefix_str):
	model.save_pretrained(f"./models/{save_prefix_str}/model")
	processor.save_pretrained(f"./models/{save_prefix_str}/processor")


[emotions_processor, emotions_model] = get_processor_and_model("dima806/facial_emotions_image_detection")
save_model_processor(emotions_model, emotions_processor, "emotions-classifier")

[hand_gestures_processor, hand_gestures_model] = get_processor_and_model("dima806/hand_gestures_image_detection")
save_model_processor(hand_gestures_model, hand_gestures_processor, "hand-gestures-classifier")

[faces_age_processor, faces_age_model] = get_processor_and_model("dima806/faces_age_detection")
save_model_processor(faces_age_model, faces_age_processor, "faces-age-detection")