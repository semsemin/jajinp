from ultralytics import YOLO

model = YOLO("weights/best.pt")

# Perform object detection on an image
results = model(" ")
results[0].show()


# Export the model to ONNX format
path = model.export(format="onnx")  # return path to exported model
