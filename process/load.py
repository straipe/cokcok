import tensorflow_hub as hub

model_name = "movenet_thunder"

if "movenet_thunder" in model_name:
    module = hub.load("https://tfhub.dev/google/movenet/singlepose/thunder/4")
    input_size = 256
elif "movenet_lightning" in model_name:
    module = hub.load("https://tfhub.dev/google/movenet/singlepose/lightning/4")
    input_size = 192
else:
    raise ValueError("Unsupported model name: %s" % model_name)