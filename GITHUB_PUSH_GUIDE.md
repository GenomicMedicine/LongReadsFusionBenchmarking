# GitHub推送指南

## 问题：GitHub不再支持密码认证

GitHub从2021年8月13日起已停止支持使用密码进行Git操作。您需要使用**Personal Access Token (PAT)**。

## 解决方案：创建Personal Access Token

### 步骤1: 创建Personal Access Token

1. 登录GitHub: https://github.com
2. 点击右上角头像 → **Settings**
3. 左侧菜单最下方 → **Developer settings**
4. 左侧点击 **Personal access tokens** → **Tokens (classic)**
5. 点击 **Generate new token** → **Generate new token (classic)**
6. 填写信息：
   - **Note**: `LongReadsFusionBenchmarking Push`
   - **Expiration**: 选择有效期（建议90天或No expiration）
   - **Select scopes**: 勾选 `repo` (所有权限)
7. 点击底部 **Generate token**
8. **重要**: 复制生成的token（以 `ghp_` 开头），离开页面后无法再查看！

### 步骤2: 使用Token推送

```bash
cd /data6/mark/Project/chimericRNA_detection/datasets_and_results/Github

# 删除旧的远程配置
git remote remove origin

# 使用Token添加远程仓库（将YOUR_TOKEN替换为实际token）
git remote add origin https://GenomicMedicine:YOUR_TOKEN@github.com/GenomicMedicine/LongReadsFusionBenchmarking.git

# 推送到GitHub
git push -u origin main
```

### 步骤3: 或者使用SSH密钥（推荐长期使用）

如果您希望避免每次都输入token，可以设置SSH密钥：

```bash
# 生成SSH密钥
ssh-keygen -t ed25519 -C "genomicmedicine@polyu.edu.hk"

# 查看公钥
cat ~/.ssh/id_ed25519.pub

# 复制公钥内容，添加到GitHub:
# GitHub → Settings → SSH and GPG keys → New SSH key

# 更改远程URL为SSH
git remote set-url origin git@github.com:GenomicMedicine/LongReadsFusionBenchmarking.git

# 推送
git push -u origin main
```

## 当前仓库状态

- ✅ Git仓库已初始化
- ✅ 所有文件已提交（106个文件）
- ✅ 分支设置为main
- ⏳ 等待推送到GitHub

## 推送后续步骤

推送成功后：

1. **验证仓库**: https://github.com/GenomicMedicine/LongReadsFusionBenchmarking
2. **创建Release**: 
   - 点击 "Releases" → "Create a new release"
   - Tag: v1.0.0
   - Title: "Long-read Fusion Detection Benchmark v1.0.0"
3. **上传数据到云存储**: 参考 UPLOAD_GUIDE.md

## 需要帮助？

查看完整指南：
- [UPLOAD_GUIDE.md](../UPLOAD_GUIDE.md)
- [PROJECT_SUMMARY.md](../PROJECT_SUMMARY.md)
