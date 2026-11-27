#!/usr/bin/env bash
# Exercises deploy.sh stack selection without a production host or Docker daemon.
# Fake docker/curl/sleep commands record the Compose invocation and let the
# deploy script complete its control flow in an isolated temporary directory.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TMP/deployment/scripts" "$TMP/deployment/compose" "$TMP/bin"
cp "$REPO_ROOT/deployment/scripts/deploy.sh" "$TMP/deployment/scripts/deploy.sh"
cat > "$TMP/deployment/scripts/health-check.sh" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
chmod +x "$TMP/deployment/scripts/health-check.sh"

cat > "$TMP/bin/docker" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$DOCKER_CALL_LOG"
EOF
cat > "$TMP/bin/curl" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
cat > "$TMP/bin/sleep" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
chmod +x "$TMP/bin/docker" "$TMP/bin/curl" "$TMP/bin/sleep"

export PATH="$TMP/bin:$PATH"
export DOCKER_CALL_LOG="$TMP/docker.log"

assert_stack() {
  local frontend="$1"
  local backend="$2"
  local expected_frontend_overlay="$3"
  local expected_backend_overlay="$4"

  : > "$DOCKER_CALL_LOG"
  cat > "$TMP/deployment/compose/.env.production" <<EOF
FRONTEND_STACK=$frontend
BACKEND_STACK=$backend
EOF
  rm -f "$TMP/deployment/compose/"*-versions.env
  "$TMP/deployment/scripts/deploy.sh" frontend-sha backend-sha

  if [ "$expected_frontend_overlay" = "yes" ]; then
    grep -q 'compose.production.vue.yaml' "$DOCKER_CALL_LOG"
  else
    ! grep -q 'compose.production.vue.yaml' "$DOCKER_CALL_LOG"
  fi
  if [ "$expected_backend_overlay" = "yes" ]; then
    grep -q 'compose.production.fastapi.yaml' "$DOCKER_CALL_LOG"
  else
    ! grep -q 'compose.production.fastapi.yaml' "$DOCKER_CALL_LOG"
  fi
}

assert_stack react express no no
assert_stack vue express yes no
assert_stack react fastapi no yes
assert_stack vue fastapi yes yes

# Explicit positional stack arguments must override generated defaults.
cat > "$TMP/deployment/compose/.env.production" <<'EOF'
FRONTEND_STACK=react
BACKEND_STACK=express
EOF
: > "$DOCKER_CALL_LOG"
rm -f "$TMP/deployment/compose/"*-versions.env
"$TMP/deployment/scripts/deploy.sh" frontend-sha backend-sha vue fastapi
grep -q 'compose.production.vue.yaml' "$DOCKER_CALL_LOG"
grep -q 'compose.production.fastapi.yaml' "$DOCKER_CALL_LOG"

echo "deploy.sh stack selection passed for all four defaults and explicit overrides."
