import typer
from rich import print as rich_print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from yaspin import yaspin
from yaspin.spinners import Spinners
import inquirer
import json
import re
import os
from playwright.sync_api import sync_playwright
from playwright._impl._api_types import Error as PlaywrightClientTypeError
from playwright.sync_api._generated import Playwright as SyncPlaywright
from playwright.sync_api._generated import Response as PlaywrightClientResponse


app = typer.Typer()

def return_json_response(response: PlaywrightClientResponse, errors_counters: dict, json_responses: list,
                         json_request_urls: list) -> None:
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
    errors_counters = {"not_a_json": 0, "unicode_error": 0, "playwright_client_type_error": 0}
    json_responses = []
    json_request_urls = []

    chromium = playwright_client.chromium
    browser = chromium.launch(headless=True, slow_mo=8_000, timeout=240_000)
    page = browser.new_page()
    page.on("response",
            lambda response: return_json_response(response=response, errors_counters=errors_counters,
                                                  json_responses=json_responses, json_request_urls=json_request_urls))
    page.goto(url_to_analyze, timeout=240_000)
    browser.close()
    return json_responses, json_request_urls, errors_counters


def main_execution(url_to_analyze: str, file_name: str | None) -> tuple:
    with sync_playwright() as playwright_client:
        json_responses, json_request_urls, errors_counters = run(playwright_client, url_to_analyze)

        if json_responses:
            with open(f'{file_name}_responses.json', 'w') as f:
                json.dump(json_responses, f)

            with open(f'{file_name}_urls.txt', 'w') as f:
                f.write('\n'.join(json_request_urls))
    return json_responses, json_request_urls, errors_counters


@app.command()
def main(url_to_analyze: str, verbose_response: bool = typer.Option(False, help="Show additional error information."),
         style: bool = typer.Option(True, help="Prints results without styling (Good for running in notebooks with !)")):
    if style:
        questions = [
            inquirer.Text('file_name', message="Write a name for the file to save the responses of hidden apis (if any)",
                          validate=lambda _, x: re.match(r'^[a-zA-Z0-9_]{1,40}$', x),
                          )
        ]
        file_information: dict = inquirer.prompt(questions)
        file_name = file_information.get('file_name')

        with yaspin(spinner=Spinners.bouncingBar, text=f"Searching for possible hidden apis in {url_to_analyze}...",
                    color="yellow") as spinner:
            json_responses, json_request_urls, errors_counters = main_execution(url_to_analyze, file_name)
            rich_print("\n")
            if json_responses:
                rich_print(Panel.fit(f"For [link={url_to_analyze}]{url_to_analyze}[/link],"
                                f" [bold green]{len(json_responses)}[/bold green] possible hidden apis have been found."
                              f"\n\nYou can find your responses at:   [green]{os.getcwd()}/{file_name}_responses.json[/green]"
                                f"\nand the requested hidden apis at: [green]{os.getcwd()}/{file_name}_urls.txt[/green]",
                                title="Results", title_align="left", padding=1))
            else:
                rich_print(Panel.fit(f"[bold red]No hidden apis have been found.[/bold red]",
                                title="Result", title_align="left", padding=1))

            if verbose_response:
                rich_print("\n")
                console = Console()
                table = Table("Error", "Count")
                for error, count in errors_counters.items():
                    table.add_row(str(error), str(count))
                console.print(Panel.fit(table, title="Additional info", title_align="left", padding=1))

    else:
        file_name = str(typer.prompt("Write a name for the file to save the responses of hidden apis (if any): ",
                                 default="results"))
        print(f"\nSearching for possible hidden apis in {url_to_analyze}...")
        json_responses, json_request_urls, errors_counters = main_execution(url_to_analyze, file_name)
        if json_responses:
            print(f"\nFor {url_to_analyze}, {len(json_responses)} possible hidden apis have been found."
                  f"\n\nYou can find your responses at: {os.getcwd()}/{file_name}_responses.json"
                  f"\nand the requested hidden apis at: {os.getcwd()}/{file_name}_urls.txt")

        else:
            print(f"\nNo hidden apis have been found.")

        if verbose_response:
            print("\n")
            for error, count in errors_counters.items():
                print(f"{error}: {count}")


if __name__ == "__main__":
    typer.run(main)
