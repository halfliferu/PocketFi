from bot.config import settings
import requests
import re
from bot.utils import logger

baseUrl = "https://gm.pocketfi.org"

def get_main_js_format(base_url):
    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        content = response.text
        matches = re.findall(r'src="([^"]*index-[^"]+\.js)"', content)
        if matches:
            # Return all matches, sorted by length (assuming longer is more specific)
            return sorted(set(matches), key=len, reverse=True)
        else:
            return None
    except requests.RequestException as e:
        logger.warning(f"Error fetching the base URL: {e}")
        return None


def get_base_api(url):
    try:
        logger.info("Checking for changes in api...")
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        match = re.findall(r'\b\w+\s*=\s*"(https?://[^\s"]+)"', content)
        header = re.search(r'"x-paf-t":\s*"([A-Za-z0-9=]+)"', content)

        if match and header:
            print(match)
            return [True, match, header.group(1)]
        else:
            logger.info("Could not find 'api' in the content.")
            return None

    except requests.RequestException as e:
        logger.warning(f"Error fetching the JS file: {e}")
        return None


def check_base_url():
    base_url = "https://pocketfi.app/mining"
    main_js_formats = get_main_js_format(base_url)

    if settings.ADVANCED_ANTI_DETECTION:
        r = requests.get("https://raw.githubusercontent.com/halfliferu/PocketFi/refs/heads/main/cgi")
        js_ver = r.text.strip()
        for js in main_js_formats:
            if js_ver in js:
                logger.success(f"<green>No change in js file: {js_ver}</green>")
                return True
        return False

    if main_js_formats:
        for format in main_js_formats:
            logger.info(f"Trying format: {format}")
            full_url = f"https://pocketfi.app{format}"
            result = get_base_api(full_url)
            # print(f"{result} | {baseUrl}")
            if result is None:
                return False

            if baseUrl in result[1] and "https://bot.pocketfi.org" in result[1] and "https://rubot.pocketfi.org" in result[1] and result[2] == "Abvx2NzMTM==" and result[0]:
                logger.success(f"<green>No change in all api!</green>")
                return True

            else:
                if baseUrl in result[1] and result[2] == "Abvx2NzMTM==":

                    logger.success("<green>No change in api!</green>")
                    return True
            return False
        else:
            logger.warning("Could not find 'baseURL' in any of the JS files.")
            return False

    else:
        logger.info("Could not find any main.js format. Dumping page content for inspection:")
        try:
            response = requests.get(base_url)
            print(response.text[:1000])  # Print first 1000 characters of the page
            return False
        except requests.RequestException as e:
            logger.warning(f"Error fetching the base URL for content dump: {e}")
            return False
