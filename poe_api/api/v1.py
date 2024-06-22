import time
from starlette.responses import StreamingResponse
from fastapi import FastAPI, HTTPException, Depends,Request
from contextlib import asynccontextmanager
from poe_api.config.config_model import PoeConfig,OpenAiRequest,Proxies,ChatCompletionRequest,Message
from poe_api.adapter.poewrapper import PoeApi
import os


WrapperInstance = None
@asynccontextmanager
async def get_dependencies(app):
    global WrapperInstance
    poecfg = PoeConfig("./assets/config.yaml")
    WrapperInstance = PoeApi(init_config=poecfg)
    yield 



app = FastAPI(title="OpenAI-compatible Poe Wrapper",lifespan=get_dependencies)


@app.post("/chat/completions")
async def chat_completions(
    chatcompletion: ChatCompletionRequest,
    request: Request
):
    if not len(chatcompletion.messages) == 1:
        raise HTTPException(
            status_code=422,
            detail="messages can only hold one message from the user at the moment",
        )
    if chatcompletion.messages[0].role != "user":
        raise HTTPException(
            status_code=422,
            detail="messages can only hold one message from the user at the moment",
        )
    if chatcompletion.model not in WrapperInstance.config.PriceMapping:
        raise HTTPException(
            status_code=422,
            detail=f"model name not recognized. avaiable models are {', '.join([k for k,_ in WrapperInstance.PriceMapping.items()])}",
        )

    if not chatcompletion.stream:
        text_response, chat_id = await WrapperInstance.send_message(request=chatcompletion,token=request.headers.get('Authorization'))
        

        return {
            "id": chat_id,
            "object": "chat.completion",
            "created": time.time(),
            "model": chatcompletion.model,
            "choices": [{"message": Message(role="assistant", content=[{"format":"text","text":text_response}])}],
        }
    else:
        return StreamingResponse(
            WrapperInstance.send_message_stream(
                request=chatcompletion,token=request.headers.get('Authorization')
            ),
            media_type="application/x-ndjson",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
