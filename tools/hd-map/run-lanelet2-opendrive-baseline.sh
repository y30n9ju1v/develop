#!/usr/bin/env bash
# Run the Tier IV Lanelet2 -> OpenDRIVE baseline and keep its audit artifacts.
#
# Usage:
#   bash tools/hd-map/run-lanelet2-opendrive-baseline.sh path/to/map.osm [output-dir]
#
# Prerequisites: Docker Desktop with Compose v2, Git, and network access for
# the first clone/build.  On any non-x86_64 host (Apple Silicon macOS, ARM64
# Linux, ...) this intentionally builds/runs the upstream x86_64 image
# because the bundled CARLA wheel is x86_64-only.
#
# Environment variables (all optional):
#   TIER_IV_L2O_DIR         Where to keep the upstream checkout.
#                           Default: ${TMPDIR:-/tmp}/autoware_lanelet2_to_opendrive
#   TIER_IV_L2O_REF         Git ref (commit/tag/branch) to pin the checkout to.
#                           Default: whatever was already cloned there (or the
#                           upstream default branch tip on first clone).
#   TIER_IV_L2O_TARGET      Conversion target passed to the tool (carla or the
#                           tool's generic ASAM OpenDRIVE target).
#                           Default: carla
#   TIER_IV_L2O_ORIGIN_LAT  Latitude of the map's projection origin.
#   TIER_IV_L2O_ORIGIN_LON  Longitude of the map's projection origin.
#                           Both are required together. The tool's `map=`
#                           Hydra config is what actually carries the CRS
#                           origin (MGRS grid or lat/lon) for a given map --
#                           it is NOT just a label for the input file. When
#                           both are set, this script generates a throwaway
#                           map config with this origin and points the tool
#                           at it. When unset, the run falls back to the
#                           tool's bundled `example` map config (see its
#                           conf/map/example.yaml for the origin that
#                           implies) and prints a loud warning, since that
#                           origin is almost certainly wrong for your map.
#   TIER_IV_L2O_ORIGIN_ALT  Altitude for the generated origin. Default: 0.
#
# Each run writes its artifacts into a fresh, timestamped subdirectory under
# [output-dir] instead of overwriting a shared directory, and records a
# manifest.txt with the input hash, CRS origin, and upstream commit so
# results stay traceable to what actually produced them.

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 path/to/map.osm [output-dir]" >&2
  exit 64
fi

input_map="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
if [[ ! -f "$input_map" ]]; then
  echo "input map not found: $input_map" >&2
  exit 66
fi

sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    shasum -a 256 "$1" | awk '{print $1}'
  fi
}

output_root="${2:-$(pwd)/artifacts/lanelet2-opendrive-baseline}"
mkdir -p "$output_root"
output_root="$(cd "$output_root" && pwd)"

map_name="$(basename "$input_map" .osm)"
input_name="$(basename "$input_map")"
output_name="${map_name}.xodr"

run_id="$(date -u +%Y%m%dT%H%M%SZ)"
output_dir="$output_root/${run_id}-${map_name}"
mkdir -p "$output_dir"

work_dir="${TIER_IV_L2O_DIR:-${TMPDIR:-/tmp}/autoware_lanelet2_to_opendrive}"
tier_iv_ref="${TIER_IV_L2O_REF:-}"
tier_iv_target="${TIER_IV_L2O_TARGET:-carla}"

if [[ ! -d "$work_dir/.git" ]]; then
  if [[ -n "$tier_iv_ref" ]]; then
    # A pinned ref may not be reachable from a shallow clone of the default
    # branch, so fetch full history up front when one is requested.
    git clone https://github.com/tier4/autoware_lanelet2_to_opendrive.git "$work_dir"
  else
    git clone --depth 1 https://github.com/tier4/autoware_lanelet2_to_opendrive.git "$work_dir"
  fi
fi

if [[ -n "$tier_iv_ref" ]]; then
  git -C "$work_dir" fetch --depth 1 origin "$tier_iv_ref"
  git -C "$work_dir" checkout --quiet --detach FETCH_HEAD
fi

dirty_note=""
if [[ -n "$(git -C "$work_dir" status --porcelain)" ]]; then
  dirty_note=" (WARNING: work_dir has local modifications not reflected in this commit hash)"
fi

target_platform=""
platform_args=()
if [[ "$(uname -m)" != "x86_64" ]]; then
  target_platform="linux/amd64"
  platform_args=(--platform "$target_platform")
fi

cp "$input_map" "$output_dir/$input_name"

# The tool's `map=` Hydra option selects a config that carries the CRS
# origin (MGRS grid or lat/lon) for the map being converted -- it does not
# just label the input file. Passing an arbitrary/unmatched name here (or
# reusing a bundled preset for a different map) either errors out or, worse,
# silently applies the wrong origin. When an origin was supplied, generate a
# throwaway map config for this run and add it to Hydra's search path;
# otherwise fall back to the bundled `example` config with a loud warning.
origin_lat="${TIER_IV_L2O_ORIGIN_LAT:-}"
origin_lon="${TIER_IV_L2O_ORIGIN_LON:-}"
origin_alt="${TIER_IV_L2O_ORIGIN_ALT:-0}"
map_group="$(printf '%s' "$map_name" | tr -c 'A-Za-z0-9_-' '_')"

