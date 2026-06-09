# ⚠️ Null Model Paradigm (NMP)

&gt; Constraint-First Architecture for Reliable LLM Agents

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ⚠️ 项目状态声明

**当前阶段：理论框架 + 概念验证（Proof of Concept）**

**这不是一个可用的产品。这是一个范式提案。**

### 已完成
- ✅ 论文发表（Zenodo DOI）
- ✅ 架构设计（三层分离、六步流水线）
- ✅ 核心概念验证（系统监控场景）
- ✅ 隐私资料库数据结构（知识+规则+日志+元事实）
- ✅ 感知调度器（**提取前调度**，隐私数据从未暴露）
- ✅ 物理预算模块（LLM调用前资源计算）
- ✅ 原子执行器（事务性执行+回滚）

### 未完成（需要社区贡献）
- ❌ 真正的因果骨架自动生成（当前是手工节点）
- ❌ 真正的目的解析器（当前是关键词匹配）
- ❌ 真正的探针系统（视频/音频/硬件接口）
- ❌ 真正的LLM接口（当前是模拟响应）
- ❌ 可安装包（`pip install null-model`）
- ❌ 跨平台支持（Windows/Mac/Linux）

### ⚠️ 使用警告

**DO NOT USE IN PRODUCTION.**

当前代码仅用于：
- 学术研究
- 架构验证
- 社区讨论

---

## 核心命题

当前LLM Agent的崩溃不是工程缺陷，而是**架构缺陷**。

当DuMate在8GB内存的消费级设备上尝试整理150个文件时，它连续三次崩溃——这不是因为模型不够聪明，而是因为它**让知识负载的LLM直接接触物理世界**。

NMP的解决方案：**不是给LLM更多知识，而是给它一个"硬壳"——Null Model（空模型）**。

&gt; "The LLM may be infinitely knowledgeable, but it must never touch the file system without passing through the irreversible filter of physics, mathematics, logic, and causality."
&gt; —— *Null Model Paradigm, Zenodo DOI*

---

## 架构本质

### 三层分离

| 层级 | 名称 | 位置 | 权限 | 核心功能 |
|------|------|------|------|----------|
| **L1** | Intent Injection | 人类 | 不可计算、不可委托 | 提供目的、价值排序、成功标准 |
| **L2** | Null Model | **本地** | **唯一执行权** | 物理预算、数学分解、约束锁定、事实提取、最终判断 |
| **L3** | Full Model (LLM) | 云端/本地 | **零写入权、零执行权** | 语义理解、标签输出、策略生成 |

### 六步流水线

1. **Problem** → 人类输入目的
2. **Null Model (Strategy)** → 物理预算、任务分解、约束锁定、感知调度
3. **Full Model (Cognition)** → LLM语义理解
4. **Database (Knowledge)** → 隐私资料库查询
5. **Full Model (Synthesis)** → LLM组装策略
6. **Null Model (Judgment & Execution)** → 评估、选择、**原子执行、回滚**

---

## 快速开始（概念验证）

```bash
git clone https://github.com/yourname/null-model-paradigm.git
cd null-model-paradigm

# 运行系统监控演示
python examples/phase1_demo.py
项目结构
null-model-paradigm/
├── README.md                    # 本文件
├── LICENSE                      # MIT
├── requirements.txt             # 依赖
├── docs/                        # 文档
│   ├── architecture.md            # 架构设计
│   ├── principles.md              # 论文原理精要
│   ├── privacy_vault.md           # 隐私资料库设计
│   └── cloud_local_protocol.md    # 云端-本地交互协议
├── local/                         # 本地空模型（核心）
│   └── null_model/
│       ├── __init__.py
│       ├── main.py                  # 主控器
│       ├── privacy_vault.py         # 隐私资料库
│       ├── perception_scheduler.py  # 感知调度器
│       ├── final_judgment.py        # 最终判断
│       ├── physical_budget.py       # 物理预算
│       ├── atomic_executor.py       # 原子执行
│       ├── purpose_parser.py        # 目的解析
│       ├── causal_skeleton.py       # 因果骨架
│       ├── fact_extractor.py        # 事实提取
│       └── desensitizer.py         # 脱敏处理
├── cloud/                         # 云端LLM接口
│   └── llm_client.py
├── protocol/                      # 数据契约
│   └── schema/
│       ├── purpose_schema.json
│       ├── fact_schema.json
│       ├── strategy_schema.json
│       └── metarule_schema.json
├── examples/                      # 示例
│   └── phase1_demo.py
└── tests/                         # 测试（待添加）
我们需要你的帮助
这不是一个产品路线图。这是一个计算范式的提案。
表格
技能	贡献方向
形式逻辑/本体论	因果骨架自动扩展
NLP/语义解析	目的形式化解析器
计算机视觉	视频探针模块
语音识别	音频探针模块
系统编程	原子执行器优化
LLM工程	真实LLM接口适配
安全审计	约束不可变性证明
如何参与
阅读 论文原理
运行 演示
在 Discussions 提出你的想法
提交 Issue 或 Pull Request
愿景
让每个人都能在本地安装一个主权判断引擎——
它不为任何云服务提供商工作，只为你的目的服务。
它不积累知识，只保持判断的纯粹。
它不侵犯隐私，因为隐私是架构的根基，不是后加的补丁。
我们需要建造者，而不只是用户。
引用
@article{loweswang2026nmp,
  title={The Null Model Paradigm: Constraint-First Architecture for Reliable LLM Agents},
  author={loweswang},
  year={2026},
  month={may},
  publisher={Zenodo},
  doi={10.5281/zenodo.xxxxx}
}
许可
MIT License — 详见 LICENSE
