#!/bin/bash
set -e

echo "Setting up environment..."
just install

# Load .env into the current shell environment for interactive sessions inside the container
if [ -f /workspaces/resume/.env ]; then
	echo "Loading .env into environment"
	# export each non-empty, non-comment line (safe-ish for simple KEY=VALUE pairs)
	set -o allexport
	# shellcheck disable=SC1090
	source /workspaces/resume/.env
	set +o allexport
fi

echo "Environment setup complete!"
