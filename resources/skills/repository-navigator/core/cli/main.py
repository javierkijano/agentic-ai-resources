#!/usr/bin/env python3
import sys
import os
import pathlib
import argparse
import json

# Añadir la lógica al path
sys.path.append(os.path.join(os.path.dirname(__file__), "../logic"))
from explorer import RepoExplorer

def main():
    repo_root = pathlib.Path(__file__).parent.parent.parent.parent.parent
    explorer = RepoExplorer(repo_root)
    
    parser = argparse.ArgumentParser(description="Repository Navigator & Agent Expert")
    subparsers = parser.add_subparsers(dest="command")
    
    subparsers.add_parser("onboarding", help="Show onboarding guide for agents")
    subparsers.add_parser("list", help="List all available resources")
    
    p_find = subparsers.add_parser("find", help="Find skills by tag")
    p_find.add_argument("tag", help="Tag to search for")
    
    args = parser.parse_args()
    
    if args.command == "onboarding":
        print(explorer.get_onboarding_summary())
    elif args.command == "list":
        resources = explorer.list_all_resources()
        print(json.dumps(resources, indent=2))
    elif args.command == "find":
        matches = explorer.find_skill_by_tag(args.tag)
        print(json.dumps(matches, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
