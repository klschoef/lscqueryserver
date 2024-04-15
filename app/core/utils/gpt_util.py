import requests


class GPTUtil:

    GPT_API_URL = "https://api.openai.com/v1/chat/completions"

    @staticmethod
    def request(messages, api_key, model="gpt-3.5-turbo-0125", additional_data={}):
        r = requests.post(GPTUtil.GPT_API_URL, json={
            "model": model,
            "messages": messages
        } | additional_data, headers={
            "Authorization": f"Bearer {api_key}"
        })

        if r.ok:
            json_r = r.json()
            return {
                "json_response": json_r,
                "http_response": r,
                "content": json_r["choices"][0]["message"]["content"],
                "message": json_r["choices"][0]["message"],
                "choices": json_r["choices"],
            }
        else:
            return None
