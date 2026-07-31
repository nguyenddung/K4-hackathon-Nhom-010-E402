import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv('.env')
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
model = os.getenv('GEMINI_MODEL', 'gemini-3.5-flash')
print('MODEL', model)
try:
    response = client.models.generate_content(
        model=model,
        contents='Reply with JSON {"ok": true}',
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=200,
            response_mime_type='application/json',
        ),
    )
    print('SUCCESS', response.text)
except Exception as exc:
    import traceback
    traceback.print_exc()
