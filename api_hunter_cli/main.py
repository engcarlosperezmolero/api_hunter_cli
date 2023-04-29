import typer
from rich import print as rich_print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from yaspin import yaspin
from yaspin.spinners import Spinners
import inquirer
import re
import os
from api_hunter_cli.playwright_custom import main_execution


app = typer.Typer()


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
        rich_print(f"\nSearching for possible [yellow]hidden apis[/yellow] in [blue]{url_to_analyze}[/blue] ...")
        json_responses, json_request_urls, errors_counters = main_execution(url_to_analyze, file_name)
        if json_responses:
            rich_print(f"\nFor {url_to_analyze} , {len(json_responses)} possible hidden apis have been found."
                  f"\n\nYou can find your responses at: [green]{os.getcwd()}/{file_name}_responses.json[/green]"
                  f"\nand the requested hidden apis at: [green]{os.getcwd()}/{file_name}_urls.txt[/green]")

        else:
            rich_print(f"\n[bold red]No hidden apis have been found.[/bold red]")

        if verbose_response:
            print("\n")
            for error, count in errors_counters.items():
                rich_print(f"{error}: [red]{count}[/red]")


if __name__ == "__main__":
    typer.run(main)
