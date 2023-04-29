from playwright.sync_api import sync_playwright
from playwright._impl._api_types import Error as PlaywrightClientTypeError
from playwright.sync_api._generated import Playwright as SyncPlaywright
from playwright.sync_api._generated import Response as PlaywrightClientResponse
import json


def return_json_response(response: PlaywrightClientResponse, errors_counters: dict, json_responses: list,
                         json_request_urls: list) -> None:
    """
    it parses the different responses that are received when loading the target page, and it only takes those
    that response with a JSON. Also updates the lists and dictionary passed.

    Args:
        response:
        errors_counters: a dictionary of the form:
                        {"not_a_json": 0, "unicode_error": 0, "playwright_client_type_error": 0}
        json_responses: an empty list to stored possible json responses
        json_request_urls: an empty list to stored possible hidden apis urls

    """
    try:
        formatted_response = {"url": response.url, "json_response": response.json()}
        json_responses.append(formatted_response)
        json_request_urls.append(response.url)

    except json.JSONDecodeError:
        errors_counters["not_a_json"] += 1

    except UnicodeDecodeError:
        errors_counters["unicode_error"] += 1

    except PlaywrightClientTypeError:
        errors_counters["playwright_client_type_error"] += 1


def run(playwright_client: SyncPlaywright, url_to_analyze: str) -> tuple:
    """

    Args:
        playwright_client: SyncPlaywright object that makes available chromium
        url_to_analyze: the url passed as an argument when executing the tool

    Returns:
        a tuple containing:
        json_response: a list with dictionaries
        json_request_urls: a list with the requested possible hidden apis
        errors_counters: a dictionary with the counts of different error that could appear
    """
    errors_counters = {"not_a_json": 0, "unicode_error": 0, "playwright_client_type_error": 0}
    json_responses = []
    json_request_urls = []

    chromium = playwright_client.chromium
    browser = chromium.launch(headless=True, slow_mo=8_000, timeout=240_000)
    page = browser.new_page()
    page.on("response",
            lambda response: return_json_response(response=response,
                                                  errors_counters=errors_counters,
                                                  json_responses=json_responses,
                                                  json_request_urls=json_request_urls
                                                  )
            )
    page.goto(url_to_analyze, timeout=240_000)
    browser.close()
    return json_responses, json_request_urls, errors_counters


def main_execution(url_to_analyze: str, file_name: str | None) -> tuple:
    """

    Args:
        url_to_analyze: the url passed as an argument when executing the tool
        file_name: filename to name output files

    Returns:
        a tuple containing:
        json_response: a list with dictionaries
        json_request_urls: a list with the requested possible hidden apis
        errors_counters: a dictionary with the counts of different error that could appear
    """
    with sync_playwright() as playwright_client:
        json_responses, json_request_urls, errors_counters = run(playwright_client, url_to_analyze)

        if json_responses:
            with open(f'{file_name}_responses.json', 'w') as f:
                json.dump(json_responses, f)

            with open(f'{file_name}_urls.txt', 'w') as f:
                f.write('\n'.join(json_request_urls))
    return json_responses, json_request_urls, errors_counters
