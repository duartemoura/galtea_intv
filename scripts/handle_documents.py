import sys
import os
from dotenv import load_dotenv

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, project_root)

# Load environment variables from .env file
load_dotenv(os.path.join(project_root, ".env"))

from src.db import VectorDB

db = VectorDB()


db.upload_document("/Users/duartemoura/Documents/GitHub/galtea_intv/docs/vw.pdf")

#db.delete_document("vw.pdf")

