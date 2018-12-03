import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import requests
import orm_module


APP_ID = "lijiexu-onlinere-SBX-060a78903-59edffad"  # App ID(Client ID):
DEV_ID = "4f24052-4c04-4809-865d-041624a036e0"  # Dev ID
CERT_ID = "SBX-60a78903dce9-866c-44df-b392-98ee"  # Cert ID(Client Secret)


"""
  HTTP方法：    POST
   URL（沙盒）： https ： //api.sandbox.ebay.com/identity/v1/oauth2/token

  HTTP标头：
    Content-Type = application / x-www-form-urlencoded
    Authorization = Basic < B64-encoded_oauth_credentials >

  请求正文（为便于阅读而包装）：
    grant_type = client_credentials＆
    redirect_uri = < RuName-value >＆
    范围= HTTPS：//api.ebay.com/oauth/api_scope
"""
