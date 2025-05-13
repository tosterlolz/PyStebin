# 🚀 PyStebin

**PyStebin** is a simple and modern Pastebin uploader for the terminal. It features a friendly CLI, TUI, configuration saving, and auto-updating from GitHub.

---

## 📦 Installation

### 🔧 Install via Git

```bash
git clone https://github.com/tosterlolz/PyStebin.git
cd PyStebin
pip install .
```
## 🛠️ Configuration
Before using PyStebin, you need to set up your Pastebin API key and some defaults.

Run the following command to configure:

📝 Usage
```bash
pystebin init # You will need your API key here (https://pastebin.com/doc_api)
pystebin upload -t "print('Hello World')" --title "My First Paste"
pystebin upload -f /path/to/file.py --private 0
pystebin show-config
pystebin update
```

# 🔧 Update Instructions
To update PyStebin, simply run:
```bash
pystebin update
```
It will check for the latest version on GitHub and update automatically.

## 💡 Features
* Auto-Update: Automatically checks for and applies updates from GitHub.

* Easy Configuration: Save your Pastebin API key and default settings.

## 🛠️ Development
If you'd like to contribute or modify the code, feel free to fork the repository and make a pull request.