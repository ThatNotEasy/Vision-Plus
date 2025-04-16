import re, requests
import json
import base64

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def generate_verimatrix_jwt(hardware_id: str) -> str:
    header = {
        "provisioning": [
            {
                "system": "verimatrix",
                "data": [
                    {
                        "name": "vuid",
                        "value": hardware_id
                    }
                ]
            }
        ]
    }
    payload = {}
    encoded_header = base64url_encode(json.dumps(header, separators=(",", ":")).encode())
    encoded_payload = base64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    token = f"{encoded_header}.{encoded_payload}"
    return token

def pretty_print(data: dict):
    con = data.get("con", [])[0]

    print("=" * 80)
    print(f"📺 Title       : {con.get('oti')}")
    print(f"🆔 Content ID  : {con.get('cid')}")
    print(f"📌 Type        : {con.get('typ')}")
    print(f"📅 Year        : {con.get('oda')}")
    print(f"⏱️  Duration    : {int(con.get('dur', 0)) // 60} minutes")
    print(f"🌐 Language    : {con.get('lan')}")
    print(f"🌍 Country     : {', '.join(con.get('cou', []))}")
    print(f"🔞 Adult       : {'Yes' if con.get('adult') else 'No'}")
    print(f"🎭 Categories  : {', '.join(con.get('categories', []))}")
    print("=" * 80)

    print("🖼️  Poster Images:")
    poster_sizes = con.get("loc", [{}])[0].get("img_lnk", {}).get("pos", {}).get("sizes", {})
    for size, path in poster_sizes.items():
        url = f"https://www.visionplus.id/images/repository/{path}"
        print(f"  - {size.upper()}   : {url}")

    print("=" * 80)
    for delivery in con.get("del", []):
        print(f"🎬 Delivery ID  : {delivery.get('eid')}")
        print(f"📅 Start Time   : {delivery.get('sta')}")
        print(f"📅 End Time     : {delivery.get('end')}")
        print(f"🗣️  Audio Lang   : {', '.join(delivery.get('aul', [])) or 'N/A'}")
        print(f"📺 HD           : {'Yes' if delivery.get('hd') else 'No'}")
        print(f"🆔 Stream ID    : {delivery.get('sid')}")
        print(f"🕸️  DRM          : ", end="")
        drm_list = []
        for entry in delivery.get("sov", []):
            for comb in entry.get("comb", []):
                drm_list.extend(comb.get("drm", []))
        print(", ".join(set(drm_list)) or "None")

        stream_url = delivery.get('sov', [{}])[0].get('url')
        print(f"🔗 Stream URL   : {stream_url}")

        domain_match = re.search(r'/live//(.*?)\/DASH', stream_url or "")
        segment_match = re.search(r'/DASH/([a-f0-9]{32})/', stream_url or "")
        if domain_match and segment_match:
            domain_raw = domain_match.group(1)
            domain = domain_raw.replace("EG_", "")
            segment_id = segment_match.group(1)
            mpd_url = f"https://{domain}.cloudfront.net/out/v1/{segment_id}.index.mpd"
            print(f"📄 MPD URL      : {mpd_url}")
        else:
            print("📄 MPD URL      : [Not found]")

        print("-" * 80)
        
        
def extract_id(url: str) -> str:
    match = re.search(r'(SERS\d+)', url)
    if match:
        return match.group(1)
    raise ValueError("Series ID not found in the URL")

def extract_pssh(manifest_url, proxies=None):
    headers = {
        "host": "d2tolhxlph2dpt.cloudfront.net",
        "connection": "keep-alive",
        "sec-ch-ua-platform": "\"Windows\"",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
        "dnt": "1",
        "sec-ch-ua-mobile": "?0",
        "accept": "*/*",
        "origin": "https://www.visionplus.id",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.visionplus.id/",
        "accept-language": "en-US,en;q=0.9,ms;q=0.8"
    }
    try:
        r = requests.get(manifest_url, headers=headers, proxies=proxies)
        if r.status_code == 200:
            widevine_pattern = re.compile(
                r'<ContentProtection[^>]+schemeIdUri="urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed"[^>]*>.*?<cenc:pssh[^>]*>([^<]+)</cenc:pssh>',
                re.DOTALL | re.IGNORECASE
            )
            match = widevine_pattern.search(r.text)
            if match:
                return match.group(1)
            else:
                print("No Widevine PSSH found in manifest.")
                return None
        else:
            print(f"HTTP error {r.status_code}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None