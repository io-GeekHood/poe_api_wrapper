
from openai import OpenAI

# init client and connect to localhost server
client = OpenAI(
    api_key="fake-api-key",
    base_url="http://localhost:2525",
)
# # stream version
stream = client.chat.completions.create(
    model="gpt4_o",
    messages=[{"role": "user", "content": [{"type":"text","text":"translate to spanish"}]}],
    stream=True,
)

for chunk in stream:
    print(chunk.choices[0].delta.content or "")
