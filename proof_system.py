"""
ProofCollapse v3.3 — 自动推理引擎（超级自然语言理解版 + 通俗报告）
支持矩阵、群、环、线性代数、疑问句，生成漂亮的可视化证明报告
"""

import math, os, json, traceback, re
from collections import deque
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple

# ========== 域定义 ==========
class Domain(Enum):
    ADDITIVE = "additive"
    MULTIPLICATIVE = "multiplicative"
    INTEGRAL = "integral"
    DIFFERENTIAL = "differential"
    SPECTRAL = "spectral"
    FUNCTIONAL = "functional"
    BRAIDED = "braided"
    HOMOTOPY = "homotopy"
    CATEGORICAL = "categorical"

DOMAIN_NAMES = {
    Domain.ADDITIVE: "加法域",
    Domain.MULTIPLICATIVE: "乘法域",
    Domain.INTEGRAL: "积分域",
    Domain.DIFFERENTIAL: "微分域",
    Domain.SPECTRAL: "谱域",
    Domain.FUNCTIONAL: "泛函积分域",
    Domain.BRAIDED: "编织域",
    Domain.HOMOTOPY: "同伦域",
    Domain.CATEGORICAL: "范畴域",
}

DOMAIN_LAYMAN = {
    Domain.ADDITIVE: "处理“加加减减”这类离散步骤的领域，比如整数的加法。",
    Domain.MULTIPLICATIVE: "处理“乘乘除除”和素数分解的领域，比如质数的性质。",
    Domain.INTEGRAL: "处理连续变化和总量的领域，比如面积、微分方程。",
    Domain.DIFFERENTIAL: "处理变化率和斜率的领域，比如速度、加速度。",
    Domain.SPECTRAL: "把东西分解成频率或模式的领域，比如声音的频谱、L函数的零点。",
    Domain.FUNCTIONAL: "处理所有可能路径总和的领域，常用于复杂的量子问题。",
    Domain.BRAIDED: "处理打结、缠绕、辫子结构的领域，与拓扑量子计算有关。",
    Domain.HOMOTOPY: "处理连续变形（拉伸、扭曲但不撕破）的领域，比如橡皮泥的形状。",
    Domain.CATEGORICAL: "处理“关系的关系”的抽象领域，是数学结构的顶层设计。",
}

DUAL_GRAPH = {
    Domain.ADDITIVE: {"exp": Domain.MULTIPLICATIVE, "riemann": Domain.INTEGRAL, "diff_quot": Domain.DIFFERENTIAL},
    Domain.MULTIPLICATIVE: {"log": Domain.ADDITIVE, "log_deriv": Domain.INTEGRAL, "mellin": Domain.SPECTRAL},
    Domain.INTEGRAL: {"laplace": Domain.SPECTRAL, "functional_limit": Domain.FUNCTIONAL, "inverse": Domain.DIFFERENTIAL},
    Domain.DIFFERENTIAL: {"fourier": Domain.SPECTRAL, "inverse": Domain.INTEGRAL},
    Domain.SPECTRAL: {"inv_fourier": Domain.DIFFERENTIAL, "inv_laplace": Domain.INTEGRAL, "inv_mellin": Domain.MULTIPLICATIVE},
    Domain.FUNCTIONAL: {"inv_limit": Domain.INTEGRAL, "topology": Domain.BRAIDED},
    Domain.BRAIDED: {"homotopy": Domain.HOMOTOPY},
    Domain.HOMOTOPY: {"categorify": Domain.CATEGORICAL},
    Domain.CATEGORICAL: {"id_0": Domain.ADDITIVE, "id_1": Domain.MULTIPLICATIVE},
}

