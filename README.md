# Clash 链式代理配置工具

一个简单易用的 Web 工具，用于将住宅 IP 节点添加到 Clash 订阅配置中，并实现链式代理。

## ✨ 功能特点

- 🏠 配置住宅 IP SOCKS5 代理节点
- 🔗 自动合并原始订阅链接
- 🚀 生成支持链式代理的 Clash 配置
- 💻 简洁美观的 Web 界面
- 🔧 自动处理 REALITY short-id 引号问题

## 📦 依赖安装

```bash
pip install flask requests pyyaml
```

## 🚀 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
# 或
pip install flask requests pyyaml
```

2. 运行程序：
```bash
python sub_converter.py
```

3. 打开浏览器访问：
```
http://127.0.0.1:5000
```

4. 配置住宅 IP 节点信息并保存

5. 输入原始订阅链接，生成新的链接

6. 将生成的链接添加到 Clash 客户端中

## 🎯 使用场景

适用于需要通过住宅 IP 进行链式代理的场景，例如：
- 绕过地理位置限制
- 提高匿名性
- 访问特定区域的网络资源

## ⚠️ 注意事项

- `node_config.json` 文件会在首次保存配置后自动生成，包含你的代理服务器信息
- 请勿将 `node_config.json` 文件上传到公共仓库
- 本项目仅供学习交流使用，请遵守当地法律法规

## 📝 配置说明

### 住宅 IP 节点配置
- **节点名称**: 自定义节点显示名称
- **服务器地址**: 代理服务器的 IP 地址
- **端口**: 代理服务器端口
- **用户名**: SOCKS5 认证用户名
- **密码**: SOCKS5 认证密码
- **启用 UDP**: 是否启用 UDP 支持

### 链式代理说明
程序会自动创建一个"🚀 链式前置"策略组，包含所有订阅中的节点。住宅 IP 节点会通过这个策略组的选中节点进行连接，实现链式代理。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
