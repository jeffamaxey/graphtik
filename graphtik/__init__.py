# Copyright 2016, Yahoo Inc.
# Licensed under the terms of the Apache License, Version 2.0. See the LICENSE file associated with the project for terms.
"""Lightweight :term:`computation` graphs for Python."""

__version__ = "5.7.1"
__release_date__ = "7 Apr 2020, 9:20"
__title__ = "graphtik"
__summary__ = __doc__.splitlines()[0]
__license__ = "Apache-2.0"
__uri__ = "https://github.com/pygraphkit/graphtik"
__author__ = "hnguyen, ankostis"


from .base import NO_RESULT, default_plot_annotator
from .config import (
    abort_run,
    debug,
    evictions_skipped,
    execution_pool,
    get_execution_pool,
    get_plot_annotator,
    is_abort,
    is_debug,
    is_endure_operations,
    is_marshal_tasks,
    is_parallel_tasks,
    is_reschedule_operations,
    is_skip_evictions,
    operations_endured,
    operations_reschedullled,
    plot_annotator,
    reset_abort,
    set_debug,
    set_endure_operations,
    set_execution_pool,
    set_marshal_tasks,
    set_parallel_tasks,
    set_plot_annotator,
    set_reschedule_operations,
    set_skip_evictions,
    tasks_in_parallel,
    tasks_marshalled,
)
from .modifiers import *  # noqa, on purpose to include any new modifiers
from .netop import compose
from .network import AbortedException, IncompleteExecutionError
from .op import operation
