#!/usr/bin/env python3
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""import_anthocnet.py's self-test as a plain test script (reusable-python-ci runs it under coverage)."""

import sys

import import_anthocnet

if __name__ == "__main__":
    sys.exit(import_anthocnet.self_test())
