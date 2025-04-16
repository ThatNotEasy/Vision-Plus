import re
from modules.vision_plus import VISION_PLUS
from modules.banners import banners
from modules.extractor import extract_id, extract_pssh

def is_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")

if __name__ == "__main__":
    banners()
    user_input = input("Enter Vision+ URL or CID: ").strip()
    try:
        content_id = extract_id(user_input) if is_url(user_input) else user_input
        vision_plus = VISION_PLUS()
        vision_plus.get_details(content_id)
        multirights = vision_plus.get_multirights(content_id)
        license_url, manifest_url = vision_plus.get_license_manifest(multirights)
        pssh = extract_pssh(manifest_url)
        vision_plus.decrypt_content(license_url, pssh)

    except Exception as e:
        print(f"[ERROR] {e}")
