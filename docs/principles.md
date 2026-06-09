# NMP 论文原理精要

> 来源：*The Null Model Paradigm: Constraint-First Architecture for Reliable LLM Agents*  
> 作者：loweswang  
> 发布：Zenodo正式版（DOI），2026年5月30日

---

## 一、问题诊断：DuMate崩溃的范式意义

### 观察事实
2026年5月30日，DuMate（本地部署的AI办公助手）在消费级设备（i5-7400, 8GB RAM, 120GB SSD, Win10）上执行文件整理任务时：
- 任务：整理约100个文本文件和数十个Word文档
- 指令："按内容和类型整理；汇总相同内容；保留原文件；保存到kb文件夹"
- 结果：连续三次失败，报错Internal Server Error: Bad Gateway

### 核心论点
**这不是实现缺陷，而是范式缺陷。**

当前Agent采用**Full-Model Paradigm（全模型范式）**：让单一LLM同时承担理解意图、规划操作、执行物理动作。LLM满载互联网语料、文化知识、统计模式，却缺乏物理世界所需的骨架结构。

---

## 二、AlphaGo直觉：结构先例

| 组件 | AlphaGo | NMP Agent |
|------|---------|-----------|
| 问题来源 | 对手的棋步 | 人类意图 + 世界状态 |
| 判断引擎 | MCTS + 价值网络 | **Null Model** |
| 知识来源 | 人类棋谱 / 自我对弈 | LLM + 数据库 |
| 最终权威 | 引擎选择棋步 | **Null Model选择动作** |

**关键洞察**：AlphaGo/AlphaZero的搜索-评估引擎**没有围棋文化、没有人类直觉、没有开局库**——它只有通用的计算骨架（搜索、评估、选择）。人类棋谱只是候选来源，引擎决定哪一步真正执行。

NMP将这一分离推广到物理世界Agent：
- **LLM是开局库（Opening Book）**——提供候选策略
- **Null Model是棋手（Player）**——计算、评估、选择、执行

---

## 三、形式定义

### Full Model（全模型）
知识层被领域语料、文化经验、价值偏好、自主目标生成机制**最大化饱和**的AI系统。当代LLM（GPT-4、Qwen、Claude）及其衍生Agent是典型全模型。

### Null Model（空模型）
**知识自由的计算判断基底（Knowledge-free computational judgment substrate）**。

"Null"不是空集（∅），而是**撤离（Evacuation）**：
- 系统性地剥离所有偶然知识（领域语料、文化经验、价值偏好、自主目的）
- 保留完整的先验算法骨架（判断、搜索、评估、约束满足、最优路径选择）
- 不包含领域知识、文化数据、价值偏好、自主目的

**操作输入**：
1. 人类目的（Human Purpose）
2. 物理世界状态（Physical-world State）
3. 形式约束（物理学、数学、逻辑、因果性）

**操作输出**：
- 允许的动作序列（Permitted Action Sequences）
- 执行裁决（Execution Verdicts）

**所有语义解释所需的知识都向Full Model（LLM）查询，但LLM对Null Model的裁决零修改权。**

### 六步流水线（Six-Step Pipeline）

1. **Problem**：人类以自然语言表达意图
2. **Null Model (Strategy Computation)**：物理资源预算、数学任务分解、约束锁定、候选执行路径生成
3. **Full Model (Cognition)**：LLM执行语义理解与分类，只输出文本标签和知识片段
4. **Database (Knowledge)**：外部检索领域特定信息
5. **Full Model (Synthesis)**：LLM在Null Model约束下组装文本-only执行蓝图
6. **Null Model (Judgment & Execution)**：评估LLM蓝图的形式约束符合性，选择最优允许路径，强制执行原子性，提供回滚保证
7. **Solution**：物理世界执行结果

---

## 四、三层架构防火墙

### L1：意图注入（Intent Injection）——人类主权
人类提供目标、价值排序、成功标准。这一层**不可计算、不可委托**。

### L2：Null Model层——计算判断引擎
**唯一拥有物理世界执行权限的层**。它不只是"过滤"LLM输出，而是**从零计算执行策略**。LLM（L3）拥有：
- 零文件系统写入权限
- 零进程生成权限
- 零修改执行计划权限

