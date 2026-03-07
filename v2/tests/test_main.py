from pathlib import Path

from justpath.main import PathDict


def test_from_list(tmp_path):
    p = PathDict.from_list([tmp_path / "a", tmp_path / "b"])
    assert len(p) == 2


def test_guarantee_homedir():
    p = PathDict.from_list(["~"])
    assert next(p.path_items()).dir.resolved == str(Path.home())


def test_with_simlinks(tmp_path):
    a = tmp_path / "a"
    a.mkdir()
    b = Path(tmp_path / "b")
    b.symlink_to(a, target_is_directory=True)
    assert a.exists()
    assert b.exists()
    print(a)
    print(b)
    print(b.resolve())
    p = PathDict.from_list([a, b])
    m = list(p.path_items())
    assert m[0].duplicates.raw == 1
    assert m[1].duplicates.raw == 1
    assert m[1].duplicates.resolved == 2
    p.purge_duplicates()
    assert len(p) == 1
