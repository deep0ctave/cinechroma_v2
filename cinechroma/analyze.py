""" This file is part of cinechroma.
See README.md for:
- project structure
- workflow
- responsibilities
- data model
"""


def run_analysis(args):
	print(f"[analyze] Would analyze {args.video} with k={getattr(args, 'k', 5)}")
