from logging import INFO

import pytest


class TestMain:
    @pytest.fixture
    def target_func(self):
        from main import main

        return main

    def test_log_app_version(self, target_func, settings, caplog, mocker):
        caplog.set_level(INFO)
        mocker.patch.object(settings, "APP_VERSION", "0.0.0")

        target_func()
        _, _, actual = caplog.record_tuples[0]

        assert "App Version" in actual
        assert "0.0.0" in actual
