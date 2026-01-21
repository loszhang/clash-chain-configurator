# 远程服务器部署指南

本文档介绍如何在远程服务器上部署 Clash Chain Configurator。

## 📋 前置要求

- 一台 Linux 服务器（Ubuntu/Debian/CentOS 等）
- 已安装 Docker 和 Docker Compose
- SSH 访问权限

## 🚀 快速部署

### 1. 安装 Docker（如果未安装）

**Ubuntu/Debian:**
```bash
# 更新软件包
sudo apt update

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo apt install docker-compose-plugin -y

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到 docker 组（可选，避免每次使用 sudo）
sudo usermod -aG docker $USER
# 重新登录以使组更改生效
```

**CentOS/RHEL:**
```bash
# 安装 Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. 克隆项目

```bash
# 克隆 GitHub 仓库
git clone https://github.com/loszhang/clash-chain-configurator.git

# 进入项目目录
cd clash-chain-configurator
```

### 3. 启动服务

```bash
# 构建并启动容器（后台运行）
docker compose up -d --build

# 或者使用旧版本的 docker-compose
docker-compose up -d --build
```

### 4. 验证服务

```bash
# 查看容器运行状态
docker compose ps

# 查看日志
docker compose logs -f

# 测试访问（在服务器上）
curl http://localhost:5000
```

### 5. 配置防火墙（如果需要）

**开放 5000 端口：**

**Ubuntu/Debian (UFW):**
```bash
sudo ufw allow 5000/tcp
sudo ufw reload
```

**CentOS/RHEL (firewalld):**
```bash
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

**云服务器（阿里云/腾讯云/AWS 等）:**
- 在安全组/防火墙规则中开放 5000 端口

### 6. 访问服务

在浏览器中访问：
```
http://你的服务器IP:5000
```

## 🔧 常用命令

### 查看服务状态
```bash
docker compose ps
```

### 查看实时日志
```bash
docker compose logs -f
```

### 停止服务
```bash
docker compose down
```

### 重启服务
```bash
docker compose restart
```

### 更新代码并重新部署
```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker compose up -d --build
```

### 查看容器内部
```bash
docker compose exec app sh
```

## 🌐 使用反向代理（推荐）

如果你想使用域名访问并配置 HTTPS，可以使用 Nginx 或 Caddy 作为反向代理。

### 使用 Nginx

**1. 安装 Nginx:**
```bash
sudo apt install nginx -y
```

**2. 创建配置文件:**
```bash
sudo nano /etc/nginx/sites-available/clash-chain
```

**3. 添加以下配置:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**4. 启用站点:**
```bash
sudo ln -s /etc/nginx/sites-available/clash-chain /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**5. 配置 HTTPS（使用 Let's Encrypt）:**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### 使用 Caddy（更简单）

**1. 安装 Caddy:**
```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy -y
```

**2. 创建 Caddyfile:**
```bash
sudo nano /etc/caddy/Caddyfile
```

**3. 添加配置（Caddy 会自动配置 HTTPS）:**
```
your-domain.com {
    reverse_proxy localhost:5000
}
```

**4. 重启 Caddy:**
```bash
sudo systemctl reload caddy
```

## 🔐 安全建议

1. **使用 HTTPS** - 通过反向代理配置 SSL 证书
2. **配置防火墙** - 只开放必要的端口（80, 443, 22）
3. **定期更新** - 保持系统和 Docker 镜像更新
4. **备份配置** - 定期备份 `node_config.json` 文件
5. **限制访问** - 可以在 Nginx 中配置 IP 白名单或基本认证

## 📊 监控和维护

### 查看容器资源使用
```bash
docker stats clash-chain-configurator
```

### 清理 Docker 资源
```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune
```

### 自动重启策略
docker-compose.yml 已配置 `restart: unless-stopped`，容器会在系统重启后自动启动。

## ❓ 故障排查

### 容器启动失败
```bash
# 查看详细日志
docker compose logs

# 检查端口占用
sudo netstat -tulpn | grep 5000
```

### 无法访问服务
1. 检查容器是否运行：`docker compose ps`
2. 检查防火墙设置
3. 检查云服务器安全组规则
4. 查看 Nginx/Caddy 日志

### 配置文件丢失
配置文件已挂载到 `./node_config.json`，确保不要删除项目目录。

---

如有问题，请访问项目 GitHub 提交 Issue：
https://github.com/loszhang/clash-chain-configurator/issues
