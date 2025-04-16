import requests
import json
from modules.extractor import pretty_print, generate_verimatrix_jwt
from modules.config import setup_config
from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH

class VISION_PLUS:
    def __init__(self):
        self.config = setup_config()
        self.widevine_device = self.config["VISION_PLUS"]["DEVICE"]
        self.proxies = {"http": self.config["VISION_PLUS"]["PROXIES"], "https": self.config["VISION_PLUS"]["PROXIES"]}
        self.token = self.config["VISION_PLUS"]["TOKEN"]
        self.hardware_id = self.config["VISION_PLUS"]["HARDWARE_ID"]
        self.provision_data = generate_verimatrix_jwt(self.hardware_id)
        
    def get_details(self, content_id):
        url = "https://www.visionplus.id/managetv/tvinfo/content/get"
        querystring = {
            "cid": content_id,
            "deliveryLimit": "20,20,20",
            "language": "ENG",
            "partition": "IndonesiaPartition",
            "region": "Indonesia",
            "view": "web_content_info_del_view"
        }
        headers = {
            "host": "www.visionplus.id",
            "connection": "keep-alive",
            "sec-ch-ua-platform": "\"Windows\"",
            "iris-app-version": "11.3.75",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "iris-device-type": "WINDOWS/CHROME",
            "iris-device-class": "PC",
            "iris-device-region": "Indonesia",
            "sec-ch-ua-mobile": "?0",
            "iris-hw-device-id": self.hardware_id,
            "iris-app-mode": "Normal",
            "iris-device-status": "ACTIVE",
            "dnt": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "iris-module-id": "+hZMMSTG",
            "accept": "*/*",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.visionplus.id/webclient/",
            "accept-language": "en-US,en;q=0.9,ms;q=0.8"
        }
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        pretty_print(data)
        

    def get_multirights(self, content_id):
        url = "https://www.visionplus.id/managetv/bookmark/seriesFilter"
        querystring = {
            "cid": content_id,
            "identityToken": self.token,
            "language": "ENG",
            "partition": "IndonesiaPartition",
            "scope": "VOD",
            "view": "stb_contents_list_view"
        }
        headers = {
            "host": "www.visionplus.id",
            "connection": "keep-alive",
            "sec-ch-ua-platform": "\"Windows\"",
            "authorization": self.token,
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "iris-endpoints-version": "VklSVFVBTF9DSEFOTkVMUz0xNjk1NjIyNzE1NTI2LFVTRVJfU0VUVElOR1M9MTc0NDYwMjEyOTExNCxTVUJTQ1JJQkVSX1NFVFRJTkdTPTE3NDQ2MDIxMjkxMTQsUFVSQ0hBU0VfTElTVD0xNzQ0NjAyMTI5MTE0LFVJX0RBVEE9MTc0NDE3NDU1NzIyMSxVU0VSX0RBVEE9MTc0NDYwMjEyOTExNCxSRUNPUkRJTkdfTElTVD0xNzQ0MTc0NTU3MjIxLFVTRVJfUFJPRklMRT0xNzQ0MTc0NTYwNjEyLFNFR01FTlRBVElPTj0xNzQ0MTc0NTY1NDcwLFBFUlNPTkFMX0FDVElWRV9DSEFOTkVMUz0xNzQ0MTc0NjYzNTE0LE9UVF9ERVZJQ0VTPTE3NDQ2MDIxMjkxMjgsREVWSUNFX1NFVFRJTkdTPTE3NDQ2MDIxMjkxMTQsRkFWX0NIQU5ORUxfTElTVD0xNjk2NDQyMDEwMDQyLEFDVElWRV9DSEFOTkVMUz0xNzQ0NjAyMTI5MTE0",
            "sec-ch-ua-mobile": "?0",
            "iris-hw-device-id": self.hardware_id,
            "iris-device-status": "ACTIVE",
            "iris-app-version": "11.3.75",
            "iris-profile-id": "13701824",
            "iris-device-type": "WINDOWS/CHROME",
            "iris-device-class": "PC",
            "iris-device-region": "Indonesia",
            "iris-app-mode": "Normal",
            "dnt": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "iris-module-id": "+hZMMSTG",
            "accept": "*/*",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.visionplus.id/webclient/",
            "accept-language": "en-US,en;q=0.9,ms;q=0.8"
        }
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            data = response.json()
            multirights = data["next"]["vod"]["urls"][0]["url"]
            return multirights
        else:
            print(f"Error: {response.status_code}")
            return None
        
    def get_license_manifest(self, multirights):
        url = "https://www.visionplus.id/streamlocators/multirights/getPlayableUrlAndLicense"
        querystring = {
            "adsProfile": "free",
            "drm": "WV",
            "packaging": "DASH",
            "provisioningData": self.provision_data,
            "url": multirights,
            "userSessionToken": self.token
        }
        headers = {
            "host": "www.visionplus.id",
            "connection": "keep-alive",
            "sec-ch-ua-platform": "\"Windows\"",
            "authorization": self.token,
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "iris-endpoints-version": "VklSVFVBTF9DSEFOTkVMUz0xNjk1NjIyNzE1NTI2LFVTRVJfU0VUVElOR1M9MTc0NDYwMjEyOTExNCxTVUJTQ1JJQkVSX1NFVFRJTkdTPTE3NDQ2MDIxMjkxMTQsUFVSQ0hBU0VfTElTVD0xNzQ0NjAyMTI5MTE0LFVJX0RBVEE9MTc0NDE3NDU1NzIyMSxVU0VSX0RBVEE9MTc0NDYwMjEyOTExNCxSRUNPUkRJTkdfTElTVD0xNzQ0MTc0NTU3MjIxLFVTRVJfUFJPRklMRT0xNzQ0MTc0NTYwNjEyLFNFR01FTlRBVElPTj0xNzQ0MTc0NTY1NDcwLFBFUlNPTkFMX0FDVElWRV9DSEFOTkVMUz0xNzQ0MTc0NjYzNTE0LE9UVF9ERVZJQ0VTPTE3NDQ2MDIxMjkxMjgsREVWSUNFX1NFVFRJTkdTPTE3NDQ2MDIxMjkxMTQsRkFWX0NIQU5ORUxfTElTVD0xNjk2NDQyMDEwMDQyLEFDVElWRV9DSEFOTkVMUz0xNzQ0NjAyMTI5MTE0",
            "sec-ch-ua-mobile": "?0",
            "iris-hw-device-id": self.hardware_id,
            "iris-device-status": "ACTIVE",
            "iris-app-version": "11.3.75",
            "iris-profile-id": "13701824",
            "iris-device-type": "WINDOWS/CHROME",
            "iris-device-class": "PC",
            "iris-device-region": "Indonesia",
            "iris-app-mode": "Normal",
            "dnt": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "iris-module-id": "+hZMMSTG",
            "accept": "*/*",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.visionplus.id/webclient/",
            "accept-language": "en-US,en;q=0.9,ms;q=0.8"
        }
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        manifest_url = data["videos"][0]["url"]
        license_url = data["videos"][0]["licenses"][0]["url"]
        print("=" * 80)
        print("[+] Manifest URL: " + manifest_url)
        print("[+] License URL: " + license_url)
        print("=" * 80)
        return license_url, manifest_url
        
        
    def decrypt_content(self, license_url, in_pssh):
        pssh = PSSH(in_pssh)
        device = Device.load(self.widevine_device)
        cdm = Cdm.from_device(device)
        session_id = cdm.open()
        challenge = cdm.get_license_challenge(session_id, pssh)
        headers = {
            "host": "multidrm.core.verimatrixcloud.net",
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
        response = requests.post(license_url, data=challenge, headers=headers)
        if response.status_code == 200:
            cdm.parse_license(session_id, response.content)
            for key in cdm.get_keys(session_id):
                print(f"[{key.type}] {key.kid.hex}:{key.key.hex()}")
            cdm.close(session_id)
        else:
            print(response.status_code)