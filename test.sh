#!/usr/bin/env bash

set -u

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGETS=("$ROOT_DIR/auth_service" "$ROOT_DIR/order_service" "$ROOT_DIR/product_service")

EXIT_CODE=0

print_step() {
	echo
	echo "==> $1"
}

run_check() {
	local title="$1"
	shift

	print_step "$title"
	if "$@"; then
		echo "[OK] $title"
	else
		echo "[FAIL] $title"
		EXIT_CODE=1
	fi
}

require_cmd() {
	local cmd="$1"
	if ! command -v "$cmd" >/dev/null 2>&1; then
		echo "Required command '$cmd' not found in PATH"
		exit 2
	fi
}

require_cmd black
require_cmd mypy
require_cmd ruff

run_check "Black format check" black --check "${TARGETS[@]}"
run_check "Mypy type check" mypy "${TARGETS[@]}"
run_check "Ruff lint check" ruff check "${TARGETS[@]}"

exit "$EXIT_CODE"
