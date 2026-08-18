#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
IMAGE_NAME="longreadsfusionbenchmarking/longfuse-k235-pipeline:latest"
DOCKERFILE_PATH="${SCRIPT_DIR}/Dockerfile"

if ! command -v docker >/dev/null 2>&1; then
  echo "Error: docker is not installed or not in PATH."
  exit 1
fi

if [[ "${1:-}" == "--rebuild" ]]; then
  docker build -t "${IMAGE_NAME}" -f "${DOCKERFILE_PATH}" "${REPO_ROOT}"
  shift
fi

if ! docker image inspect "${IMAGE_NAME}" >/dev/null 2>&1; then
  echo "Docker image not found, building ${IMAGE_NAME} ..."
  docker build -t "${IMAGE_NAME}" -f "${DOCKERFILE_PATH}" "${REPO_ROOT}"
fi

declare -A MOUNT_DIRS
MOUNT_DIRS["${REPO_ROOT}"]=1

path_args=(
  "--sim-calls"
  "--real-calls"
  "--output-dir"
  "--curated-fusions"
  "--ground-truth"
  "--ensembl-map"
)

for ((i=1; i<=$#; i++)); do
  current="${!i}"
  for key in "${path_args[@]}"; do
    if [[ "${current}" == "${key}" ]]; then
      next_index=$((i+1))
      if [[ ${next_index} -le $# ]]; then
        next_val="${!next_index}"
        if [[ "${next_val}" != --* ]]; then
          abs_path="$(python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "${next_val}")"
          if [[ "${key}" == "--output-dir" ]]; then
            target_dir="${abs_path}"
          else
            target_dir="$(dirname "${abs_path}")"
          fi
          MOUNT_DIRS["${target_dir}"]=1
        fi
      fi
      break
    fi
  done
done

docker_args=(
  run --rm
  --user "$(id -u):$(id -g)"
)

for mount_dir in "${!MOUNT_DIRS[@]}"; do
  if [[ -d "${mount_dir}" ]]; then
    docker_args+=(-v "${mount_dir}:${mount_dir}")
  fi
done

docker_args+=(-w "$(pwd)")
docker_args+=("${IMAGE_NAME}")
docker_args+=("$@")

echo "Running containerized LongFuse k235 pipeline..."
docker "${docker_args[@]}"