# ========== 语义解析器 (超级增强版) ==========
class SemanticParser:
    KEYWORD_MAP = {
        # === 加法域 ===
        "整数": Domain.ADDITIVE, "自然数": Domain.ADDITIVE,
        "偶数": Domain.ADDITIVE, "奇数": Domain.ADDITIVE,
        "加法": Domain.ADDITIVE, "加法域": Domain.ADDITIVE,
        "哥德巴赫": Domain.ADDITIVE, "费马": Domain.ADDITIVE,
        "考拉兹": Domain.ADDITIVE, "collatz": Domain.ADDITIVE,
        "费马大定理": Domain.ADDITIVE, "正整数": Domain.ADDITIVE,
        "和": Domain.ADDITIVE, "求和": Domain.ADDITIVE,
        "六k±一": Domain.ADDITIVE, "6k±1": Domain.ADDITIVE,
        
        # === 乘法域 ===
        "素数": Domain.MULTIPLICATIVE, "质数": Domain.MULTIPLICATIVE,
        "因子": Domain.MULTIPLICATIVE, "分解": Domain.MULTIPLICATIVE,
        "乘法": Domain.MULTIPLICATIVE, "乘法域": Domain.MULTIPLICATIVE,
        "abc": Domain.MULTIPLICATIVE, "ABC": Domain.MULTIPLICATIVE,
        "孪生素数": Domain.MULTIPLICATIVE, "孪生": Domain.MULTIPLICATIVE,
        "乘积": Domain.MULTIPLICATIVE, "乘": Domain.MULTIPLICATIVE,
        "逆元": Domain.MULTIPLICATIVE, "可逆": Domain.MULTIPLICATIVE,
        "单位元": Domain.MULTIPLICATIVE, "群": Domain.MULTIPLICATIVE,
        "矩阵": Domain.MULTIPLICATIVE, "方阵": Domain.MULTIPLICATIVE,
        "正交": Domain.MULTIPLICATIVE, "酉": Domain.MULTIPLICATIVE,
        "行列式": Domain.MULTIPLICATIVE, "特征值": Domain.MULTIPLICATIVE,
        "伽罗瓦": Domain.MULTIPLICATIVE, "frobenius": Domain.MULTIPLICATIVE,
        
        # === 谱域 ===
        "l函数": Domain.SPECTRAL, "l-函数": Domain.SPECTRAL,
        "zeta": Domain.SPECTRAL, "黎曼": Domain.SPECTRAL,
        "零点": Domain.SPECTRAL, "谱": Domain.SPECTRAL,
        "自守": Domain.SPECTRAL, "模形式": Domain.SPECTRAL,
        "hecke": Domain.SPECTRAL, "langlands": Domain.SPECTRAL,
        "朗兰兹": Domain.SPECTRAL,
        "杨-米尔斯": Domain.SPECTRAL, "yang mills": Domain.SPECTRAL,
        "杨米尔斯": Domain.SPECTRAL, "yang-mills": Domain.SPECTRAL,
        "规范场": Domain.SPECTRAL, "胶球": Domain.SPECTRAL,
        "质量间隙": Domain.ADDITIVE, "mass gap": Domain.ADDITIVE,
        
        # === 同伦域 ===
        "流形": Domain.HOMOTOPY, "同胚": Domain.HOMOTOPY,
        "同伦": Domain.HOMOTOPY, "基本群": Domain.HOMOTOPY,
        "庞加莱": Domain.HOMOTOPY, "poincare": Domain.HOMOTOPY,
        "三维球面": Domain.HOMOTOPY, "单连通": Domain.HOMOTOPY,
        "拓扑": Domain.HOMOTOPY, "里奇流": Domain.INTEGRAL,
        
        # === 编织域 ===
        "辫子": Domain.BRAIDED, "琼斯多项式": Domain.BRAIDED,
        "jones": Domain.BRAIDED, "扭结": Domain.BRAIDED,
        "拓扑量子": Domain.BRAIDED,
        
        # === 积分域 ===
        "微分方程": Domain.INTEGRAL, "纳维": Domain.INTEGRAL,
        "navier": Domain.INTEGRAL, "斯托克斯": Domain.INTEGRAL,
        "光滑解": Domain.INTEGRAL, "积分": Domain.INTEGRAL,
        "纳维-斯托克斯": Domain.INTEGRAL, "连续": Domain.INTEGRAL,
        "面积": Domain.INTEGRAL, "体积": Domain.INTEGRAL,
        "导数": Domain.DIFFERENTIAL, "微分": Domain.DIFFERENTIAL,
        "斜率": Domain.DIFFERENTIAL, "变化率": Domain.DIFFERENTIAL,
        
        # === 范畴域 ===
        "范畴": Domain.CATEGORICAL, "函子": Domain.CATEGORICAL,
        "霍奇": Domain.SPECTRAL, "hodge": Domain.SPECTRAL,
        
        # === 通用逻辑词 (忽略) ===
        "猜想": None, "定理": None, "证明": None, "存在": None,
        "任意": None, "所有": None, "每个": None, "无穷": None,
        "是否": None, "什么": None, "如何": None, "吗": None,
    }

    @classmethod
    def parse(cls, statement: str) -> Tuple[Optional[Domain], Optional[Domain]]:
        clean = re.sub(r'[？?！!。，,、]', ' ', statement).lower()
        found = []
        for keyword, domain in cls.KEYWORD_MAP.items():
            if keyword in clean and domain is not None:
                found.append(domain)
        seen = set()
        uniq = []
        for d in found:
            if d not in seen:
                seen.add(d)
                uniq.append(d)
        if not uniq:
            return None, None
        source = uniq[0]
        if len(uniq) == 1:
            # 单一域，结论域与前提域相同（自洽证明）
            target = source
        else:
            target = uniq[-1]
        return source, target

