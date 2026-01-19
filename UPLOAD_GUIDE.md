# GitHub Upload and Data Sharing Instructions

## Overview

This guide explains how to upload this benchmark repository to GitHub and share the large datasets via cloud storage.

## Part 1: GitHub Repository Setup

### Step 1: Initialize Git Repository

```bash
cd /data6/mark/Project/chimericRNA_detection/datasets_and_results/Github

# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Fusion detection benchmark with Docker containers and analysis scripts"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com
2. Click "New Repository"
3. Repository name: `LongReadsFusionBenchmarking` (or your preferred name)
4. Description: "Comprehensive benchmark of fusion detection tools for long-read RNA-seq"
5. Choose Public or Private
6. Do NOT initialize with README (we already have one)
7. Click "Create repository"

### Step 3: Push to GitHub

```bash
# Add remote repository
git remote add origin https://github.com/GenomicMedicine/LongReadsFusionBenchmarking.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 4: Verify Upload

Visit `https://github.com/GenomicMedicine/LongReadsFusionBenchmarking` to verify all files are uploaded.

Expected structure:
```
LongReadsFusionBenchmarking/
├── README.md
├── WIKI.md
├── LICENSE
├── .gitignore
├── GFD_main.sh
├── makefusion.sh
├── dockerfiles/
├── analysis_scripts/
├── docs/
└── data_links/
```

## Part 2: Data Upload to Cloud Storage

Since datasets are large (~1.3 TB total), they should be hosted separately.

### Option A: Zenodo (Recommended for Permanent DOI)

**Advantages**:
- Permanent DOI for citations
- Free for academic use
- Unlimited storage for research data
- Integrated with GitHub

**Steps**:

1. **Create Zenodo Account**: https://zenodo.org/signup

2. **Prepare Data Archive**:
```bash
# Compress simulated data
cd /data6/mark/Project/chimericRNA_detection/datasets_and_results
tar -czf simulated_data.tar.gz simulated_data/
tar -czf simulated_data_cpu25.tar.gz simulated_data_cpu25/

# Compress real data
tar -czf real_data.tar.gz real_data/

# Generate checksums
sha256sum simulated_data.tar.gz > checksums.txt
sha256sum simulated_data_cpu25.tar.gz >> checksums.txt
sha256sum real_data.tar.gz >> checksums.txt
```

3. **Upload to Zenodo**:
   - Go to https://zenodo.org/deposit/new
   - Upload files (may take hours/days depending on connection)
   - Fill in metadata:
     - Title: "Fusion Detection Benchmark Datasets - Simulated and Real Long-read RNA-seq Data"
     - Description: Copy from SIMULATED_DATA.md
     - Authors: Your name(s)
     - Keywords: RNA-seq, fusion detection, long reads, ONT, PacBio
     - License: CC BY 4.0
   - Click "Publish"
   - Copy the DOI (e.g., `10.5281/zenodo.XXXXXXX`)

4. **Update Repository**:
```bash
# Update data_links/SIMULATED_DATA.md with Zenodo DOI
# Update data_links/REAL_DATA.md with Zenodo DOI
# Update README.md with data repository link

git add data_links/*.md README.md
git commit -m "Add Zenodo DOI links for datasets"
git push
```

### Option B: Google Drive (Easier, No Size Limit for Workspace)

**Advantages**:
- Familiar interface
- Fast upload
- Easy sharing

**Disadvantages**:
- No permanent DOI
- Shared links may change

**Steps**:

1. **Upload to Google Drive**:
   - Create folder: "Fusion_Benchmark_Datasets"
   - Upload compressed files
   - Right-click → Share → Get link
   - Set to "Anyone with the link can view"
   - Copy the link or File ID

2. **Create Download Script**:
```bash
# Create download helper
cat > download_simulated_data.sh << 'EOF'
#!/bin/bash
# Download simulated datasets from Google Drive

FILEID="YOUR_GOOGLE_DRIVE_FILE_ID"
FILENAME="simulated_data.tar.gz"

# Install gdown if needed
pip install gdown

# Download
gdown --id $FILEID -O $FILENAME

# Verify checksum
echo "EXPECTED_SHA256  $FILENAME" | sha256sum -c

# Extract
tar -xzf $FILENAME
EOF

chmod +x download_simulated_data.sh
```

3. **Update Repository**:
```bash
git add download_simulated_data.sh
git add data_links/*.md
git commit -m "Add Google Drive download links"
git push
```

### Option C: Institutional Repository

Check if your institution provides data repository services:
- Many universities offer research data storage with DOIs
- Contact your library or IT department

## Part 3: Docker Hub (Optional)

### Push Pre-built Docker Images

**Advantages**:
- Users don't need to build images
- Faster setup
- Version control

**Steps**:

1. **Create Docker Hub Account**: https://hub.docker.com

2. **Build and Tag Images**:
```bash
cd dockerfiles

# Build all images
for tool_dir in */; do
    cd "$tool_dir"
    tool_name=$(basename "$tool_dir" | sed 's/_docker//')
    docker build -t "YOUR_DOCKERHUB_USERNAME/fusion-${tool_name}:v1.0" .
    cd ..
done
```

