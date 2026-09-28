# -*- coding: utf-8 -*-
"""批量为 posts/ 下所有文章补充 内容介绍 + 技术备注, 并做排版美化."""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

POSTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'posts')

# ---------- 分类 -> 介绍模板 ----------
CAT_DESC = {
    'python':    'Python 编程实战笔记',
    'go':        'Go 语言后端开发实战',
    'Linux':     'Linux 系统运维笔记',
    '集群':      '服务器集群与高可用架构实践',
    'lnmp':      'LNMP/LAMP Web 服务架构与优化',
    'kubernetes':'Kubernetes 云原生容器编排实践',
    'openstack': 'OpenStack 私有云部署与运维笔记',
    '前端':      '前端开发学习与实践',
    'shell':     'Shell 脚本自动化运维',
    'vue':       'Vue 前端工程化实践',
    'tomcat':    'Tomcat 中间件部署与调优',
    'autoops':   '自动化运维平台开发实践',
    'ansible':   'Ansible 自动化运维实践',
    'zabbix':    'Zabbix 监控系统实践',
    '运维基础':  '运维基础架构建设笔记',
    '后端':      '后端服务开发笔记',
    'typescript':'TypeScript 学习笔记',
    'cobbler':   'Cobbler 自动化装机实践',
    '未分类':    '技术随笔与实践记录',
}

# ---------- 关键词 -> 技术演进备注 ----------
TECH_NOTES = [
    (r'centos\s*6|6\.\d', 'CentOS 6 已于 2020 年 11 月停止维护(EOL),生产环境建议迁移至 Rocky Linux / AlmaLinux / Ubuntu LTS。'),
    (r'centos\s*7|7\.\d', 'CentOS 7 已于 2024 年 6 月 30 日停止维护(EOL),建议迁移至 Rocky Linux 9 / AlmaLinux 9 或国产 openEuler。'),
    (r'python\s*2|python2', 'Python 2 已于 2020 年 1 月停止官方支持,文中示例建议在 Python 3 环境下验证。'),
    (r'mysql\s*5\.[56]', 'MySQL 5.5/5.6 均已停止维护,建议升级至 MySQL 8.0+ 或 MariaDB 10.6+。'),
    (r'mysql\s*5\.7', 'MySQL 5.7 已于 2023 年 10 月停止官方支持(EOL),建议规划升级至 MySQL 8.0。'),
    (r'php\s*5|php5', 'PHP 5.x 系列已全部停止维护,建议使用 PHP 8.x 以获得性能与安全更新。'),
    (r'kubernetes.*1\.(10|11|12|13|14)\b|k8s.*1\.(10|11|12|13|14)\b', '文中 Kubernetes 版本较旧,kubeadm 部署方式在 1.24+ 后已默认使用 containerd 运行时(dockershim 已移除),请注意版本差异。'),
    (r'openstack', 'OpenStack 各版本迭代较快,部署时请以官方文档对应版本为准;生产中也可考虑 Kolla-Ansible 等容器化部署方案。'),
    (r'docker', 'Docker 与 Kubernetes 生态演进较快,新版 K8s 默认运行时为 containerd,请注意适配。'),
    (r'zabbix\s*[23]\.', 'Zabbix 2.x/3.x 已停止维护,建议升级至 Zabbix 6.0 LTS 或 7.0 LTS。'),
    (r'ansible', 'Ansible 2.9 之后的社区版更名为 ansible-core + collections 模式,部分模块路径有变化。'),
    (r'nginx', 'Nginx 配置在不同大版本间略有差异,建议以当前稳定版(1.24+/1.26+)官方文档为准。'),
    (r'iptables', '现代发行版(RHEL 8+/Debian 10+)默认使用 nftables,iptables 多为兼容层,可考虑学习 nftables 语法。'),
]

def gen_intro(title, cat, body):
    """生成内容介绍."""
    base = CAT_DESC.get(cat, '技术实践笔记')
    # 提取正文里前几条非空内容,辅助描述
    text = re.sub(r'```[\s\S]*?```', '', body)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    lines = [l.strip() for l in text.splitlines() if l.strip()][:3]
    snippet = ''
    if lines:
        s = ' '.join(lines)
        s = re.sub(r'\s+', ' ', s)
        snippet = s[:80]
    intro = f'本文是{base},记录了「{title}」的相关内容。'
    if snippet and len(snippet) > 15:
        intro += f'主要涉及:{snippet}…'
    return intro

def gen_note(title, body, date):
    """根据关键词与年份生成技术演进备注."""
    hay = (title + '\n' + body)[:4000].lower()
    for pat, note in TECH_NOTES:
        if re.search(pat, hay):
            return note
    year = int(date[:4]) if date[:4].isdigit() else 2020
    if year <= 2018:
        return '本文写于较早年代,文中软件版本与命令在新系统上可能有差异,执行前请核对当前环境。'
    return ''

def beautify(body):
    """排版美化: 给无语言标注的代码块补 shell 标注."""
    def repl(m):
        lang = m.group(1)
        code = m.group(2)
        if lang:
            return m.group(0)
        # 简单猜测语言
        l = 'shell'
        if re.search(r'^\s*(import |from |def |print\()', code, re.M):
            l = 'python'
        elif re.search(r'^\s*(package main|func |fmt\.)', code, re.M):
            l = 'go'
        elif re.search(r'^\s*<[a-zA-Z]', code, re.M):
            l = 'html'
        return f'```{l}{code}```'
    return re.sub(r'```(\w*)\n?([\s\S]*?)```', lambda m: repl(m) if True else m.group(0), body)

def process(path):
    raw = open(path, encoding='utf-8').read()
    raw = raw.lstrip('﻿')
    m = re.match(r'^---\r?\n([\s\S]*?)\r?\n---\r?\n?', raw)
    if not m:
        return None
    fm = m.group(1)
    body = raw[m.end():]

    title = re.search(r'^title:\s*"(.*)"', fm, re.M)
    date  = re.search(r'^date:\s*"(\d{4}-\d{2}-\d{2})', fm, re.M)
    cat   = re.search(r'^category:\s*"(.*)"', fm, re.M)
    title = title.group(1) if title else os.path.basename(path)
    date  = date.group(1) if date else ''
    cat   = cat.group(1) if cat else '未分类'

    if '**内容介绍**' in body:   # 已处理过
        return None

    intro = gen_intro(title, cat, body)
    note  = gen_note(title, body, date)

    new_body = body.lstrip('\n')
    new_body = beautify(new_body)

    header = f'> **内容介绍**\n>\n> {intro}\n'
    if note:
        header += f'\n> **技术备注**\n>\n> {note}\n'
    header += '\n---\n\n'

    return raw[:m.end()] + header + new_body

def main():
    files = sorted(f for f in os.listdir(POSTS) if f.endswith('.md'))
    changed = []
    for f in files:
        p = os.path.join(POSTS, f)
        out = process(p)
        if out is not None:
            open(p, 'w', encoding='utf-8', newline='\n').write(out)
            changed.append(f)
    print(f'changed: {len(changed)}')
    for f in changed:
        print(f)

if __name__ == '__main__':
    main()
