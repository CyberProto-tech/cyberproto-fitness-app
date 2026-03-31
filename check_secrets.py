import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print("--- SECURITY CHECK ---")
print(f"File exists in folder: {os.path.exists('.env')}")
print(f"SUPABASE_URL: {url}")
print(f"SUPABASE_KEY: {key[:10]}..." if key else "SUPABASE_KEY: None")