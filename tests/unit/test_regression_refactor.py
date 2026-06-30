"""
Regression tests for scaffold restructure (7183f53) and uv migration (6ee1a11).

Verify that the two major refactors did not cause functional drift
in package importability, CLI resolution, config loading, or the
library API contract.
"""

import pytest

# ================================================================
# PACKAGE IMPORTABILITY
# ================================================================


class TestPackageImport:
    """Package root is importable with expected attributes."""

    @pytest.mark.unit
    def test_import_editor_assistant(self):
        import editor_assistant

        assert hasattr(editor_assistant, "__version__")

    @pytest.mark.unit
    def test_version_consistency(self):
        import editor_assistant
        from editor_assistant.config import __version__ as cfg_ver

        assert editor_assistant.__version__ == cfg_ver

    @pytest.mark.unit
    def test_version_format(self):
        import editor_assistant

        ver = editor_assistant.__version__
        assert isinstance(ver, str)
        parts = ver.split(".")
        assert len(parts) >= 2

    @pytest.mark.unit
    def test_all_submodules_importable(self):
        # NOTE: These imports verify package structure only.
        # All submodules must be free of side effects at import time.
        from editor_assistant import cli  # noqa: F401
        from editor_assistant import main  # noqa: F401
        from editor_assistant import llm_client  # noqa: F401
        from editor_assistant import md_processor  # noqa: F401
        from editor_assistant import md_converter  # noqa: F401
        from editor_assistant import clean_html_to_md  # noqa: F401
        from editor_assistant import content_validation  # noqa: F401
        from editor_assistant import data_models  # noqa: F401
        from editor_assistant import utils  # noqa: F401
        from editor_assistant import config  # noqa: F401
        from editor_assistant import storage  # noqa: F401
        from editor_assistant import tasks  # noqa: F401


# ================================================================
# CLI ENTRY POINTS
# ================================================================


class TestCLIEntryPoints:
    """CLI entry point functions exist and are callable."""

    @pytest.mark.unit
    def test_editor_assistant_cli_main(self):
        from editor_assistant.cli import main

        assert callable(main)

    @pytest.mark.unit
    def test_any2md_entry_point(self):
        from editor_assistant.md_converter import main

        assert callable(main)

    @pytest.mark.unit
    def test_html2md_entry_point(self):
        from editor_assistant.clean_html_to_md import main

        assert callable(main)


# ================================================================
# CONFIG LOADING
# ================================================================


class TestConfigLoading:
    """Config files load from installed package."""

    @pytest.mark.unit
    def test_llm_config_loads(self):
        from editor_assistant.config.llm_models import load_all_settings

        settings = load_all_settings()
        assert len(settings) >= 5

    @pytest.mark.unit
    def test_prompt_templates_exist(self):
        from editor_assistant.config.load_prompt import PromptLoader

        loader = PromptLoader()
        templates = list(loader.prompts_dir.glob("*.txt"))
        assert len(templates) >= 3

    @pytest.mark.unit
    def test_constants_exports(self):
        from editor_assistant.config.constants import (
            MAX_API_RETRIES,
            API_REQUEST_TIMEOUT_SECONDS,
            MIN_REQUEST_INTERVAL_SECONDS,
            MAX_REQUESTS_PER_MINUTE,
            INITIAL_RETRY_DELAY_SECONDS,
        )

        assert isinstance(MAX_API_RETRIES, int)
        assert isinstance(API_REQUEST_TIMEOUT_SECONDS, (int, float))
        assert isinstance(MIN_REQUEST_INTERVAL_SECONDS, (int, float))
        assert isinstance(MAX_REQUESTS_PER_MINUTE, int)
        assert isinstance(INITIAL_RETRY_DELAY_SECONDS, (int, float))


# ================================================================
# LIBRARY API CONTRACT
# ================================================================


class TestLibraryAPIContract:
    """Public API that external projects depend on."""

    @pytest.mark.unit
    def test_new_llm_core_import_path_available(self):
        from llm_exec_core import LLMClient

        assert hasattr(LLMClient, "generate_response")

    @pytest.mark.unit
    def test_legacy_llm_client_import_path_still_available(self):
        from editor_assistant.llm_client import LLMClient

        assert hasattr(LLMClient, "generate_response")

    @pytest.mark.unit
    def test_legacy_llm_models_import_path_still_available(self):
        from editor_assistant.config.llm_models import get_supported_models

        assert isinstance(get_supported_models(), list)

    @pytest.mark.unit
    def test_legacy_llm_constants_still_exported_from_app_constants(self):
        from editor_assistant.config.constants import MAX_API_RETRIES

        assert isinstance(MAX_API_RETRIES, int)

    @pytest.mark.unit
    def test_llm_client_has_generate_response(self):
        from editor_assistant.llm_client import LLMClient

        assert hasattr(LLMClient, "generate_response")

    @pytest.mark.unit
    def test_llm_client_has_get_supported_models(self):
        from editor_assistant.llm_client import LLMClient

        assert hasattr(LLMClient, "get_supported_models")

    @pytest.mark.unit
    def test_get_model_details_callable(self):
        from editor_assistant.config.llm_models import (
            get_model_details,
        )

        assert callable(get_model_details)

    @pytest.mark.unit
    def test_get_supported_models_returns_list(self):
        from editor_assistant.config.llm_models import (
            get_supported_models,
        )

        models = get_supported_models()
        assert isinstance(models, list)
        assert len(models) > 0
        assert all(isinstance(m, str) for m in models)

    @pytest.mark.unit
    def test_get_model_details_returns_tuple(self):
        from editor_assistant.config.llm_models import (
            get_model_details,
            get_supported_models,
        )

        model = get_supported_models()[0]
        result = get_model_details(model)
        assert isinstance(result, tuple)
        assert len(result) == 2


# ================================================================
# TASK SYSTEM
# ================================================================


class TestTaskSystem:
    """TaskRegistry discovers all built-in tasks."""

    @pytest.mark.unit
    def test_registry_has_all_tasks(self):
        from editor_assistant.tasks import TaskRegistry

        tasks = TaskRegistry.list_tasks()
        assert "brief" in tasks
        assert "outline" in tasks
        assert "translate" in tasks

    @pytest.mark.unit
    def test_tasks_are_callable(self):
        from editor_assistant.tasks import TaskRegistry

        for name in ["brief", "outline", "translate"]:
            task = TaskRegistry.get(name)
            assert hasattr(task, "validate")
            assert hasattr(task, "build_prompt")
            assert hasattr(task, "post_process")
