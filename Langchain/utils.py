import os
from dotenv import load_dotenv
load_dotenv()

def getmodel():
    model=os.getenv('MODEL')
    return model

def getEmbeddedModel():
    model=os.getenv('EMBED_MODEL')
    return model