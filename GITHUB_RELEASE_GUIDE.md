# GitHub 项目发布指南

## 项目信息

- **名称**: `null-model-paradigm`
- **描述**: Null Model Paradigm: Constraint-First Architecture for Reliable LLM Agents
- **标签**: `ai-safety`, `llm-agents`, `architecture`, `causal-reasoning`, `privacy`
- **许可**: MIT

## 发布步骤

### 1. 创建GitHub仓库

```bash
# 方式A: 使用GitHub CLI
gh repo create null-model-paradigm   --public   --description "Null Model Paradigm: Constraint-First Architecture for Reliable LLM Agents"   --homepage "https://zenodo.org/record/xxxxx"   --license MIT

# 方式B: 在GitHub网页手动创建
# https://github.com/new
# 填写名称、描述、选择MIT License
```

### 2. 推送代码

```bash
cd nmp-project
git init
git add .
git commit -m "Initial commit: NMP architecture, Phase 1 prototype, privacy vault, perception scheduler"

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/null-model-paradigm.git

# 推送
git branch -M main
git push -u origin main
```

### 3. 创建Release并获取DOI

#### 通过Zenodo获取DOI:

1. 登录 https://zenodo.org
2. 进入 Settings → GitHub → 连接GitHub账户
3. 启用 `null-model-paradigm` 仓库的自动归档
4. 在GitHub创建Release:
   ```bash
   git tag -a v0.1.0 -m "Phase 1: System monitoring prototype with privacy vault"
   git push origin v0.1.0
   ```
5. Zenodo自动生成DOI，更新README中的DOI链接

### 4. 配置GitHub Pages

```bash
# 在仓库 Settings → Pages → Source 选择 main/docs
# 或使用GitHub Actions自动生成
```

### 5. 添加项目徽章

在README.md顶部添加:

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.xxxxx.svg)](https://doi.org/10.5281/zenodo.xxxxx)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
```

## 项目结构说明

```
null-model-paradigm/
├── README.md              # 项目总览 + 论文精要
├── LICENSE                # MIT License
├── requirements.txt       # 依赖
├── .gitignore            # Git忽略规则
├── docs/                 # 文档（GitHub Pages源）
│   ├── architecture.md    # Mermaid架构图
│   ├── principles.md    # 论文原理精要
│   ├── privacy_vault.md # 隐私资料库设计
│   └── cloud_local_protocol.md # 交互协议
├── local/                # 本地空模型（核心）
│   └── null_model/
│       ├── __init__.py
│       ├── main.py       # 主控器
│       ├── privacy_vault.py      # 隐私资料库
│       ├── perception_scheduler.py # 感知调度器
│       ├── final_judgment.py       # 最终判断
│       ├── purpose_parser.py       # 目的解析
│       ├── causal_skeleton.py      # 因果骨架
│       ├── fact_extractor.py       # 事实提取
│       └── desensitizer.py        # 脱敏处理
├── cloud/                # 云端LLM接口
│   └── llm_client.py     # 最小化客户端
├── protocol/             # 数据契约
│   └── schema/
│       ├── purpose_schema.json
│       ├── fact_schema.json
│       ├── strategy_schema.json
│       └── metarule_schema.json
├── examples/             # 示例
│   └── phase1_demo.py    # 系统监控演示
└── tests/                # 测试
```

## 后续开发计划

| Phase | 目标 | 时间 |
|-------|------|------|
| Phase 1 | 系统监控场景 + 隐私资料库 | 已完成 |
| Phase 2 | 动态因果骨架扩展 + 时序推理 | 2-4周 |
| Phase 3 | 视频/音频感知调度 + 多模态 | 1-2月 |
| Phase 4 | 完整DuMate-like场景复现 | 2-3月 |
| Phase 5 | 学术论文投稿（NeurIPS/ICML） | 3-6月 |

## 社区贡献

欢迎提交:
- 新的探针模块（系统/网络/硬件）
- 新的因果骨架节点（医疗/金融/工业）
- 隐私资料库规则模板
- 多语言目的解析器
- 测试用例和基准

## 联系方式

- 论文作者: loweswang
- 项目维护: [GitHub Issues](https://github.com/YOUR_USERNAME/null-model-paradigm/issues)
- 讨论: [GitHub Discussions](https://github.com/YOUR_USERNAME/null-model-paradigm/discussions)
