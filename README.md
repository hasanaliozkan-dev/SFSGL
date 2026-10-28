![PyPI version](https://img.shields.io/pypi/v/sfsgl.svg)
[![License: MIT](https://img.shields.io/pypi/l/sfsgl.svg)](https://github.com/hasanaliozkan-dev/SFSGL/blob/main/LICENSE)
[![PyPI Downloads](https://static.pepy.tech/badge/sfsgl?label=PyPI%20Downloads)](https://pepy.tech/projects/sfsgl)
![Visitors](https://visitor-badge.laobi.icu/badge?page_id=hasanaliozkan-dev/SFSGL)

# **SFSGL (Simple File Sharing & Gathering Library)**
```bash
███████╗███████╗███████╗ ██████╗ ██╗
██╔════╝██╔════╝██╔════╝██╔════╝ ██║
███████╗█████╗  ███████╗██║  ███╗██║
╚════██║██╔══╝  ╚════██║██║   ██║██║
███████║██║     ███████║╚██████╔╝███████╗
╚══════╝╚═╝     ╚══════╝ ╚═════╝ ╚══════╝
┌───────────────────────────────────────┐
│Simple File Sharing & Gathering Library│
└───────────────────────────────────────┘
```

### Description
SFSGL lets you hand out files to students and collect their solutions over a local network, using nothing but a browser on their side. It starts two small web pages built with Flask:

* a **share page** (port 5001) that lists the files in a folder for students to download, and
* a **gather page** (port 5002) where students upload their solutions.

It was made for programming labs and quizzes: if your lab has an intranet without internet access, students can reach your machine but nothing outside the lab network (no ChatGPT, Copilot, etc.), and you don't need any other tool to distribute and collect the work.

### Features
* One command to start both pages, with every option available on the command line.
* Uploaded files are **never overwritten**. Each file is prefixed with the uploader's IP address, and a taken name gets a `_1`, `_2`, ... suffix.
* Only the file types you allow can be uploaded or downloaded, and students see a clear message when a file is rejected.
* One upload per student (IP address) by default, so a quiz can't be resubmitted.
* Upload size limit (50 MB by default).
* File names in any language are kept as they are (`çalışma.py` stays `çalışma.py`); unsafe characters and folder parts are removed.

### Installation
SFSGL needs Python 3.9 or newer.

```bash
pip install sfsgl
```

### Quick start
1. Put the files you want to share in a folder named `shared`.
2. Run SFSGL from the folder that contains it:

    ```bash
    sfsgl
    ```

    `python -m SFSGL` does the same thing. SFSGL prints the folders it uses, then both pages start.
3. Find your computer's IP address on the lab network (`ipconfig` on Windows, `ipconfig getifaddr en0` on macOS, `hostname -I` on Linux) and give the students these addresses:
    * `http://<your-ip>:5001` to download the shared files
    * `http://<your-ip>:5002` to upload their solutions
4. Uploaded files appear in the `gathered` folder. Stop the server with `Ctrl+C`.

Both folders are created if they don't exist. Your operating system's firewall may ask you to allow incoming connections the first time.

### Command-line options
| Option | Default | Description |
|---|---|---|
| `--shared PATH` | `shared` | Folder whose files students can download |
| `--gathered PATH` | `gathered` | Folder where uploads are saved |
| `--gather-ext EXT [EXT ...]` | `py zip` | File types students may upload |
| `--share-ext EXT [EXT ...]` | `py zip txt` | File types listed on the share page |
| `--allow-multiple-upload` | off | Let a student upload more than one file |
| `--no-ip-in-filename` | off | Don't prefix saved files with the uploader's IP address |
| `--max-upload-mb MB` | `50` | Upload size limit, `0` for no limit |
| `--share-port PORT` | `5001` | Port of the share page |
| `--gather-port PORT` | `5002` | Port of the gather page |

For example, to collect Jupyter notebooks and let students resubmit:

```bash
sfsgl --shared ~/course/week3 --gathered ~/course/week3-submissions --gather-ext ipynb --allow-multiple-upload
```

### Python usage
```python
from SFSGL import SFSGL

if __name__ == "__main__":
    session = SFSGL(
        shared_folder_path="/path/to/assignment",
        gathered_folder_path="/path/to/submissions",
        allowed_extension_to_gather=["py", "ipynb"],
    )
    session.start()
```

Keep the `if __name__ == "__main__":` line: SFSGL runs the two pages in separate processes, and on Windows and macOS those processes re-import your script.

Relative paths are resolved from the folder you run the script in, so absolute paths are the safest choice.

### Configuration parameters
| Parameter | Default | Description |
|---|---|---|
| `shared_folder_path` | `"shared"` | Folder whose files are listed on the share page |
| `gathered_folder_path` | `"gathered"` | Folder where uploaded files are saved |
| `allowed_extension_to_gather` | `["py", "zip"]` | File extensions students may upload |
| `allowed_extension_to_share` | `["py", "zip", "txt"]` | File extensions listed on the share page |
| `allow_multiple_upload` | `False` | Allow more than one upload per IP address |
| `add_ip_to_file` | `True` | Prefix saved file names with the uploader's IP address |
| `max_upload_size_mb` | `50` | Upload size limit in MB, `0` or `None` for no limit |
| `shared_port` | `5001` | Port of the share page |
| `gathered_port` | `5002` | Port of the gather page |

`allow_multiple_upload` and `add_ip_to_file` accept `True`/`False` as well as the strings `"True"`/`"False"` used by older versions. Extensions are case-insensitive and may be written with or without the dot.

`FileShare` and `FileGather` can also be used on their own, for example `FileGather(gathered_folder_path="submissions", port=5002).run()`.

### How uploaded files are named
With the default settings, a file `odev.py` uploaded from `192.168.1.23` is saved as `192.168.1.23_odev.py`. If that name is already taken, the next one becomes `192.168.1.23_odev_1.py`, so no submission is ever replaced. With `add_ip_to_file=False` (or `--no-ip-in-filename`) the original name is used, with the same `_1`, `_2`, ... rule.

### Docker
The image stores everything under `/data`. Mount a folder there so the shared files are visible to the container and the submissions survive it:

```bash
docker build -t sfsgl .
docker run -p 5001:5001 -p 5002:5002 -v "$(pwd)/sfsgl-data:/data" sfsgl
```

Put the files to share in `sfsgl-data/shared`. Submissions are written to `sfsgl-data/gathered`.

### Limits and security notes
* SFSGL has no login. Anyone who can reach your computer on the network can open both pages, so use it on a lab or classroom network, never on a machine exposed to the internet.
* The one-upload-per-IP rule only lasts as long as the server runs. Restarting SFSGL lets everyone upload again, and students behind the same router or proxy share one IP address.
* SFSGL uses Flask's built-in server, which handles a classroom comfortably. Flask prints a "development server" warning at start-up, which you can ignore for this use.

### Development
```bash
git clone https://github.com/hasanaliozkan-dev/SFSGL.git
cd SFSGL
pip install -e . pytest
pytest
```

### Contribution
You can contribute by forking the repository and sending a pull request, and report bugs or request features by opening an issue. Security reports are especially welcome: if you find a problem, please open an issue or send a fix.

### Citation
If you use SFSGL in your research or teaching, please cite it using [CITATION.cff](https://github.com/hasanaliozkan-dev/SFSGL/blob/main/CITATION.cff) (GitHub's "Cite this repository" button generates the reference for you).

### License
SFSGL is released under the MIT License. See [LICENSE](https://github.com/hasanaliozkan-dev/SFSGL/blob/main/LICENSE) for the full text.
