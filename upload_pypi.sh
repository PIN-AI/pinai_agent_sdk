#!/bin/bash

# 自动更新版本号
current_version=$(grep -o 'version="[^"]*"' setup.py | grep -o '[0-9]*\.[0-9]*\.[0-9]*')
echo "当前版本: $current_version"

# 将版本号分割为数组
IFS='.' read -ra VERSION_PARTS <<< "$current_version"
PATCH=${VERSION_PARTS[2]}
NEW_PATCH=$((PATCH + 1))
NEW_VERSION="${VERSION_PARTS[0]}.${VERSION_PARTS[1]}.$NEW_PATCH"

# 使用 sed 更新 setup.py 中的版本号
sed -i '' "s/version=\"$current_version\"/version=\"$NEW_VERSION\"/" setup.py
echo "版本号已更新至: $NEW_VERSION"

# 清理旧的构建文件
rm -rf dist/ build/ *.egg-info/

# 构建包
python -m build

# 上传到 PyPI
python -m twine upload dist/* --username __token__ --password "pypi-AgEIcHlwaS5vcmcCJDg5MjY4ZTVmLTBkMzUtNGE1Ny04OGU1LTU4ZTI3MTJlM2Y2OAACKlszLCI0ZDc5YzcxMy1mOGVlLTRjYmYtYWNmNy0yZTAxODUzNWE3NTgiXQAABiBSat9D-VdmhLFu4IKKi3FBiuyIJmxIXNtSdcC738AUEA"

echo "上传完成！"

# 提交版本更新到 git（可选）
git add .
git commit -m "bump version to $NEW_VERSION"
# git push 