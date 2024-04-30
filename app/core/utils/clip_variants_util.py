from core.utils.gpt_util import GPTUtil


class ClipVariantsUtil:

    @staticmethod
    def fetch_variants(api_key, hint, amount):
        r = GPTUtil.request([
            {
                "role": "system",
                "content": "Reformulate this description, use a different wording."
                           "Just output the rewritten part in one line without any additional information. "
                           f"Do it {amount} times, each variant in a new line"
            },
            {
                "role": "user",
                "content": hint
            }
        ], api_key=api_key, model="gpt-4-turbo", additional_data={"n": 1})

        if r and r.get("content"):
            return r.get("content").split("\n")

        return None