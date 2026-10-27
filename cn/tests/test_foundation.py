import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "offline_baseline"))
from cn_web.workspaces import WorkspaceRegistry, WorkspaceDenied
from cn_web.retention import RetentionItem, cleanup_candidates
from store import Store


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.registry = WorkspaceRegistry(self.tmp.name)

    def test_real_existing_stores_are_independent(self):
        a = self.registry.provision("verified-A", quota_bytes=100000000)
        b = self.registry.provision("verified-B", quota_bytes=200000000)
        self.assertNotEqual(a.database_path, b.database_path)
        sa, sb = Store(a.database_path), Store(b.database_path)
        settings = sa.settings()
        settings["products"][0]["name"] = "A private product"
        sa.save_settings(settings)
        self.assertNotEqual(sa.settings()["products"][0]["name"], sb.settings()["products"][0]["name"])
        self.assertEqual(self.registry.resolve("verified-A"), a)
        self.assertEqual(self.registry.resolve("verified-B").quota_bytes, 200000000)

    def test_unknown_and_disabled_cannot_resolve(self):
        with self.assertRaises(WorkspaceDenied):
            self.registry.resolve("unknown")
        a = self.registry.provision("A", quota_bytes=1000)
        self.registry.set_enabled("A", False)
        with self.assertRaises(WorkspaceDenied):
            self.registry.resolve("A")
        self.registry.set_enabled("A", True)
        self.assertEqual(self.registry.resolve("A"), a)

    def test_browser_shaped_identity_is_not_used_as_a_path(self):
        a = self.registry.provision("../../outside", quota_bytes=1000)
        self.assertEqual(a.directory.parent, Path(self.tmp.name) / "workspaces")
        self.assertRegex(a.directory.name, r"^[a-f0-9]{32}$")
        self.assertFalse((Path(self.tmp.name) / "outside").exists())

    def test_duplicate_provision_does_not_replace_mapping(self):
        a = self.registry.provision("A", quota_bytes=1000)
        with self.assertRaises(sqlite3.IntegrityError):
            self.registry.provision("A", quota_bytes=2000)
        self.assertEqual(a, self.registry.resolve("A"))

    def test_bad_quota_does_not_create_workspace(self):
        for amount in (0, -1, 1.1, True, "1000"):
            with self.assertRaises(ValueError):
                self.registry.provision("A", quota_bytes=amount)
        with self.assertRaises(WorkspaceDenied):
            self.registry.resolve("A")

    def test_corrupt_mapping_fails_closed(self):
        self.registry.provision("A", quota_bytes=1000)
        with sqlite3.connect(self.registry.path) as db:
            db.execute("UPDATE workspaces SET workspace_id='../outside' WHERE user_id='A'")
        with self.assertRaises(WorkspaceDenied):
            self.registry.resolve("A")

    def test_directory_symlink_fails_closed(self):
        a = self.registry.provision("A", quota_bytes=1000)
        a.directory.rmdir()
        outside = Path(self.tmp.name) / "other-user"
        outside.mkdir()
        a.directory.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(WorkspaceDenied):
            self.registry.resolve("A")


class RetentionTests(unittest.TestCase):
    now = datetime(2026, 10, 21, tzinfo=timezone.utc)

    def item(self, category, age=61, **kw):
        t = self.now - timedelta(days=age)
        return RetentionItem(category, category, t, t, **kw)

    def test_only_old_unlinked_inactive_temp_items_qualify(self):
        items = [self.item(c) for c in ("cache", "temporary_preview", "abandoned_upload", "source_statement", "calculation", "scheme", "issued_cn", "backup")]
        self.assertEqual(cleanup_candidates(items, now=self.now), ["cache", "temporary_preview", "abandoned_upload"])
        self.assertEqual(cleanup_candidates([self.item("cache", linked_to_saved_work=True), self.item("cache", active=True)], now=self.now), [])

    def test_recent_use_and_cutoff_do_not_qualify(self):
        old = self.item("cache")
        recent = RetentionItem("recent", "cache", old.created_at, self.now)
        self.assertEqual(cleanup_candidates([recent, self.item("cache", age=60)], now=self.now), [])

    def test_naive_dates_and_invalid_age_rejected(self):
        with self.assertRaises(ValueError):
            cleanup_candidates([], now=datetime(2026, 10, 21))
        for age in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                cleanup_candidates([], now=self.now, age_days=age)


if __name__ == "__main__":
    unittest.main()
