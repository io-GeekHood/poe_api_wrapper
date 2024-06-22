# from fastapi import FastAPI
# from fastapi_utils.inferring_router import InferringRouter
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi_redis_cache import FastApiRedisCache
# from poe_api.util.logging import logger
# import socket
# import time
# import os
# import signal
# import gc
# import threading

# # inititate application requirements
# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# router = InferringRouter()
# caching = FastApiRedisCache()

# TRANSLATOR_HOST = os.getenv("TRANSLATOR_HOST","172.27.226.11")
# TRANSLATOR_PORT = os.getenv("TRANSLATOR_PORT","5555")
# VECTORIZER_HOST= os.getenv("VECTORIZER_HOST","172.27.226.67")
# VECTORIZER_PORT= os.getenv("VECTORIZER_PORT","5563")
# QDRANT_HOST = os.getenv("QDRANT_HOST",'172.27.226.110')
# QDRANT_PORT = os.getenv("QDRANT_PORT",'6333')
# CV_HOST = os.getenv("CV_HOST","172.27.226.67")
# CV_PORT = os.getenv("CV_PORT","5565")
# RERANKER_HOST = os.getenv("RERANKER_HOST","172.27.226.67")
# RERANKER_PORT = os.getenv("RERANKER_PORT","5564")
# MERGER_HOST = os.getenv("MERGER_HOST","172.27.226.67")
# MERGER_PORT = os.getenv("MERGER_PORT","5566")
# REDIS_CACHE = os.getenv("REDIS_CACHE","redis://127.0.0.1:6379")
# logger.debug(f"VECTORIZER_URI | ip = {VECTORIZER_HOST} port = {VECTORIZER_PORT}")
# logger.debug(f"QDRANT_URI | ip = {QDRANT_HOST} port = {QDRANT_PORT}")
# logger.debug(f"CV_URI | ip = {CV_HOST} port = {CV_PORT}")
# logger.debug(f"RERANKER_URI | {RERANKER_HOST} port = {RERANKER_PORT}")
# logger.debug(f"MERGER_URI | ip = {MERGER_HOST} port = {MERGER_PORT}")
# logger.debug(f"REDIS_CACHE | ip = {REDIS_CACHE}")


# def healthcheck():
#     backing_services = {
#         "Vectorizer_BigG":(VECTORIZER_HOST,VECTORIZER_PORT),
#         "Category_Vectorizer": (CV_HOST,CV_PORT),
#         "Reranker": (RERANKER_HOST,RERANKER_PORT),
#         "imageTextMerger": (MERGER_HOST,MERGER_PORT),
#         "Translator": (TRANSLATOR_HOST,TRANSLATOR_PORT)
#     }
#     while True:
#         for service,address in backing_services.items():
#             try:
#                 connection = socket.create_connection(address, timeout=2)
#                 time.sleep(0.15)
#                 connection.close()
#                 time.sleep(1)
#             except (ConnectionRefusedError, socket.timeout):
#                 logger.error(f"{service} DEAD! (garbage collector activated)")
#                 gc.collect()
#                 uvicorn_pid = os.getppid()
#                 logger.error(f"Killing uvicorn PID {uvicorn_pid}")
#                 os.kill(uvicorn_pid, signal.SIGINT)
#                 raise SystemExit
            
# threading.Thread(target=healthcheck).start()

# # initialize redis cache class for request | response
# @app.on_event("startup")
# async def startup():
#     redis_cache = caching.init(
#         host_url=REDIS_CACHE,
#         prefix="searchapi-cache",
#         response_header="X-MyAPI-Cache",
#     )
    
#     return redis_cache

# @app.on_event("shutdown")
# async def cleanup():
#     logger.info("Performing cleanup...")
#     pid = os.getpid()
#     logger.info(f'Worker with PID {pid} is gonna get shut down')
tokens = {
    'm-b': 'PH2DFI93zJ8b_IPzqNHFEA==; Path=/; Domain=quora.com; Secure; HttpOnly; Expires=Fri, 17 Apr 2026 12:05:14 GMT;',
    'm-lat': '/S+avRa6ZqNjCXfxzgO8RPBn55a41g+flJvQEUk0Ug==;',
    'm-uid':'1500740041;',
    'm-login':'1; Path=/; Domain=quora.com; Expires=Sat, 18 Apr 2026 00:05:14 GMT;',
    'm-b_lax':'PH2DFI93zJ8b_IPzqNHFEA==; Path=/; Domain=quora.com; Secure; HttpOnly; Expires=Fri, 17 Apr 2026 12:05:14 GMT;',
    'm-b_strict':'PH2DFI93zJ8b_IPzqNHFEA==; Path=/; Domain=quora.com; Secure; HttpOnly; Expires=Fri, 17 Apr 2026 12:05:14 GMT;',
    'm-s':'lrqgM0Pzz0IIufRgisSNmg==; Path=/; Domain=quora.com; Secure; HttpOnly; Expires=Fri, 17 Apr 2026 12:05:14 GMT;',
    'p-b':'fflBQAr2k2qx_9BULWhxwA%3D%3D; Path=/; Expires=Fri, 17 Apr 2026 09:53:58 GMT; Max-Age=63072000; Secure; HttpOnly; SameSite=none'

}

heads = {
"quora-formkey":"5d2a71acd9c2647159724723e896af49",
"quora-tchannel":"poe-chan63-8888-hszozbpfoqtpburjmuho",
"user-agent":"Poe a2.39.8 rv:3918 env:prod (SM-S908E; Android OS 9; en_US)",
"poe-language-code":"en",
"content-type":"application/json; charset=utf-8",
"cookies":"m-uid=1500740041; m-login=1; m-lat=/S+avRa6ZqNjCXfxzgO8RPBn55a41g+flJvQEUk0Ug==; m-b_lax=PH2DFI93zJ8b_IPzqNHFEA==; m-b_strict=PH2DFI93zJ8b_IPzqNHFEA==; m-b=PH2DFI93zJ8b_IPzqNHFEA==; m-s=lrqgM0Pzz0IIufRgisSNmg=="
}

proxy_context = {
    "https":"http://192.168.1.127:2080", 
    "http":"http://192.168.1.127:2080"}

