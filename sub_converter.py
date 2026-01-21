import requests
import yaml
import json
import os
from flask import Flask, request, Response, render_template, jsonify

# 必须依赖: pip install flask requests pyyaml

app = Flask(__name__)

# ================= 配置区域 =================
CONFIG_FILE = 'node_config.json'

# 默认配置 (如果不手动设置，会使用这个)
DEFAULT_CONFIG = {
    'name': '',
    'type': '',
    'server': '',
    'port': 443,
    'username': '',
    'password': '',
    'udp': False
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_CONFIG

def save_node_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# 自定义 YAML 字符串类型，强制加引号
class QuotedStr(str):
    pass

def quoted_scalar_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

yaml.add_representer(QuotedStr, quoted_scalar_representer)
yaml.add_representer(QuotedStr, quoted_scalar_representer, Dumper=yaml.SafeDumper)

PRE_PROXY_GROUP_NAME = '🚀 链式前置'
TARGET_MAIN_GROUP_TYPES = ['select']
# ===========================================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    if request.method == 'GET':
        return jsonify(load_config())
    else:
        new_config = request.json
        # 补全必要字段
        new_config['type'] = 'socks5' # 目前固定
        new_config['dialer-proxy'] = PRE_PROXY_GROUP_NAME 
        save_node_config(new_config)
        return jsonify({'status': 'ok'})

@app.route('/convert')
def convert():
    # 1. 获取 config
    node_config = load_config()
    # 确保核心字段存在
    node_config['dialer-proxy'] = PRE_PROXY_GROUP_NAME
    node_config['type'] = 'socks5'

    # 2. 获取订阅链接参数
    sub_url = request.args.get('url')
    if not sub_url:
        return "❌ 错误: 请提供 'url' 参数", 400
    
    print(f"📥 正在获取订阅: {sub_url}")

    # 3. 下载远程订阅内容
    try:
        headers = {
            'User-Agent': 'ClashVerge/1.3.8',
            'Accept': '*/*'
        }
        resp = requests.get(sub_url, headers=headers, timeout=10)
        resp.raise_for_status()
        # 强制使用 UTF-8 编码，防止 requests 自动识别错误导致的中文乱码
        resp.encoding = 'utf-8'
        content = resp.text
    except Exception as e:
        return f"❌ 下载订阅失败: {str(e)}", 500

    # 4. 解析 YAML
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        if "base64" in content[:20]:
            return "❌ 错误: 目标链接返回的是 Base64 编码而非 YAML 格式。请在机场后台复制 'Clash' 专用订阅链接。", 400
        return f"❌ 解析 YAML 失败: {str(e)}", 500

    if not data or not isinstance(data, dict):
        return "❌ 错误: 订阅内容格式不正确 (非字典结构)", 500

    # 5. 修改逻辑
    
    # 5.1 处理 proxies
    proxies = data.get('proxies')
    if proxies is None:
        proxies = []
        data['proxies'] = proxies

    # 修复 REALITY short-id 引号问题
    for p in proxies:
        if isinstance(p, dict) and 'reality-opts' in p:
            opts = p['reality-opts']
            if 'short-id' in opts:
                opts['short-id'] = QuotedStr(str(opts['short-id']))
    
    # 添加/更新住宅IP节点 (使用配置中的信息)
    # 先检查是否已有同名节点，如果有则替换，没有则追加
    existing_idx = next((i for i, p in enumerate(proxies) if p.get('name') == node_config['name']), -1)
    if existing_idx != -1:
        proxies[existing_idx] = node_config
    else:
        proxies.append(node_config)
    
    # 5.2 准备前置组的候选节点
    # 排除住宅IP自身
    all_nodes = [p['name'] for p in proxies if p['name'] != node_config['name']]
    
    # 自动选择置顶
    auto_select = next((name for name in all_nodes if '自动选择' in name or 'Autoselect' in name), None)
    if auto_select:
        all_nodes.remove(auto_select)
        all_nodes.insert(0, auto_select)

    # 5.3 处理 proxy-groups
    proxy_groups = data.get('proxy-groups')
    if proxy_groups is None:
        proxy_groups = []
        data['proxy-groups'] = proxy_groups

    # 创建或更新“链式前置”组
    pre_group = next((g for g in proxy_groups if g['name'] == PRE_PROXY_GROUP_NAME), None)
    if pre_group:
        pre_group['proxies'] = all_nodes
    else:
        new_group = {
            'name': PRE_PROXY_GROUP_NAME,
            'type': 'select',
            'proxies': all_nodes
        }
        insert_pos = 1 if len(proxy_groups) > 0 else 0
        proxy_groups.insert(insert_pos, new_group)

    # 5.4 将住宅IP加入到主策略组
    for group in proxy_groups:
        if group['type'] in TARGET_MAIN_GROUP_TYPES and group['name'] != PRE_PROXY_GROUP_NAME:
            if 'Recycle' in group['name']: continue
            
            if node_config['name'] not in group['proxies']:
                group['proxies'].insert(0, node_config['name'])

    # 6. 返回修改后的 YAML
    try:
        result_yaml = yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
        return Response(result_yaml, mimetype='text/yaml; charset=utf-8')
    except Exception as e:
        return f"❌ 生成配置失败: {str(e)}", 500

if __name__ == '__main__':
    print("✅ 服务已启动，请访问: http://127.0.0.1:5000 配置节点信息")
    app.run(host='0.0.0.0', port=5000)
