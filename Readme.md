# POE API
poe bots connector served on rest(fastapi/uvicorn)

### startup
build application script with:
```bash
pip install -e .
```

### RUN API
```
poe_api run -H 127.0.0.1 -p 9000 -v v1 
```
or 
```
./runserver.sh script
```



#### Python Client
```python
from openai import OpenAI

# init client and connect to localhost server
client = OpenAI(
    api_key="fake-api-key",
    base_url="http://server:port",
)
# # stream version
stream = client.chat.completions.create(
    model="gpt4_o",
    messages=[{"role": "user", "content": [{"type":"text","text":"tell me a joke in spanish!"}]}],
    stream=True,
)

for chunk in stream:
    print(chunk.choices[0].delta.content or "")


```


### Stream Format
response to strean is in starlette format.
```json
{
    "id": "int",
    "object": "chat.completion.chunk",
    "created": "time.time()",
    "model": "request.model",
    "choices": [
        {
            "delta": {
                "content": "message"
            }
        }
    ],
}

```


