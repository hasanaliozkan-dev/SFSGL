"""Tests for SFSGL."""

import io
import os
import subprocess
import sys
from pathlib import Path

import pytest

from SFSGL import SFSGL, FileGather, FileShare
from SFSGL.sfsgl import as_bool, main, safe_filename

REPO_ROOT = Path(__file__).resolve().parents[1]


def upload(client, *files, ip="10.0.0.1"):
    data = {"file": [(io.BytesIO(content), name) for name, content in files]}
    return client.post("/", data=data, content_type="multipart/form-data", environ_base={"REMOTE_ADDR": ip})


@pytest.fixture
def gathered(tmp_path):
    return tmp_path / "gathered"


def gather_client(folder, **kwargs):
    return FileGather(gathered_folder_path=str(folder), **kwargs).app.test_client()


# safe_filename / as_bool


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("odev.py", "odev.py"),
        ("çalışma.py", "çalışma.py"),
        ("作业.py", "作业.py"),
        ("my homework (1).py", "my_homework__1_.py"),
        ("../../etc/passwd.py", "passwd.py"),
        ("..\\..\\evil.py", "evil.py"),
        (".hidden.py", "hidden.py"),
        ("CON.py", "_CON.py"),
        ("..", ""),
    ],
)
def test_safe_filename(raw, expected):
    assert safe_filename(raw) == expected


@pytest.mark.parametrize("value, expected", [(True, True), (False, False), ("True", True), ("false", False), ("1", True)])
def test_as_bool(value, expected):
    assert as_bool(value) is expected


# FileGather


def test_same_file_name_from_two_students_keeps_both(gathered):
    client = gather_client(gathered)
    upload(client, ("odev.py", b"student A"), ip="10.0.0.1")
    upload(client, ("odev.py", b"student B"), ip="10.0.0.2")
    assert (gathered / "10.0.0.1_odev.py").read_bytes() == b"student A"
    assert (gathered / "10.0.0.2_odev.py").read_bytes() == b"student B"


def test_without_ip_prefix_names_are_never_overwritten(gathered):
    client = gather_client(gathered, add_ip_to_file=False, allow_multiple_upload=True)
    upload(client, ("odev.py", b"first"))
    upload(client, ("odev.py", b"second"))
    assert (gathered / "odev.py").read_bytes() == b"first"
    assert (gathered / "odev_1.py").read_bytes() == b"second"


def test_non_ascii_file_name_is_kept(gathered):
    client = gather_client(gathered, add_ip_to_file=False)
    response = upload(client, ("çalışma.py", b"x"))
    assert (gathered / "çalışma.py").exists()
    assert "çalışma.py" in response.get_data(as_text=True)


def test_path_traversal_stays_inside_folder(gathered, tmp_path):
    client = gather_client(gathered, add_ip_to_file=False)
    upload(client, ("../../evil.py", b"x"))
    assert os.listdir(gathered) == ["evil.py"]
    assert not (tmp_path / "evil.py").exists()


def test_disallowed_extension_shows_error_and_saves_nothing(gathered):
    client = gather_client(gathered)
    response = upload(client, ("virus.exe", b"x"))
    assert '<div class="alert">' in response.get_data(as_text=True)
    assert "File type not allowed" in response.get_data(as_text=True)
    assert os.listdir(gathered) == []


def test_extension_check_is_case_insensitive(gathered):
    client = gather_client(gathered, add_ip_to_file=False, allowed_extension_to_gather=[".PY"])
    upload(client, ("Main.Py", b"x"))
    assert os.listdir(gathered) == ["Main.Py"]


def test_one_file_per_ip_by_default(gathered):
    client = gather_client(gathered)
    upload(client, ("a.py", b"1"))
    response = upload(client, ("b.py", b"2"))
    assert "only upload one file" in response.get_data(as_text=True)
    assert os.listdir(gathered) == ["10.0.0.1_a.py"]
    upload(client, ("c.py", b"3"), ip="10.0.0.2")
    assert len(os.listdir(gathered)) == 2


