import os
from dotenv import load_dotenv


load_dotenv('env/data.env')
print(os.getenv('apiKey'))
