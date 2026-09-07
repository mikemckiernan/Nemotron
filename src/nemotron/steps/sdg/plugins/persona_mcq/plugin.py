# Copyright (c) 2026, NVIDIA CORPORATION.  All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Entry point descriptor for the Persona MCQ Data Designer plugin."""

from data_designer.plugins.plugin import Plugin, PluginType

persona_mcq = Plugin(
    impl_qualified_name="nemotron.steps.sdg.plugins.persona_mcq.generator.PersonaMCQGenerator",
    config_qualified_name="nemotron.steps.sdg.plugins.persona_mcq.config.PersonaMCQConfig",
    plugin_type=PluginType.COLUMN_GENERATOR,
)