def test_several_files_in_one_request_rejected_when_multiple_upload_is_off(gathered):
    client = gather_client(gathered)
    response = upload(client, ("a.py", b"1"), ("b.py", b"2"))
    assert "only one file" in response.get_data(as_text=True)
    assert os.listdir(gathered) == []
    # The student wasn't blocked, so a single file still goes through
    upload(client, ("a.py", b"1"))
    assert os.listdir(gathered) == ["10.0.0.1_a.py"]


def test_multiple_upload_saves_every_selected_file(gathered):
    client = gather_client(gathered, allow_multiple_upload=True, add_ip_to_file=False)
    upload(client, ("a.py", b"1"), ("b.py", b"2"), ("c.zip", b"3"))
    assert sorted(os.listdir(gathered)) == ["a.py", "b.py", "c.zip"]


@pytest.mark.parametrize("value", [False, "False", "false"])
def test_bool_options_accept_bools_and_strings(gathered, value):
    gather = FileGather(gathered_folder_path=str(gathered), allow_multiple_upload=value, add_ip_to_file=value)
    assert gather.MULTIPLE_UPLOAD is False
    assert gather.ADD_IP_TO_FILE is False


def test_file_input_allows_multiple_only_when_enabled(gathered):
    single = gather_client(gathered).get("/").get_data(as_text=True)
    multi = gather_client(gathered, allow_multiple_upload=True).get("/").get_data(as_text=True)
    assert " multiple>" not in single
    assert " multiple>" in multi


def test_upload_size_limit(gathered):
    client = gather_client(gathered, max_upload_size_mb=0.001)
    response = upload(client, ("big.zip", b"x" * 5000))
    assert response.status_code == 413
    assert "too large" in response.get_data(as_text=True)
    assert os.listdir(gathered) == []


def test_default_gather_folder_is_not_the_shared_folder(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert FileGather().UPLOAD_FOLDER == str(tmp_path / "gathered")


def test_no_empty_file_name(gathered):
    response = upload(gather_client(gathered), ("", b"x"))
    assert "No selected file" in response.get_data(as_text=True)


# FileShare


def test_missing_shared_folder_is_created(tmp_path):
    shared = tmp_path / "shared"
    response = FileShare(shared_folder_path=str(shared)).app.test_client().get("/")
    assert response.status_code == 200
    assert shared.is_dir()


def test_share_lists_and_serves_only_allowed_files(tmp_path):
    shared = tmp_path / "shared"
    shared.mkdir()
    (shared / "lab1.py").write_text("print('lab')")
    (shared / "secret.env").write_text("KEY=1")
    (shared / "folder.py").mkdir()
    client = FileShare(shared_folder_path=str(shared)).app.test_client()
    page = client.get("/").get_data(as_text=True)
    assert "lab1.py" in page and "secret.env" not in page and "folder.py" not in page
    assert client.get("/download/lab1.py").data == b"print('lab')"
    assert client.get("/download/secret.env").status_code == 404
    assert client.get("/download/..%2F..%2Fetc%2Fpasswd.py").status_code == 404


def test_templates_load_no_missing_assets(tmp_path):
    share_page = FileShare(shared_folder_path=str(tmp_path / "s")).app.test_client().get("/").get_data(as_text=True)
    gather_page = gather_client(tmp_path / "g").get("/").get_data(as_text=True)
    assert "spel/static" not in share_page + gather_page


# CLI


def test_cli_options_reach_sfsgl(monkeypatch):
    monkeypatch.setattr(SFSGL, "start", lambda self: self._init_kwargs)
    kwargs = main(["--gather-ext", "ipynb", "py", "--allow-multiple-upload", "--no-ip-in-filename", "--gather-port", "6002"])
    assert kwargs["allowed_extension_to_gather"] == ["ipynb", "py"]
    assert kwargs["allow_multiple_upload"] is True
    assert kwargs["add_ip_to_file"] is False
    assert kwargs["gathered_port"] == 6002
    assert kwargs["shared_folder_path"] == "shared"


def test_python_dash_m_entry_point():
    env = {**os.environ, "PYTHONPATH": os.pathsep.join(filter(None, [str(REPO_ROOT), os.environ.get("PYTHONPATH")]))}
    result = subprocess.run([sys.executable, "-B", "-m", "SFSGL", "--help"], capture_output=True, text=True, env=env)
    assert result.returncode == 0
    assert "--gather-ext" in result.stdout
