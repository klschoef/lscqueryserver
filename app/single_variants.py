import os
from dotenv import load_dotenv

from core.utils.clip_variants_util import ClipVariantsUtil

load_dotenv()
api_key = os.getenv('API_KEY')

variants = ClipVariantsUtil.fetch_variants(
    api_key,
    "I was praying to small golden Buddha in a tunnel. There were plants and offerings around the Buddha. "
    "It was inside of a tourist park with a large ornamental tower. It was in September 2019 in Thailand.",
    5)

print("\n".join(variants))