3. **Push to Docker Hub**:
```bash
# Login
docker login

# Push all images
for tool_dir in */; do
    tool_name=$(basename "$tool_dir" | sed 's/_docker//')
    docker push "YOUR_DOCKERHUB_USERNAME/fusion-${tool_name}:v1.0"
done
```

4. **Update README**:
Add to README.md:
```markdown
## Pre-built Docker Images

Pull pre-built images from Docker Hub:

\`\`\`bash
docker pull YOUR_DOCKERHUB_USERNAME/fusion-ctat-lr-fusion:v1.0
docker pull YOUR_DOCKERHUB_USERNAME/fusion-jaffal:v1.0
# ... etc
\`\`\`
```

## Part 4: Create GitHub Release

### Tag a Release

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Version 1.0.0 - Initial release with 9 tools and 40 simulated datasets"

# Push tag
git push origin v1.0.0
```

### Create Release on GitHub

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Tag: v1.0.0
4. Title: "Fusion Detection Benchmark v1.0.0"
5. Description:
```markdown
## Fusion Detection Benchmark v1.0.0

First stable release of the fusion detection benchmark.

### Included Tools (9)
- CTAT-LR-Fusion
- JAFFAL
- LongGF
- FusionSeeker
- FLAIR-fusion
- pbfusion
- IFDlong
- genion
- FUGAREC

### Datasets
- 40 simulated datasets
- 17 real datasets

### Data Repository
- Zenodo DOI: [10.5281/zenodo.XXXXXXX]
- Google Drive: [INSERT LINK]

### Citation
[Your Paper Citation]
```
6. Click "Publish release"

## Part 5: Update Placeholders

### Replace All Placeholders

Search and replace in all files:

```bash
# In all .md files
find . -name "*.md" -type f -exec sed -i 's/GenomicMedicine/actual_github_username/g' {} +
find . -name "*.md" -type f -exec sed -i 's/YOUR_EMAIL/your.email@institution.edu/g' {} +
find . -name "*.md" -type f -exec sed -i 's/YOUR_DOCKERHUB_USERNAME/actual_dockerhub_username/g' {} +
find . -name "*.md" -type f -exec sed -i 's/\[INSERT ZENODO DOI LINK\]/https:\/\/doi.org\/10.5281\/zenodo.XXXXXXX/g' {} +
find . -name "*.md" -type f -exec sed -i 's/\[INSERT GOOGLE DRIVE LINK\]/https:\/\/drive.google.com\/file\/d\/FILE_ID/g' {} +
```

Manual replacements needed:
- `[Your Name/Institution]` in LICENSE
- `[Your Paper Citation]` in all documentation
- `[YOUR_EMAIL]` in contact sections
- Google Drive File IDs
- Zenodo DOI

## Part 6: Documentation Website (Optional)

### GitHub Pages

Create a documentation website from your repository:

1. **Enable GitHub Pages**:
   - Repository Settings → Pages
   - Source: Deploy from branch
   - Branch: main, folder: /docs
   - Save

2. **Add Jekyll Configuration**:
```bash
cat > docs/_config.yml << 'EOF'
title: Fusion Detection Benchmark
description: Comprehensive benchmark of fusion detection tools for long-read RNA-seq
theme: jekyll-theme-cayman
EOF
```

3. **Push Changes**:
```bash
git add docs/_config.yml
git commit -m "Add GitHub Pages configuration"
git push
```

4. **Access Website**: `https://GenomicMedicine.github.io/LongReadsFusionBenchmarking`

## Part 7: Community Engagement

### Add Important Files

1. **CONTRIBUTING.md**:
```markdown
# Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

For bugs, open an issue with:
- System information
- Error messages
- Steps to reproduce
```

2. **CODE_OF_CONDUCT.md**: Use GitHub's template

3. **Issue Templates**: Create `.github/ISSUE_TEMPLATE/`

### Promote Your Repository

- Tweet announcement with hashtags: #Bioinformatics #RNAseq #Genomics
- Post on relevant forums/mailing lists
- Submit to awesome lists (awesome-bioinformatics)
- Contact tool authors
- Present at conferences

## Verification Checklist

Before final publication:

- [ ] All code runs without errors
- [ ] Docker containers build successfully
- [ ] Analysis scripts execute correctly
- [ ] Documentation is complete and clear
- [ ] Data links work and are accessible
- [ ] Placeholders replaced with actual values
- [ ] LICENSE file included
- [ ] .gitignore configured properly
- [ ] README.md is comprehensive
- [ ] All figures generate correctly
- [ ] Citation information added
- [ ] Contact information updated
- [ ] GitHub release created
- [ ] Zenodo/Google Drive data uploaded
- [ ] Checksums provided for data integrity

## Timeline Estimate

| Task | Time Estimate |
|------|---------------|
| Git setup and initial push | 30 minutes |
| Compress datasets | 4-6 hours |
| Upload to Zenodo (1.3 TB) | 1-3 days |
| Docker Hub images | 2-4 hours |
| Documentation updates | 2-3 hours |
| Testing all links | 1 hour |
| **Total** | **2-4 days** |

## Support

After publication:
- Monitor GitHub issues regularly
- Respond to community questions
- Update documentation based on feedback
- Create FAQ based on common questions
- Release updates as needed

---

**Good luck with your publication!**

For questions about this guide, contact: [YOUR_EMAIL]
