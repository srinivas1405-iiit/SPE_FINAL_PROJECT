import tensorflow_hub as hub
import os

print("Pre-downloading Universal Sentence Encoder...")
# Download to the default cache dir so it's available at runtime
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
print("Model downloaded successfully!")
