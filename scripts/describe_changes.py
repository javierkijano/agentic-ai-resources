#!/usr/bin/env python3
import os, sys
os.system('python3 ' + os.path.join(os.path.dirname(__file__), '../resources/skills/repository-manager/core/describe_changes.py ') + ' '.join(sys.argv[1:]))
