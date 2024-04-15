from core.utils.gpt_util import GPTUtil


class ClipVariantsUtil:

    @staticmethod
    def fetch_variants(api_key, hint, amount):
        r = GPTUtil.request([
            {
                "role": "system",
                "content": "Please rewrite and restructure the given input. Use the same style of language,"
                           " use simple words and keep the sentences short. "
                           "Shorter is better. Only use the relevant information. "
                           "You also can use just keywords"
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