**四个刚性计算模块**：

1. **Physical Budgeting Module**：监控RAM、磁盘空间、文件句柄、网络状态。在调用任何LLM之前计算安全批次大小（如8GB机器上每批10个文件）。

2. **Mathematical Planning Module**：在复杂度和资源约束下将任务分解为最优原子操作序列。这是**规划计算**，不是知识查询。

3. **Constraint Formalization Module**：将自然语言意图转化为不可变的逻辑断言。例如"不删除原文件"形式化为公理 ¬Delete(S_source)，永久剪枝Delete类中的任何候选操作。

4. **Verification & Rollback Module**：强制执行因果性（每个效果有可追溯的原因）、同一性（复制文件保持校验和一致）、可逆性（每批要么全提交要么全回滚）。

### L3：Full Model层——生成认知
LLM和外部数据库在此运行。它们的唯一权限：
- 读取文件内容（文本-only输入）
- 输出文本标签（如"Contract"、"Meeting Minutes"）
- 生成人类可读摘要

**零文件系统写入权限、零进程生成权限、零修改执行计划权限。**

---

## 五、DuMate案例：反事实分析

### 全模型范式的失败链
1. **无物理预算**：LLM尝试同时处理150+文件，耗尽8GB RAM
2. **无原子性**：操作未分批次；中途崩溃导致文件系统不一致
3. **无回滚**：遇到Bad Gateway时，Agent生成道歉文本而非回滚部分复制
4. **语言歧义**：LLM"统计性理解"了请求，但没有对"保留原文件"的形式锁定

**LLM不是在"被缺失层支撑"，而是在物理世界上裸体翻滚。**

### NMP范式的反事实成功
1. **L2物理模块**扫描F:i：150个文件，总大小X，可用RAM≈4GB（扣除OS占用）。计算安全批次大小为10。
2. **L2约束模块**形式化意图：Operation ∈ {Copy}, ¬Delete, ¬Move。
3. **L3 LLM**每批只接收10个文件的文本内容，返回标签（如"Contract"）。
4. **L2**清洗标签（剥离路径遍历字符、阻断保留名称）。
5. **L2**执行Copy(src, dst)，验证校验和同一性（MD5_src = MD5_dst），因果日志记录，继续执行。
6. **如果LLM超时（Bad Gateway）**，L2不会崩溃。它优雅降级：标签默认回退到文件扩展名，复制继续执行，异常记录供人类审查。

---

## 六、形式保证

NMP架构提供全模型范式无法提供的三项结构保证：

1. **Resource Safety（资源安全）**：Null Model在调用LLM之前先预算资源，保证物理耗尽不可能由LLM过度生成导致。

2. **Constraint Immutability（约束不可变性）**：一旦¬Delete(S)在L2中被形式化，任何LLM输出都无法覆盖它——由架构防火墙保证。

3. **Graceful Degradation（优雅降级）**：如果L3失败（超时、幻觉），L2回退到确定性默认值，保证系统始终处于安全状态。

---

## 七、AGI启示

当前工业实践通过**饱和**追求AGI：更多参数、更多数据、更多模态、更多自主行为。NMP认为这是一个**范畴错误**。

AGI不是一个膨胀的、"无所不知"的Full Model；它是一个最小的、"永不跌倒"的Null Model。

安全AGI的路径不是：
```
More Data → More Knowledge → More Autonomy
```

而是：
```
Harder Constraints → Reliable Judgment → Safe Execution
```

---

## 八、核心论断

> "The DuMate failure is not an anecdote; it is a paradigm indicator. LLM agents will continue to collapse in physical environments until the industry recognizes that generation without constraint is hallucination, and execution without judgment is destruction."

> "The Null Model Paradigm does not reject LLMs; it cages them. The Null Model does not merely cage the LLM; it out-computes it on the only axis that matters for physical reliability: the ability to plan, evaluate, and execute under hard constraints without hallucinating authority."

> "Intelligence is not the accumulation of knowledge; it is the discipline to know when not to act—and the hard shell that enforces that discipline."
