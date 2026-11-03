from dotenv import load_dotenv
import os
load_dotenv()

def get_model(model:str=os.getenv('MODEL')) -> str:
    return model