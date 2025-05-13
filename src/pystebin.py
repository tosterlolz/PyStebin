import typer
import requests
import json
from pathlib import Path
from typing import Optional

__version__ = "1.0.0"
app = typer.Typer()
CONFIG_PATH = Path.home() / ".pystebin_config.json"
PASTEBIN_API_URL = 'https://pastebin.com/api/api_post.php'
REPO_RAW_URL = "https://raw.githubusercontent.com/tosterlolz/PyStebin/main/src/pystebin.py"
LOCAL_PATH = Path(__file__)

def get_latest_version() -> str:
    response = requests.get(REPO_RAW_URL)
    if response.status_code == 200:
        for line in response.text.splitlines():
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"')
    return "unknown"

@app.command()
def update():
    """Check for updates and auto-update pystebin.py"""
    typer.echo("🔎 Checking for updates...")
    latest = get_latest_version()

    if latest == "unknown":
        typer.secho("❌ Failed to fetch version info from GitHub.", fg=typer.colors.RED)
        raise typer.Exit()

    if latest == __version__:
        typer.secho("✅ You already have the latest version.", fg=typer.colors.GREEN)
        return

    typer.secho(f"⬆️  New version available: {latest} (you have {__version__})", fg=typer.colors.YELLOW)

    response = requests.get(REPO_RAW_URL)
    if response.status_code != 200:
        typer.secho("❌ Failed to download the latest version.", fg=typer.colors.RED)
        raise typer.Exit()

    backup_path = LOCAL_PATH.with_suffix(".bak")
    shutil.copy(LOCAL_PATH, backup_path)
    typer.echo(f"🛡 Backup saved as {backup_path.name}")

    with open(LOCAL_PATH, "w", encoding="utf-8") as f:
        f.write(response.text)

    typer.secho("✅ Updated successfully! Restart the tool to use the new version.", fg=typer.colors.GREEN)

def save_config(api_key: str, default_private: int, default_expire: str):
    config = {
        "api_dev_key": api_key,
        "default_private": default_private,
        "default_expire": default_expire
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)
    typer.secho(f"✔ Config saved to {CONFIG_PATH}", fg=typer.colors.GREEN)

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    else:
        typer.secho("⚠️ Config not found. Run `pystebin init` first.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command()
def init():
    """Initialize Pastebin config"""
    typer.echo("=== Pystebin Init ===")
    api_key = typer.prompt("Pastebin API key")
    visibility = typer.prompt("Default visibility (0 = public, 1 = unlisted, 2 = private)", default="1")
    expire = typer.prompt("Default expiration (e.g. N, 10M, 1H, 1D)", default="N")

    try:
        save_config(api_key, int(visibility), expire)
    except ValueError:
        typer.secho("Invalid visibility. Must be 0, 1 or 2.", fg=typer.colors.RED)

@app.command
def help():
    typer.secho("📎 Pystebin - Pastebin CLI uploader", fg=typer.colors.CYAN, bold=True)
    typer.echo()
    typer.secho("Usage:", fg=typer.colors.YELLOW)
    typer.echo("  pystebin [COMMAND] [OPTIONS]")
    typer.echo()
    typer.secho("Commands:", fg=typer.colors.YELLOW)
    typer.echo("  init         Configure API key and defaults")
    typer.echo("  up           Upload text or file to Pastebin")
    typer.echo("  show-config  Show current saved configuration")
    typer.echo("  help         Show this help message")
    typer.echo()
    typer.secho("Upload Options:", fg=typer.colors.YELLOW)
    typer.echo("  --file, -f      Path to a file to upload")
    typer.echo("  --text, -t      Inline text to upload")
    typer.echo("  --title         Title of the paste (optional)")
    typer.echo("  --private       0 = public, 1 = unlisted, 2 = private")
    typer.echo("  --expire        Expiration time (10M, 1H, 1D, N, etc.)")
    typer.echo()
    typer.secho("Examples:", fg=typer.colors.YELLOW)
    typer.echo("  pystebin init")
    typer.echo("  pystebin upload -t \"Hello world\" --title MyPaste")
    typer.echo("  pystebin upload -f script.py --private 0")
    typer.echo()
    typer.secho("Documentation:", fg=typer.colors.YELLOW)
    typer.echo("  https://pastebin.com/doc_api")


@app.command()
def up(
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Path to file to upload"),
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Text to upload directly"),
    title: str = typer.Option("", "--title", help="Title of the paste"),
    private: Optional[int] = typer.Option(None, "--private", help="0 = public, 1 = unlisted, 2 = private"),
    expire: Optional[str] = typer.Option(None, "--expire", help="Expiration: N, 10M, 1H, 1D, etc.")
):
    """Upload text or file to Pastebin"""
    config = load_config()
    content = ""

    if file:
        if not file.exists():
            typer.secho("File not found.", fg=typer.colors.RED)
            raise typer.Exit()
        content = file.read_text(encoding="utf-8")
    elif text:
        content = text
    else:
        typer.secho("You must provide either --file or --text.", fg=typer.colors.RED)
        raise typer.Exit()

    payload = {
        'api_dev_key': config['api_dev_key'],
        'api_option': 'paste',
        'api_paste_code': content,
        'api_paste_name': title,
        'api_paste_private': str(private if private is not None else config.get("default_private", 1)),
        'api_paste_expire_date': expire if expire is not None else config.get("default_expire", "N"),
        'api_paste_format': 'text',
    }

    response = requests.post(PASTEBIN_API_URL, data=payload)
    if response.status_code == 200 and response.text.startswith("http"):
        typer.secho("✅ Paste created:", fg=typer.colors.GREEN)
        typer.echo(response.text)
    else:
        typer.secho(f"❌ Upload failed: {response.text}", fg=typer.colors.RED)

@app.command()
def show_config():
    """Print current config"""
    config = load_config()
    typer.echo(json.dumps(config, indent=2))

if __name__ == "__main__":
    app()
