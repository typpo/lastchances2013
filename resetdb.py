from app import db
import os

try:
  os.remove("matchmaking.db")
except:
  pass

db.create_all()
