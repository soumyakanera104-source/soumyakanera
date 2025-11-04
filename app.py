from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

chat_completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "Help to answer my queries in a clear and concise way."},
        {"role": "user", "content": "Explain the importance of large language models."}
    ],
    model="llama-3.1-8b-instant",
    temperature=0.7,
    max_tokens=300
)

print(chat_completion.choices[0].message.content)