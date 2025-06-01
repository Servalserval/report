import asyncio
import aiohttp

async def async_send_request(url, method, json = None, headers = None, params = None, timeout = None, return_json = True, print_res = False):
    try:
        async with aiohttp.ClientSession() as session:
            if method == "get":
                async with session.get(url = url, params=params, timeout=timeout, json = json, headers = headers) as response:
                    if print_res:
                        print(f"Response status: {response.status}")
                        print(f"Response headers: {response.headers}")
                    text = await response.text()
                    if print_res:
                        print(f"Response text: {text}")
                    if return_json:
                        try:
                            res = await response.json()
                        except aiohttp.ContentTypeError:
                            print("Response is not JSON")
                            res = text
                    else:
                        res = text
                    return res

            if method == "post":
                async with session.post(url = url, json = json, headers = headers) as response:
                    if print_res:
                        print(f"Response status: {response.status}")
                        print(f"Response headers: {response.headers}")
                    text = await response.text()
                    if print_res:
                        print(f"Response text: {text}")
                    if return_json:
                        try:
                            res = await response.json()
                        except aiohttp.ContentTypeError:
                            print("Response is not JSON")
                            res = text
                    else:
                        res = text
                    return res
                
    except aiohttp.ClientResponseError as e:
        print(f"Request failed: {e.status}")
        print(f"Response text: {e.message}")
    except Exception as e:
        print(f"Async send request error: {e}")
    return None
