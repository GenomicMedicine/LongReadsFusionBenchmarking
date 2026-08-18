#!/bin/bash
set -e

# JAFFA handles its own index construction in its installation folder
echo "JAFFAL expects an internal installation of hg38."

echo "Starting Docker with JAFFAL to install reference structure inside its container..."
docker run --rm -v $(pwd):/host_dir -w /opt/JAFFA mark614/gfd:jaffal-5.20 /bin/bash -c "
  echo 'Running JAFFA install script to pull hg38 references...'
  ./install_linux64.sh || true
  echo 'Note: The references are installed inside this container instance or you can persist /opt/JAFFA out.'
"

echo "JAFFAL Reference initialization script complete."
