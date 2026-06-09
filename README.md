# Null Model Paradigm (NMP)
> Constraint-First Architecture for Reliable LLM Agents

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.xxxxx.svg)](https://doi.org/10.5281/zenodo.xxxxx)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 核心命题

**当前LLM Agent的崩溃不是工程缺陷，而是架构缺陷。**

当DuMate在8GB内存的消费级设备上尝试整理150个文件时，它连续三次崩溃——这不是因为模型不够聪明，而是因为它**让知识负载的LLM直接接触物理世界**。

NMP的解决方案：**不是给LLM更多知识，而是给它一个"硬壳"——Null Model（空模型）**。

> "The LLM may be infinitely knowledgeable, but it must never touch the file system without passing through the irreversible filter of physics, mathematics, logic, and causality."
> —— *Null Model Paradigm, Zenodo DOI*

---

## 架构本质：三层分离 + 六步流水线

### 三层分离

| 层级 | 名称 | 位置 | 权限 | 核心功能 |
|------|------|------|------|----------|
| **L1** | Intent Injection | 人类 | 不可计算、不可委托 | 提供目的、价值排序、成功标准 |
| **L2** | Null Model | **本地** | **唯一执行权** | 物理预算、数学分解、约束锁定、事实提取、最终判断 |
| **L3** | Full Model (LLM) | 云端/本地 | **零写入权、零执行权** | 语义理解、标签输出、策略生成 |

### 六步流水线

```
1. Problem          → 人类输入自然语言目的
2. Null Model       → 策略计算（物理预算、任务分解、约束锁定）
3. Full Model       → 认知（LLM语义理解，输出文本标签）
4. Database         → 知识检索（外部领域信息）
5. Full Model       → 合成（LLM组装执行蓝图，受Null Model约束）
6. Null Model       → 判断与执行（评估蓝图、选择路径、原子执行、回滚保证）
```

**关键**：LLM不是Null Model的"顾问"，而是被**笼养**在其中的知识源。Null Model不是LLM的"过滤器"，而是**计算策略的主权引擎**。

---

## 核心创新：元规则驱动的感知调度

传统AI：感知器看到一切 → 后端过滤  
**NMP：人类元规则决定感知器"应该看什么"**

```
原始视频流
    ↓
[隐私资料库] 查询元规则：
  • 当前目的是什么？
  • 哪些实体与此目的相关？
  • 哪些信息禁止提取？
    ↓
[空模型] 调度感知器：
  • 只运行人形检测，不运行人脸识别
  • 只提取运动方向，不提取面部特征
    ↓
[事实提取] 输出结构化事实原子
    ↓
[脱敏] → [云端LLM] → [策略返回]
    ↓
[空模型最终判断] 策略是否符合事实+目的？
    ↓
执行 / 拒绝 / 回滚
```

**隐私不是"提取后删除"，而是"提取动作本身被元规则约束"**。

---

## 项目结构

```
nmp-project/
├── README.md                    # 本文件
├── LICENSE                      # MIT
├── docs/
│   ├── architecture.md            # 修正后的Mermaid架构图
│   ├── principles.md              # 论文原理精要（Zenodo DOI）
│   ├── privacy_vault.md           # 隐私资料库设计
│   └── cloud_local_protocol.md    # 云端-本地交互协议
├── local/                         # 本地空模型（核心）
│   └── null_model/
│       ├── __init__.py
│       ├── purpose_parser.py      # 目的形式化
│       ├── causal_skeleton.py     # 因果骨架
│       ├── fact_extractor.py      # 事实提取
│       ├── perception_scheduler.py  # 感知调度器（元规则驱动）
│       ├── privacy_vault.py       # 隐私资料库
│       ├── desensitizer.py        # 脱敏处理
│       ├── final_judgment.py      # 最终判断
│       └── main.py                # 本地主控
├── cloud/                         # 云端LLM接口（最小化）
│   └── llm_client.py
├── protocol/                      # 数据契约
│   └── schema/
│       ├── purpose_schema.json
│       ├── fact_schema.json
│       ├── strategy_schema.json
│       └── metarule_schema.json
├── examples/
│   └── phase1_demo.py             # 系统监控场景演示
└── tests/
    └── test_end_to_end.py
```

---

## 快速开始

```bash
git clone https://github.com/yourname/null-model-paradigm.git
cd null-model-paradigm
pip install -r requirements.txt

# 运行系统监控演示
python examples/phase1_demo.py
```

---

## 引用

```bibtex
@article{loweswang2026nmp,
  title={The Null Model Paradigm: Constraint-First Architecture for Reliable LLM Agents},
  author={loweswang},
  year={2026},
  month={may},
  publisher={Zenodo},
  doi={10.5281/zenodo.xxxxx}
}
```

---

## 许可

MIT License — 详见 [LICENSE](LICENSE)
