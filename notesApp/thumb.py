from textblob import TextBlob
import nltk
import ssl
import together
import base64
import random
import re

together.api_key = "40cf8a0074d3b4a1b06445377ae0edea96ff2ce61f2a1388131668ed9bcb3ad4"

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('brown')

def extract_nouns(sen):
    sen = re.sub(r'[^\w\s]','',sen)
    blob = TextBlob(sen)
    return blob.noun_phrases

def generate_image(sen, note_id):
    nouns = extract_nouns(sen)
    sen = ""
    for noun in nouns:
        sen += noun + ", "
    seed = random.randint(0, 1000)
    if len(sen) == 0:
        sen = "leaf"
    # generate image
    response = together.Image.create(prompt=sen, height=256, width=256, model="SG161222/Realistic_Vision_V3.0_VAE", seed=seed, steps=20)
    # save the first image
    image = response["output"]["choices"][0]
    with open("./notesApp/static/thumbnails/" + str(note_id) + ".png", "wb") as f:
        f.write(base64.b64decode(image["image_base64"]))