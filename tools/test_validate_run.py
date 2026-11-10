#!/usr/bin/env python3
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""validate_run.py's self-test as a plain test script (reusable-python-ci runs it under coverage)."""

import sys

import validate_run

if __name__ == "__main__":
    sys.exit(validate_run.self_test())