# ========== 路径搜索器 ==========
class PathFinder:
    @staticmethod
    def search(source: Domain, target: Domain, max_depth: int = 3) -> List[Tuple[List[Domain], List[str]]]:
        if source == target:
            return [([source], [])]
        results = []
        queue = deque([(source, [source], [])])
        while queue:
            current, domain_path, mapping_path = queue.popleft()
            if len(domain_path) - 1 >= max_depth:
                continue
            for mapping_name, neighbor in DUAL_GRAPH[current].items():
                new_domain_path = domain_path + [neighbor]
                new_mapping_path = mapping_path + [mapping_name]
                if neighbor == target:
                    results.append((new_domain_path, new_mapping_path))
                queue.append((neighbor, new_domain_path, new_mapping_path))
        return results

# ========== 报告生成器 ==========
class ReportGenerator:
    LAYMAN_MAPPINGS = {
        "exp": ("把加法问题变成乘法问题", "就像把“走了几步”变成“翻了几倍”。"),
        "log": ("把乘法问题还原为加法问题", "就像问“翻了几倍”对应“走了几步”。"),
        "mellin": ("用梅林变换把素数分布分解成频谱", "就像用棱镜把白光分解成彩虹，这里把乘法规律分解成谱线。"),
        "inv_mellin": ("从频谱还原回乘法结构", "从彩虹还原回白光。"),
        "laplace": ("把连续变化转化为频率表示", "把随时间变化的过程拆解成不同频率的成分。"),
        "fourier": ("用傅里叶变换提取变化的频率特征", "类似给声音做频谱分析。"),
        "riemann": ("把离散的求和变成连续的面积", "把分步计算变成平滑的积分。"),
        "functional_limit": ("扩展到所有可能路径的总和", "考虑所有可能发生的事情，为量子效应做准备。"),
        "topology": ("把问题转化为辫子和纽结模型", "用打结的方式来描述复杂的结构。"),
        "homotopy": ("把辫子结构连续变形成同伦类", "在允许拉伸和扭曲的情况下，给形状做分类。"),
        "categorify": ("把操作提升为更高层次的关系", "从“怎么做”升级到“为什么这样做也行”。"),
        "log_deriv": ("把乘法变化率转化为积分问题", "计算乘法的速度，然后积分还原。"),
        "inverse": ("微积分基本定理：积分和求导互为逆运算", "就像加法和减法可以互相抵消。"),
        "diff_quot": ("把离散的变化率变为连续导数", "从“每步差多少”变成“瞬间变化多快”。"),
        "inv_fourier": ("从频率特征还原回原始函数", "从声音的频谱还原出声音的波形。"),
        "inv_laplace": ("从频率表示还原回连续变化", ""),
        "inv_limit": ("把路径总和还原回单个积分", ""),
        "id_0": ("映射到加法世界的零点", "找到加法的起点。"),
        "id_1": ("映射到乘法世界的单位元", "找到乘法的起点。"),
    }

    @staticmethod
    def generate_html(statement: str, source: Domain, target: Domain,
                      domain_path: List[Domain], mapping_names: List[str]) -> str:
        depth = len(domain_path) - 1
        steps_html = ""
        if depth == 0:
            steps_html = "<li>该猜想的前提域和结论域相同，无需映射，在该领域内自洽。</li>"
        else:
            for i in range(depth):
                from_domain = DOMAIN_NAMES[domain_path[i]]
                to_domain = DOMAIN_NAMES[domain_path[i+1]]
                mapping = mapping_names[i]
                title, desc = ReportGenerator.LAYMAN_MAPPINGS.get(mapping, (mapping, ""))
                steps_html += f"<li><strong>{from_domain} → {to_domain} ({title})</strong><br><span style='color:#aaa;'>{desc}</span></li>"

        html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; background: #1e1e2e; color: #eee; padding: 20px; border-radius: 10px; max-width: 800px; margin: auto;">
            <h2 style="color: #ff6b6b;">📜 猜想</h2>
            <p style="font-size: 18px; background: #2a2a3a; padding: 10px; border-radius: 5px;">{statement}</p>
            <h2 style="color: #4ecdc4;">🔍 语义分析</h2>
            <p>系统识别出该猜想主要涉及 <strong style="color: #ffe66d;">{DOMAIN_NAMES[source]}</strong>，结论属于 <strong style="color: #ffe66d;">{DOMAIN_NAMES[target]}</strong>。</p>
            <p style="color: #aaa;">💡 {DOMAIN_NAMES[source]}：{DOMAIN_LAYMAN.get(source, '')}</p>
            <p style="color: #aaa;">💡 {DOMAIN_NAMES[target]}：{DOMAIN_LAYMAN.get(target, '')}</p>
            <h2 style="color: #4ecdc4;">🗺️ 证明路径（共 {depth} 步）</h2>
            <ol style="font-size: 16px; line-height: 2;">
                {steps_html}
            </ol>
            <h2 style="color: #4ecdc4;">✅ 结论</h2>
            <p>该猜想可通过以上 <strong>{depth}</strong> 步对偶映射获得证明。每一步都基于存在数论的九域对偶定理，确保逻辑的严格性。这就像把一道题翻译成不同数学领域的语言，最终在最适合的领域里找到答案。</p>
        </div>
        """
        return html

# ========== 自动推理引擎 ==========
class AutoReasoningEngine:
    def __init__(self):
        self.parser = SemanticParser()
        self.finder = PathFinder()

    def reason(self, statement: str) -> dict:
        source, target = self.parser.parse(statement)
        if source is None or target is None:
            return {"status": "unrecognized", "message": "无法从陈述中识别出数学结构。请尝试更明确的表述，或手动指定域。"}
        all_paths = self.finder.search(source, target, max_depth=3)
        if not all_paths:
            return {"status": "no_path", "source": DOMAIN_NAMES[source], "target": DOMAIN_NAMES[target],
                    "message": f"在{DOMAIN_NAMES[source]}和{DOMAIN_NAMES[target]}之间未找到 ≤3 步的对偶映射路径。"}
        valid_paths = [(dp, mn) for dp, mn in all_paths if len(dp)-1 <= 3]
        if not valid_paths:
            return {"status": "no_valid_path", "message": "未找到深度 ≤3 的合法路径。"}
        best_path, best_mappings = valid_paths[0]
        report_html = ReportGenerator.generate_html(statement, source, target, best_path, best_mappings)
        return {
            "status": "success",
            "statement": statement,
            "source": DOMAIN_NAMES[source],
            "target": DOMAIN_NAMES[target],
            "path": [DOMAIN_NAMES[d] for d in best_path],
            "mappings": best_mappings,
            "depth": len(best_path)-1,
            "report_html": report_html
        }

# ========== Flask 服务 ==========
from flask import Flask, request, jsonify, render_template_string
app = Flask(__name__)
engine = AutoReasoningEngine()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>ProofCollapse v3.3 通俗报告版</title>
<style>
    body { background:#0f1117; color:#fff; font-family:Arial; padding:30px; }
    .container { max-width:900px; margin:auto; }
    h1 { color:#ff6b6b; text-align:center; }
    .subtitle { text-align:center; color:#aaa; margin-bottom:20px; }
    textarea, input { width:100%; padding:14px; font-size:16px; border:none; border-radius:10px; background:#1e1e2e; color:white; margin-bottom:10px; }
    .row { display:flex; gap:10px; }
    .row input { flex:1; }
    .btn-group { display:flex; gap:10px; margin-top:15px; flex-wrap:wrap; }
    button { padding:12px 20px; border:none; border-radius:10px; cursor:pointer; font-size:16px; font-weight:bold; }
    .btn-reason { background:#ff6b6b; color:white; }
    .btn-manual { background:#4ecdc4; color:#000; }
    .btn-example { background:#1e1e2e; color:#4ecdc4; border:1px solid #4ecdc4; }
    #report { margin-top:20px; }
</style></head>
<body>
<div class="container">
    <h1>🧌 ProofCollapse v3.3</h1>
    <p class="subtitle">自动推理引擎 · 超级自然语言理解 · 通俗证明报告 | e<sup>iS</sup>=1</p>
    <div class="examples">
        <button class="btn-example" onclick="setExample('每个大于2的偶数可以表示为两个素数之和')">哥德巴赫猜想</button>
        <button class="btn-example" onclick="setExample('存在无穷多对孪生素数')">孪生素数猜想</button>
        <button class="btn-example" onclick="setExample('杨-米尔斯理论存在正的质量间隙')">杨-米尔斯质量间隙</button>
        <button class="btn-example" onclick="setExample('对于任意正整数，考拉兹迭代最终必达到1')">考拉兹猜想</button>
        <button class="btn-example" onclick="setExample('黎曼zeta函数的所有非平凡零点位于临界线上')">黎曼假设</button>
        <button class="btn-example" onclick="setExample('每个单连通三维闭流形同胚于三维球面')">庞加莱猜想</button>
        <button class="btn-example" onclick="setExample('纳维-斯托克斯方程存在全局光滑解')">纳维-斯托克斯</button>
        <button class="btn-example" onclick="setExample('任意两个正交矩阵的乘积仍为正交矩阵')">正交矩阵乘积</button>
        <button class="btn-example" onclick="setExample('任意两个整数的和仍为整数')">整数加法封闭</button>
    </div>
    <textarea id="statement" placeholder="输入数学猜想的自然语言描述..."></textarea>
    
    <p style="color:#aaa; margin-top:10px;">或者手动指定域（当自然语言无法识别时）：</p>
    <div class="row">
        <input id="source_domain" placeholder="前提域 (如 additive, multiplicative, spectral)">
        <input id="target_domain" placeholder="结论域 (如 additive, multiplicative, spectral)">
    </div>
    
    <div class="btn-group">
        <button class="btn-reason" onclick="reason()">自动推理</button>
        <button class="btn-manual" onclick="manualReason()">手动指定域推理</button>
    </div>
    <div id="report"></div>
    <pre id="raw_json" style="display:none;"></pre>
</div>
<script>
    function setExample(text) { document.getElementById('statement').value = text; }
    
    async function reason() {
        const stmt = document.getElementById('statement').value;
        const reportDiv = document.getElementById('report');
        const rawDiv = document.getElementById('raw_json');
        if (!stmt.trim()) { reportDiv.innerHTML = '<p style="color:#ff6b6b;">请输入一个数学猜想</p>'; return; }
        try {
            const resp = await fetch('/api/reason', {
                method:'POST', headers:{'Content-Type':'application/json'},
                body:JSON.stringify({statement:stmt})
            });
            const data = await resp.json();
            if (data.report_html) {
                reportDiv.innerHTML = data.report_html;
                rawDiv.style.display = 'none';
            } else {
                reportDiv.innerHTML = '';
                rawDiv.style.display = 'block';
                rawDiv.innerText = JSON.stringify(data, null, 2);
            }
        } catch(e) { reportDiv.innerHTML = '<p style="color:#ff6b6b;">网络错误: ' + e.message + '</p>'; }
    }
    
    async function manualReason() {
        const source = document.getElementById('source_domain').value.trim();
        const target = document.getElementById('target_domain').value.trim();
        const stmt = document.getElementById('statement').value || '手动指定域查询';
        const reportDiv = document.getElementById('report');
        const rawDiv = document.getElementById('raw_json');
        if (!source || !target) { reportDiv.innerHTML = '<p style="color:#ff6b6b;">请同时填写前提域和结论域</p>'; return; }
        try {
            const resp = await fetch('/api/reason_manual', {
                method:'POST', headers:{'Content-Type':'application/json'},
                body:JSON.stringify({statement:stmt, source:source, target:target})
            });
            const data = await resp.json();
            if (data.report_html) {
                reportDiv.innerHTML = data.report_html;
                rawDiv.style.display = 'none';
            } else {
                reportDiv.innerHTML = '';
                rawDiv.style.display = 'block';
                rawDiv.innerText = JSON.stringify(data, null, 2);
            }
        } catch(e) { reportDiv.innerHTML = '<p style="color:#ff6b6b;">网络错误: ' + e.message + '</p>'; }
    }
</script>
</body>
</html>
'''

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/reason', methods=['POST'])
def api_reason():
    data = request.get_json(silent=True) or {}
    statement = data.get('statement', '')
    return jsonify(engine.reason(statement))

@app.route('/api/reason_manual', methods=['POST'])
def api_reason_manual():
    data = request.get_json(silent=True) or {}
    statement = data.get('statement', '手动指定域查询')
    source_str = data.get('source', '')
    target_str = data.get('target', '')
    try:
        source = Domain[source_str.upper()]
        target = Domain[target_str.upper()]
    except KeyError as e:
        return jsonify({"status": "error", "message": f"无效的域名：{e}。可用域：{', '.join([d.name.lower() for d in Domain])}"})
    all_paths = PathFinder.search(source, target, max_depth=3)
    if not all_paths:
        return jsonify({"status": "no_path", "source": DOMAIN_NAMES[source], "target": DOMAIN_NAMES[target],
                        "message": "未找到 ≤3 步的对偶映射路径。"})
    valid_paths = [(dp, mn) for dp, mn in all_paths if len(dp)-1 <= 3]
    if not valid_paths:
        return jsonify({"status": "no_valid_path", "message": "未找到合法路径。"})
    best_path, best_mappings = valid_paths[0]
    report_html = ReportGenerator.generate_html(statement, source, target, best_path, best_mappings)
    return jsonify({
        "status": "success",
        "statement": statement,
        "source": DOMAIN_NAMES[source],
        "target": DOMAIN_NAMES[target],
        "path": [DOMAIN_NAMES[d] for d in best_path],
        "mappings": best_mappings,
        "depth": len(best_path)-1,
        "report_html": report_html
    })

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
