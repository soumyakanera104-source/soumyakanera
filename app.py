from groq import Groq
import os

# Try to use python-dotenv if available; otherwise provide a tiny fallback loader
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    def load_dotenv(path: str = ".env"):
        """Minimal .env loader: read KEY=VALUE lines and set os.environ if not present."""
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key not in os.environ:
                    os.environ[key] = val

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