extra_mount_args=()
if [[ -n "$origin_lat" && -n "$origin_lon" ]]; then
  custom_conf_dir="$output_dir/.map-conf"
  mkdir -p "$custom_conf_dir/map"
  # The tool reads the origin from two independently-parsed places that
  # disagree on field names: resolve_projection_from_hydra() (main
  # conversion) reads `lat_lon: {latitude, longitude, altitude}`, while
  # PreprocessOperation.from_hydra_config() (always runs, even with no
  # preprocessing ops configured) reads a separate top-level `origin:
  # {lat, lon}`. Both blocks are written so either code path finds it.
  cat > "$custom_conf_dir/map/${map_group}.yaml" <<EOF
# Generated by run-lanelet2-opendrive-baseline.sh for $input_name (run $run_id).
lat_lon:
  latitude: $origin_lat
  longitude: $origin_lon
  altitude: $origin_alt
origin:
  lat: $origin_lat
  lon: $origin_lon
EOF
  extra_mount_args=(-v "$custom_conf_dir:/custom-conf:ro")
  map_override="map=$map_group"
  hydra_searchpath_arg="hydra.searchpath=[file:///custom-conf]"
  origin_summary="lat=$origin_lat lon=$origin_lon alt=$origin_alt"
else
  if [[ -n "$origin_lat" || -n "$origin_lon" ]]; then
    echo "WARNING: TIER_IV_L2O_ORIGIN_LAT and TIER_IV_L2O_ORIGIN_LON must both be set; ignoring the one that was provided." >&2
  fi
  echo "WARNING: no CRS origin supplied (set TIER_IV_L2O_ORIGIN_LAT/TIER_IV_L2O_ORIGIN_LON). Falling back to the tool's bundled 'example' map config, whose origin is almost certainly wrong for this input map -- positions in the output .xodr may be silently misplaced." >&2
  map_override="map=example"
  hydra_searchpath_arg=""
  origin_summary="<not supplied; used bundled 'example' map config>"
fi

# The upstream image includes CARLA as an extra.  Its current wheel is
# x86_64-only, so any non-x86_64 host must request the x86_64 image
# explicitly. (Verify with `docker image inspect l2o-convert:local
# --format '{{.Architecture}}'` after the first build if this ever changes.)
(
  cd "$work_dir"
  DOCKER_DEFAULT_PLATFORM="$target_platform" docker compose --profile convert build convert
)

# None of these three stages use `set -e` fail-fast: the converter can exit
# non-zero after already writing a usable .xodr (e.g. a later internal
# consistency check catching a real mapping problem), and QC/analyze on a
# partial or flagged output is itself useful diagnostic signal (0단계's
# "collect failing blocks" principle) rather than something to discard just
# because an earlier stage complained. Every stage's outcome is recorded in
# the manifest instead of being decided silently by which command aborted
# the script.
convert_status=0
docker run --rm "${platform_args[@]+"${platform_args[@]}"}" \
  "${extra_mount_args[@]+"${extra_mount_args[@]}"}" \
  -v "$output_dir:/io" \
  l2o-convert:local \
  "$map_override" \
  "target=$tier_iv_target" \
  "input_map_path=/io/$input_name" \
  "output_map_path=/io/$output_name" \
  ${hydra_searchpath_arg:+"$hydra_searchpath_arg"} || convert_status=$?

qc_status="skipped"
analyze_status="skipped"
if [[ -f "$output_dir/$output_name" ]]; then
  qc_status=0
  docker run --rm "${platform_args[@]+"${platform_args[@]}"}" \
    --entrypoint qc-validate \
    -v "$output_dir:/io" \
    l2o-convert:local \
    "/io/$output_name" \
    --output "/io/${map_name}_qc.xqar" || qc_status=$?

  analyze_status=0
  docker run --rm "${platform_args[@]+"${platform_args[@]}"}" \
    --entrypoint analyze \
    -v "$output_dir:/io" \
    l2o-convert:local \
    "/io/$output_name" \
    "/io/$input_name" \
    --output "/io/${map_name}_analysis.xqar" || analyze_status=$?
fi

tier_iv_commit="$(git -C "$work_dir" rev-parse HEAD)"
input_sha256="$(sha256_of "$input_map")"

overall_status="pass"
if [[ "$convert_status" != "0" || "$qc_status" != "0" || "$analyze_status" != "0" ]]; then
  overall_status="fail"
fi

manifest="$output_dir/manifest.txt"
{
  echo "run_id=$run_id"
  echo "map_name=$map_name"
  echo "input_map=$input_map"
  echo "input_sha256=$input_sha256"
  echo "tier_iv_repo=https://github.com/tier4/autoware_lanelet2_to_opendrive"
  echo "tier_iv_commit=$tier_iv_commit"
  echo "tier_iv_ref_requested=${tier_iv_ref:-<none, used existing checkout>}"
  echo "tier_iv_target=$tier_iv_target"
  echo "map_config=$map_override"
  echo "crs_origin=$origin_summary"
  echo "platform=${target_platform:-native}"
  echo "convert_exit=$convert_status"
  echo "qc_validate_exit=$qc_status"
  echo "analyze_exit=$analyze_status"
  echo "overall_status=$overall_status"
  echo "generated_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$manifest"

printf '\nTier IV commit: %s%s\n' "$tier_iv_commit" "$dirty_note"
printf 'Input SHA-256: %s\n' "$input_sha256"
printf 'Stage exit codes: convert=%s qc-validate=%s analyze=%s (overall: %s)\n' \
  "$convert_status" "$qc_status" "$analyze_status" "$overall_status"
printf 'Manifest: %s\n' "$manifest"
printf '\nArtifacts (run_id=%s):\n' "$run_id"
find "$output_dir" -maxdepth 1 -type f -print | sort

if [[ "$overall_status" != "pass" ]]; then
  echo "one or more stages failed; see $manifest and the log above" >&2
  exit 1
fi
