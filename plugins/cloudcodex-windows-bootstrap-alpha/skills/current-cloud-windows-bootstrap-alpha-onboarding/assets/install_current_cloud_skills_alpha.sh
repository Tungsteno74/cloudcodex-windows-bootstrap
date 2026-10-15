#!/usr/bin/env bash
# Alpha hypothesis: install a pinned copy of the five skill directories during
# Current Cloud environment onboarding. This does not register a plugin.
set -euo pipefail

readonly ALPHA_LABEL='current-cloud-skills-alpha'
readonly REPOSITORY='https://github.com/Tungsteno74/cloudcodex-windows-bootstrap.git'
readonly SOURCE_SHA='c987a7c6e02694ecb60c2965135dd85f56898525'
readonly PLUGIN_VERSION='0.6.7'
readonly PLUGIN_PATH='plugins/cloudcodex-windows-bootstrap'
readonly DESTINATION_ROOT="${HOME:?HOME must be set}/.agents/skills"
readonly SKILLS=(
  'codex-cloud-windows-check-probe'
  'github-actions-windows-bootstrap'
  'windows-ci-ephemeral-branch'
  'windows-ci-fork-fallback'
  'windows-ci-managed-branch'
)

temporary_root=''
declare -a installed_skills=()
install_complete=false

log() {
  printf '[%s] %s\n' "$ALPHA_LABEL" "$*"
}

fail() {
  log "ERROR: $*" >&2
  exit 1
}

cleanup() {
  local status=$?
  if ! "$install_complete"; then
    local skill
    for skill in "${installed_skills[@]}"; do
      rm -rf -- "$DESTINATION_ROOT/$skill"
    done
  fi
  if [[ -n "$temporary_root" && -d "$temporary_root" ]]; then
    rm -rf -- "$temporary_root"
  fi
  exit "$status"
}
trap cleanup EXIT

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "required command not found: $1"
}

assert_real_directory_tree() {
  local directory=$1
  [[ -d "$directory" && ! -L "$directory" ]] || fail "not a real directory: $directory"
  if find "$directory" -type l -print -quit | grep -q .; then
    fail "symlink found in skill tree: $directory"
  fi
}

assert_file() {
  [[ -f "$1" && ! -L "$1" ]] || fail "required file is missing: $1"
}

validate_package() {
  local source_root=$1
  local skills_root="$source_root/$PLUGIN_PATH/skills"
  local skill

  assert_file "$source_root/$PLUGIN_PATH/plugin.json"
  grep -Eq '"version"[[:space:]]*:[[:space:]]*"0\.6\.7"' \
    "$source_root/$PLUGIN_PATH/plugin.json" || fail "plugin version is not $PLUGIN_VERSION"
  [[ $(find "$skills_root" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ') == ${#SKILLS[@]} ]] ||
    fail "package does not contain exactly the required five skill directories"

  for skill in "${SKILLS[@]}"; do
    assert_real_directory_tree "$skills_root/$skill"
    local skill_file="$skills_root/$skill/SKILL.md"
    assert_file "$skill_file"
    local first_line=''
    IFS= read -r first_line < "$skill_file" || fail "cannot read frontmatter: $skill"
    first_line=${first_line%$'\r'}
    [[ "$first_line" == '---' ]] || fail "SKILL.md frontmatter missing: $skill"
    grep -Eq "^name:[[:space:]]*$skill[[:space:]]*$" "$skill_file" ||
      fail "SKILL.md name mismatch: $skill"
    grep -Eq '^description:[[:space:]]*[^[:space:]]' "$skill_file" ||
      fail "SKILL.md description missing: $skill"
    assert_file "$skills_root/$skill/agents/openai.yaml"
  done

  assert_file "$skills_root/codex-cloud-windows-check-probe/references/probe-marker.txt"
  for skill in github-actions-windows-bootstrap windows-ci-ephemeral-branch \
    windows-ci-fork-fallback windows-ci-managed-branch; do
    assert_file "$skills_root/$skill/assets/windows-workflow.yml"
    assert_file "$skills_root/$skill/references/execution-contract.md"
    assert_file "$skills_root/$skill/references/github-access.md"
    assert_file "$skills_root/$skill/references/github-constraints.md"
  done
}

trees_are_identical() {
  local source=$1
  local destination=$2
  [[ -d "$destination" && ! -L "$destination" ]] || return 1
  ! find "$destination" -type l -print -quit | grep -q . || return 1
  diff -qr "$source" "$destination" >/dev/null
}

require_command git
require_command cp
require_command diff
require_command find
require_command grep
require_command mktemp
require_command mv

temporary_root=$(mktemp -d "${TMPDIR:-/tmp}/${ALPHA_LABEL}.XXXXXX") || fail 'could not create temporary directory'
source_override=${CURRENT_CLOUD_SKILLS_ALPHA_SOURCE:-}

if [[ -n "$source_override" ]]; then
  [[ -d "$source_override" ]] || fail "local source override is not a directory: $source_override"
  source_root=$(cd "$source_override" && pwd -P)
  log "using explicit local source override for offline testing: $source_root"
else
  source_root="$temporary_root/source"
  log "cloning pinned public source $SOURCE_SHA"
  git clone --quiet --no-checkout "$REPOSITORY" "$source_root"
  git -C "$source_root" checkout --quiet --detach "$SOURCE_SHA"
  [[ $(git -C "$source_root" rev-parse HEAD) == "$SOURCE_SHA" ]] || fail 'checked out source SHA differs from pin'
fi

validate_package "$source_root"
skills_root="$source_root/$PLUGIN_PATH/skills"

for skill in "${SKILLS[@]}"; do
  destination="$DESTINATION_ROOT/$skill"
  if [[ -e "$destination" || -L "$destination" ]]; then
    if trees_are_identical "$skills_root/$skill" "$destination"; then
      log "already installed and identical: $skill"
    else
      fail "collision at $destination; refusing to overwrite an existing skill"
    fi
  fi
done

stage_root="$temporary_root/stage"
mkdir "$stage_root"
for skill in "${SKILLS[@]}"; do
  cp -R -- "$skills_root/$skill" "$stage_root/$skill"
  assert_real_directory_tree "$stage_root/$skill"
done

mkdir -p -- "$DESTINATION_ROOT"
for skill in "${SKILLS[@]}"; do
  destination="$DESTINATION_ROOT/$skill"
  if [[ ! -e "$destination" && ! -L "$destination" ]]; then
    mv -- "$stage_root/$skill" "$destination"
    installed_skills+=("$skill")
    log "installed directory copy: $skill"
  fi
done

install_complete=true
log "installed or verified five alpha skill directories; no plugin registration was performed"
