import os

path = r'd:\kuliah\Project After Lulus\ihsg-analyzer\pages\dashboard.py'
with open(path, 'rb') as f:
    data = f.read()

# Try to find the import
old_import = b'import google.generativeai as genai'
new_import = b'from google import genai'

if old_import in data:
    data = data.replace(old_import, new_import)
    print("Updated import")
else:
    print("Import not found")

# Try to find the block
old_block_start = b'genai.configure(api_key=api_key)'
if old_block_start in data:
    # This is a bit complex for a simple script, but I'll try to replace a larger chunk
    print("Found block start")
    
with open(path, 'wb') as f:
    f.write(data)
