#!/bin/bash
# Karmac Dashboard — SBOM Generator
# Generates a Software Bill of Materials listing all dependencies.
# Usage: bash generate_sbom.sh

set -e

echo "=== Karmac Dashboard — SBOM Generator ==="
echo ""

# Check for cyclonedx-bom
if ! python3 -m cyclonedx_py --version &>/dev/null 2>&1; then
    echo "Installing cyclonedx-bom..."
    pip install cyclonedx-bom --quiet
fi

# Generate SBOM in JSON format
echo "Generating SBOM from requirements.txt..."
cyclonedx-py requirements SRC/requirements.txt \
    --output-format json \
    --outfile sbom.json

# Generate SBOM in XML format (CycloneDX standard)
cyclonedx-py requirements SRC/requirements.txt \
    --output-format xml \
    --outfile sbom.xml

echo ""
echo "=== SBOM Summary ==="
python3 -c "
import json
with open('sbom.json') as f:
    sbom = json.load(f)
components = sbom.get('components', [])
print(f'Total components: {len(components)}')
print('')
print(f'{'Package':<30} {'Version':<15} {'License':<20}')
print('-' * 65)
for c in sorted(components, key=lambda x: x.get('name', '')):
    name = c.get('name', 'unknown')
    version = c.get('version', 'unknown')
    licenses = [l.get('license', {}).get('id', 'unknown') for l in c.get('licenses', [])]
    lic = ', '.join(licenses) if licenses else 'unknown'
    print(f'{name:<30} {version:<15} {lic:<20}')
"

echo ""
echo "SBOM files generated:"
echo "  sbom.json — CycloneDX JSON format"
echo "  sbom.xml  — CycloneDX XML format"