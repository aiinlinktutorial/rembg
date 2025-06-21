# API服务离线问题排除指南

## 问题分析

根据测试结果，您的API在https://rembg-12mt.onrender.com 上返回404错误，但本地测试显示API代码本身工作正常。

## 可能的原因

1. **端口配置问题** - Render可能没有正确绑定端口
2. **启动命令问题** - Docker容器可能没有正确启动
3. **健康检查失败** - 健康检查端点可能无法访问

## 解决方案

### 1. 立即修复 (推荐)

我已经更新了以下配置文件：

- ✅ **Dockerfile** - 添加了 `--workers 1` 参数
- ✅ **render.yaml** - 添加了明确的 `dockerCommand`

### 2. 部署修复

现在您需要将更改推送到GitHub并重新部署：

```bash
git add .
git commit -m "修复API部署配置问题"
git push origin main
```

### 3. 在Render Dashboard检查

1. 进入 https://dashboard.render.com
2. 找到您的 `rembg-api` 服务
3. 查看 **Logs** 页面，寻找错误信息
4. 确认 **Settings** 中的配置：
   - Build Command: (自动从Dockerfile)
   - Start Command: `uvicorn api_server:app --host 0.0.0.0 --port $PORT --workers 1`
   - Health Check Path: `/health`

### 4. 常见Render部署问题

#### 问题A: 端口绑定错误
**症状**: "No open ports detected"
**解决**: 确保使用 `--host 0.0.0.0 --port $PORT`

#### 问题B: 健康检查失败
**症状**: 部署无限循环
**解决**: 确认 `/health` 端点可访问

#### 问题C: 启动命令错误
**症状**: 容器启动后立即退出
**解决**: 检查uvicorn命令语法

### 5. 验证修复

部署完成后，运行测试：

```bash
python test_api_status.py
```

期望结果：
- ✅ `/health` 返回 200 状态码
- ✅ `/` 返回 API信息
- ✅ `/docs` 可访问

### 6. 如果问题仍然存在

1. **检查Render服务日志**:
   - 在Dashboard中查看实时日志
   - 寻找启动错误或端口绑定问题

2. **手动重新部署**:
   - 在Render Dashboard中点击 "Manual Deploy"
   - 选择最新的commit

3. **验证环境变量**:
   - 确认 `PORT` 和 `API_KEY` 已设置

4. **联系Render支持**:
   - 如果所有配置都正确但仍然失败
   - 提供服务名称和详细错误日志

## 测试API功能

修复后，您可以这样测试API：

```bash
# 健康检查
curl https://rembg-12mt.onrender.com/health

# 获取API信息
curl https://rembg-12mt.onrender.com/

# 测试背景移除 (需要API Key)
curl -H "X-API-Key: your-api-key" \
     -F "file=@your-image.jpg" \
     https://rembg-12mt.onrender.com/remove-bg \
     --output result.png
```

## 预防措施

1. **本地测试**: 使用 `python test_local_api.py` 验证更改
2. **监控**: 设置Render通知以快速发现问题
3. **备份**: 保持工作配置的备份

---

💡 **提示**: 如果您经常遇到部署问题，考虑使用Render的付费计划以获得更稳定的服务和更好的支持。 