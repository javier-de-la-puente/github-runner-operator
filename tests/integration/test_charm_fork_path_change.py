# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for github-runner charm with a fork repo.

Tests a path change in the repo.
"""
import logging

import pytest
from github.Repository import Repository
from juju.application import Application
from juju.model import Model
from ops.model import ActiveStatus

from charm_state import PATH_CONFIG_NAME
from tests.integration.helpers.common import reconcile
from tests.integration.helpers.openstack import OpenStackInstanceHelper

logger = logging.getLogger(__name__)


@pytest.mark.openstack
@pytest.mark.asyncio
@pytest.mark.abort_on_fail
async def test_path_config_change(
    model: Model,
    app_with_forked_repo: Application,
    github_repository: Repository,
    path: str,
    instance_helper: OpenStackInstanceHelper,
) -> None:
    """
    arrange: A working application with one runner in a forked repository.
    act: Change the path configuration to the main repository and reconcile runners.
    assert: No runners connected to the forked repository and one runner in the main repository.
    """
    logger.info("test_path_config_change")
    await model.wait_for_idle(
        apps=[app_with_forked_repo.name], status=ActiveStatus.name, idle_period=30, timeout=10 * 60
    )

    unit = app_with_forked_repo.units[0]

    logger.info("Ensure there is a runner (this calls reconcile)")
    await instance_helper.ensure_charm_has_runner(app_with_forked_repo)
    logger.info("after ensure_charm_has_runner")
    instance_helper.log_runners(unit)

    logger.info("Change Path config option to %s", path)
    await app_with_forked_repo.set_config({PATH_CONFIG_NAME: path})
    instance_helper.log_runners(unit)

    status = await model.get_status()
    logger.info(" status : %s", status)

    logger.info("Reconciling (again)")
    await reconcile(app=app_with_forked_repo, model=model)

    logger.info("after Reconciling (again)")
    instance_helper.log_runners(unit)

    status = await model.get_status()
    logger.info("JAVI status 2: %s", status)

    runner_names = await instance_helper.get_runner_names(unit)
    logger.info("runners: %s", runner_names)
    assert len(runner_names) == 1
    #this will crash if there is not exactly one
    logger.info("runner info: %s", instance_helper._get_single_runner(unit))

    runner_name = runner_names[0]

    runners_in_repo = github_repository.get_self_hosted_runners()
    logger.info("runners in github repo: %s", list(runners_in_repo))

    runner_in_repo_with_same_name = tuple(
        filter(lambda runner: runner.name == runner_name, runners_in_repo)
    )

    assert len(runner_in_repo_with_same_name) == 1, "there has to be 1 runner in the repo"
