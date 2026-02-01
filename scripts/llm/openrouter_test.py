from openai import OpenAI
import os
import dotenv
dotenv.load_dotenv()

print(f"API Key loaded: {os.getenv('OPENROUTER_API_KEY') is not None}")                                                                                        
print(f"API Key length: {len(os.getenv('OPENROUTER_API_KEY', ''))}")   

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

completion = client.chat.completions.create(
  extra_headers={},
  model="google/gemma-3-27b-it:free",
  messages=[
    {
      "role": "user",
      "content": "What is the meaning of life?"
    }
  ]
)

print(completion.choices[0].message.content)
