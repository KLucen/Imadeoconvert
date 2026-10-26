import json

import pytest

import settings_store as store


def test_migrates_legacy_without_modifying_it_and_separates_sections(tmp_path):
    legacy, target = tmp_path / "old.json", tmp_path / "new.json"
    original = '{"lang":"zh","quality":79,"fmt":"PNG","check_updates":false}'
    legacy.write_text(original, encoding="utf-8")
    data = store.load(target, legacy)
    data["video"] = {"quality": "high", "preset": "webm", "mute": True}
    store.save(data, target)
    document = json.loads(target.read_text(encoding="utf-8"))
    assert document["schema_version"] == 1
    assert document["general"]["lang"] == "zh"
    assert document["image"]["quality"] == 79
    assert document["video"]["quality"] == "high"
    assert store.load(target, legacy) == data
    assert legacy.read_text(encoding="utf-8") == original


def test_forgetting_settings_removes_both_modes_but_keeps_general(tmp_path):
    path = tmp_path / "settings.json"
    values = {"remember_settings": False, "quality": 90, "quality_mode": "size", "target_size_val": 300,
              "out_dir": "private", "video": {"out_dir": "video", "mute": True}, "engine_dir": "tools"}
    store.save(values, path)
    document = json.loads(path.read_text())
    assert document["image"] == document["video"] == {}
    assert store.load(path)["engine_dir"] == "tools"


@pytest.mark.parametrize("content", ["bad json", "[]", '{"schema_version":2}', '{"schema_version":1,"general":[]}'])
def test_invalid_or_newer_settings_are_preserved(tmp_path, content):
    path = tmp_path / "settings.json"
    path.write_text(content)
    with pytest.raises(store.SettingsError):
        store.load(path)
    with pytest.raises(store.SettingsError):
        store.save({"lang": "en"}, path)
    assert path.read_text() == content


def test_failed_atomic_replace_preserves_old_settings(tmp_path, monkeypatch):
    path = tmp_path / "settings.json"
    store.save({"lang": "en"}, path)
    original = path.read_bytes()
    def denied(*args):
        raise PermissionError("locked")
    monkeypatch.setattr(store.os, "replace", denied)
    with pytest.raises(PermissionError):
        store.save({"lang": "zh"}, path)
    assert path.read_bytes() == original
    assert not list(tmp_path.glob("*.tmp"))


def test_invalid_types_are_not_passed_to_tk(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"schema_version": 1, "general": {"lang": [], "check_updates": "false"},
                               "image": {"quality": "bad", "filename_tokens": 3},
                               "video": {"mute": [], "max_height": "bad"}}))
    assert store.load(path) == {"video": {}}


def test_rename_migrates_both_modes_before_legacy_and_preserves_previous_file(tmp_path, monkeypatch):
    previous, legacy, target = (tmp_path / name for name in ("covert.json", "formatix.json", "convert.json"))
    values = {"lang": "zh", "engine_dir": "my-engine", "quality": 82,
              "video": {"preset": "webm", "mute": True, "max_height": 720}}
    store.save(values, previous)
    original = previous.read_bytes()
    legacy.write_text('{"lang":"en","quality":30}', encoding="utf-8")
    monkeypatch.setattr(store, "SETTINGS_PATH", target)
    monkeypatch.setattr(store, "PREVIOUS_PATH", previous)
    migrated = store.load(target, legacy)
    assert migrated == values
    store.save(migrated, target)
    assert previous.read_bytes() == original
    store.save({"lang": "en", "video": {"preset": "mp4"}}, target)
    assert store.load(target, legacy) == {"lang": "en", "video": {"preset": "mp4"}}


@pytest.mark.parametrize("content", ["invalid", '{"schema_version":2}'])
def test_invalid_previous_settings_are_reported_without_falling_back(tmp_path, content):
    previous, legacy, target = (tmp_path / name for name in ("covert.json", "formatix.json", "convert.json"))
    previous.write_text(content, encoding="utf-8")
    legacy.write_text('{"lang":"zh"}', encoding="utf-8")
    with pytest.raises(store.SettingsError):
        store.load(target, legacy, previous=previous)
    assert previous.read_text(encoding="utf-8") == content
    assert not target.exists()


def test_rename_respects_forgetting_preferences_and_isolates_custom_paths(tmp_path, monkeypatch):
    previous, target = tmp_path / "covert.json", tmp_path / "convert.json"
    previous.write_text(json.dumps({"schema_version": 1,
        "general": {"remember_settings": False, "engine_dir": "tools"},
        "image": {"quality": 90}, "video": {"preset": "webm"}}), encoding="utf-8")
    monkeypatch.setattr(store, "PREVIOUS_PATH", previous)
    assert store.load(target, legacy=None) == {}
    assert store.load(target, legacy=None, previous=previous) == {
        "remember_settings": False, "engine_dir": "tools"}
