#!/bin/bash

# Script to run the Fennel Music REPL

# Ensure this script is executable:
# chmod +x run-repl.sh

# --- Configuration ---
FENNEL_SCRIPT_NAME="repl.fnl"
DEFAULT_DB_PATH_CHECK="../devp/wip-db.sql" # Relative to this script's directory

# --- Helper Functions ---
print_error() {
    echo "ERROR: $1" >&2
}

print_info() {
    echo "INFO: $1"
}

# 1. Check for Fennel
if ! command -v fennel &> /dev/null; then
    print_error "Fennel command not found."
    print_info "Please install Fennel. See: https://fennel-lang.org/setup"
    print_info "Example (LuaRocks): luarocks install fennel"
    exit 1
fi
print_info "Fennel found: $(command -v fennel)"

# 2. Check for LuaSQLite3
# Attempt to require lsqlite3 using Lua.
if ! lua -e "require('lsqlite3')" &> /dev/null; then
    print_error "Lua module 'lsqlite3' not found."
    print_info "Please install lsqlite3 for Lua."
    print_info "Example (LuaRocks): sudo luarocks install lsqlite3"
    print_info "Note: You might need to install development packages for SQLite3 first,"
    print_info "e.g., on Debian/Ubuntu: sudo apt-get install libsqlite3-dev"
    exit 1
fi
print_info "LuaSQLite3 module found."

# 3. Navigate to script directory
# This ensures that relative paths (like for repl.fnl and the default DB) work correctly.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit 1 # Exit if cd fails

print_info "Changed directory to: $(pwd)"

# Check if the Fennel REPL script exists
if [ ! -f "$FENNEL_SCRIPT_NAME" ]; then
    print_error "Fennel REPL script '$FENNEL_SCRIPT_NAME' not found in $(pwd)."
    exit 1
fi
print_info "Fennel REPL script '$FENNEL_SCRIPT_NAME' found."

# Optional: Check if the default database path seems plausible (won't check if DB is valid)
if [ ! -f "$DEFAULT_DB_PATH_CHECK" ]; then
    print_info "Warning: Default database at '$DEFAULT_DB_PATH_CHECK' not found. The REPL might fail to connect unless a different path is specified or the DB is created."
fi

# 4. Launch Fennel REPL
print_info "Launching Fennel REPL with '$FENNEL_SCRIPT_NAME'..."
print_info "Type '(quit)' or press Ctrl+D to exit the REPL."
print_info "The 'db' variable should be available if the database connection was successful."
print_info "---------------------------------------------------------------------"

# Execute Fennel, loading the repl.fnl script and then starting an interactive REPL session.
# `fennel --load <file>` loads the file.
# `fennel --repl` starts a REPL.
# Combining them:
fennel --load "$FENNEL_SCRIPT_NAME" --repl

# Alternative ways to launch, depending on Fennel version and desired behavior:
# fennel -l "$FENNEL_SCRIPT_NAME" --repl  # -l is short for --load
# fennel "$FENNEL_SCRIPT_NAME" --repl     # If fennel treats the first non-option arg as file to load before --repl
# fennel -i "$FENNEL_SCRIPT_NAME"         # -i is for interactive mode after running script (might exit if script doesn't loop)

print_info "---------------------------------------------------------------------"
print_info "Fennel REPL exited."
exit 0
