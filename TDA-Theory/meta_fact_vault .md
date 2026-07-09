# 元事实库（Meta-Fact Vault）设计

> **版本**: 2.0.0  
> **配套架构**: 三层双视角辩证（TDA）架构  
> **最后更新**: 2026-06-21

## 前提
**对AI使用者来说，没有公共通用的事实，只有个体私域的事实。**


## 一、定位

元事实库是 **TDA架构中空模型的外接事实寄存器**，是**使用者（个人/企业/组织）或其授权代表确认的、有时间刻度的静态事实集合**。

### 核心原则

- **没有无目的的事实**：事实只在特定使用者的特定目的下被提取和使用
- **没有无主人的事实**：事实属于确认它的使用者，LLM只代表使用者说话
- **没有无时间戳的事实**：每个事实都是某个时间刻度上的静态快照
- **矛盾是结构性的**：元事实库内部允许张力（不同时间戳的事实并存、规则与事实的冲突），但不允许逻辑自相矛盾

### 与TDA架构的关系

```
使用者（目的）
  ↓
空模型（先验计算结构：目的→事实类型映射）
  ↓ 查询
元事实库（使用者确认的静态事实快照）
  ↓ 提取+结构化
LLM（在事实约束下生成，代表使用者）
  ↓
结构化辩论层（冲突图：LLM生成 vs 空模型事实）
  ↓
裁决AI（有依据随机：在张力中选择）
  ↓
输出（代表使用者）
  ↓
事实反馈（碰壁或验证）
  ↓
判例库（错误记忆积累）
  ↓
人工审计/外部锚点（最高否决权）
  ↓
元事实库更新（新增静态快照，旧版本保留）
```

### 元事实库 vs LLM训练知识

| 维度 | 元事实库 | LLM训练知识 |
|------|---------|------------|
| **归属** | 使用者确认 | 模型内部权重 |
| **确定性** | 人类确认的静态快照 | 概率性 |
| **修改权** | 仅人类可确认新版本 | 不可直接修改 |
| **可见性** | 空模型只读，LLM完全不可见 | LLM内部可见 |
| **时效性** | 有时间戳，可版本追溯 | 截止到训练cutoff |
| **作用** | 约束LLM生成、提供判断依据 | 提供语言模式、生成候选 |
| **来源** | 使用者确认、系统导入、实时接口 | 互联网语料、预训练数据 |

#

## 二、核心设计哲学

### 2.1 事实的定义

> **事实 = 使用者（或其授权代表）确认的、有时间刻度的静态快照。**

- **个人属性**：性别、年龄、病历、过敏史
- **企业规则**：考勤制度、罚款标准、营销策略
- **设备参数**：型号、规格、运行状态（某时刻）
- **实时数据**：股价（某时刻）、传感器读数（某时刻）、交通信号（某时刻）
- **策略方向**：企业决策、个人计划、风险偏好

**不是事实的**：
- 公共常识（水沸100°C）—— LLM已训练，无需存入
- 通用领域知识（胃炎定义）—— LLM已训练，无需存入
- 未经确认的信息—— 不属于任何使用者的事实

### 2.2 静态的含义

> **静态 = 有时间刻度的确定性。**

```
T1: "诊断：慢性胃炎中度" —— 静态快照，2024-03-15
T2: "胃炎已治愈" —— 静态快照，2025-06-01

两个事实并存，不矛盾。
T1不会变成"假的"，它只是"在T1时刻为真"。
T2不是"修改"T1，是"新增一个时间戳的事实"。
```

元事实库是**静态快照的集合**，变化不是"库在动"，是"新的快照加入"。

### 2.3 矛盾的处理

| 矛盾类型 | 处理方式 | 示例 |
|---------|---------|------|
| **时间版本矛盾** | ✅ 正常并存 | T1"有病"与T2"无病" |
| **规则与事实矛盾** | ✅ 正常，暴露给冲突图 | 企业规则"罚款500" vs 员工事实"未签字" |
| **不同使用者的事实矛盾** | ✅ 正常，各自代表 | 员工A"太阳绕地球" vs 员工B"地球绕太阳" |
| **逻辑自相矛盾** | ❌ 不允许修复 | 同一时间戳同一事实既真又假 |
| **元事实库对LLM可见** | ❌ 不允许修复 | 违反架构隔离 |

#

## 三、数据结构

### 3.1 顶层结构

```json
{
  "vault_id": "user_master_v1",
  "version": "2026.06.26",
  "owner": "使用者身份标识",
  "owner_type": "individual|enterprise|organization",
  "purposes": ["health_reminder", "anomaly_detection"],
  "note": "purposes由使用者或其授权代表命名，非系统预设领域",
  "facts": [...],
  "constraints": [...],
  "ontology_mappings": [...],
  "meta_facts": [...],
  "logs": [...]
}
```

### 3.2 事实层（Facts）

使用者确认的一切事实，按类型分类但不分层级。

```json
{
  "fact_id": "F001",
  "content": {
    "entity": "medical_history",
    "attributes": {
      "condition": "gastritis",
      "severity": "moderate",
      "diagnosed_date": "2024-03-15"
    }
  },
  "type": "personal_fact",
  "confirmed_by": "user",
  "confirmed_at": "2024-03-15T10:00:00",
  "source": "hospital_record_import",
  "status": "active",
  "effective_from": "2024-03-15",
  "effective_until": null,
  "superseded_by": null,
  "superseded_at": null,
  "related_cases": [],
  "version": 1
}
```

**字段说明：**

| 字段 | 类型 | 说明 |
|-----|------|------|
| `fact_id` | string | 唯一标识 |
| `content` | object | 事实内容（实体+属性） |
| `type` | string | 事实类型标签，不影响存储 |
| `confirmed_by` | string | 确认者身份 |
| `confirmed_at` | ISO8601 | 确认时间戳 |
| `source` | string | 来源（导入/录入/系统接口） |
| `status` | enum | `active`/`historical`/`revoked` |
| `effective_from` | ISO8601 | 生效时间 |
| `effective_until` | ISO8601 | 失效时间（null=未失效） |
| `superseded_by` | string | 替代者fact_id（历史版本用） |
| `superseded_at` | ISO8601 | 被替代时间 |
| `related_cases` | array | 关联判例库ID（预留） |
| `version` | int | 版本号 |

### 3.3 约束层（Constraints）

使用者确认的提取限制，与Facts并列，同属"使用者确认层"。

```json
{
  "constraint_id": "C001",
  "content": {
    "name": "入侵检测隐私规则",
    "trigger": {
      "entities": ["human_shape"],
      "context": ["camera_feed"]
    },
    "permitted": [
      {"entity": "human_shape", "attributes": ["presence", "count"]}
    ],
    "forbidden": [
      {"entity": "face", "attributes": ["identity", "emotion"]}
    ]
  },
  "type": "enterprise_rule",
  "confirmed_by": "企业安全负责人_王五",
  "confirmed_at": "2025-03-01",
  "status": "active",
  "version": 1
}
```

**注意：** Constraints不是系统预设，是使用者确认的事实（规则事实）。

### 3.4 领域本体映射（Ontology Mappings）

将领域实体映射到因果骨架的形式节点，实现跨领域复用。

```json
{
  "mapping_id": "M001",
  "description": "系统监控领域的因果骨架映射",
  "confirmed_by": "system_admin",
  "confirmed_at": "2025-01-01",
  "mappings": {
    "memory": {
      "high_usage": "Node_A",
      "low_free": "Node_B",
      "pressure": "Node_C"
    },
    "cpu": {
      "high_usage": "Node_D",
      "pressure": "Node_E"
    }
  }
}
```

**注意：** Ontology Mappings是系统配置层，但由人类维护，空模型只读。

### 3.5 元事实（Meta-Facts）

关于感知器特性的校准参数，用于调整提取置信度。

```json
{
  "meta_fact_id": "MF001",
  "entity": "video_camera",
  "attribute": "night_mode",
  "fact": "夜间帧率从30fps降至15fps，人形检测置信度需下调0.15",
  "calibration": {
    "day_confidence": 0.85,
    "night_confidence": 0.70
  },
  "confirmed_by": "system_admin",
  "confirmed_at": "2025-01-01"
}
```

### 3.6 日志（Logs）

空模型查询元事实库的历史记录，用于优化查询策略，**不是判例库**。

```json
{
  "log_id": "L001",
  "timestamp": "2026-06-08T23:15:00",
  "purpose": "anomaly_detection",
  "queried_facts": ["F001", "F002"],
  "extracted_entities": ["human_shape.presence", "human_shape.count"],
  "outcome": "success"
}
```

#

## 四、查询接口

空模型通过以下接口查询元事实库：

```python
# 伪代码
vault = MetaFactVault.load("user_master_v1")

# 1. 根据目的和所需实体类型查询事实
facts = vault.query_facts(
    purpose="diagnose_stomach_pain",
    owner="user_001",
    required_entities=["medical_history", "today_log", "allergies"]
)
# 返回：当前active的事实快照集合

# 2. 查询约束
constraints = vault.query_constraints(
    entities=["human_shape"],
    context=["camera_feed"]
)
# 返回：使用者确认的提取限制

# 3. 获取领域本体映射
mapping = vault.get_ontology_mapping(
    mapping_id="M001"
)
# 返回：实体到形式节点的映射

# 4. 获取元事实校准
meta = vault.get_meta_fact(
    entity="video_camera",
    attribute="night_mode"
)
# 返回：感知器校准参数
```

**关键原则：**
- 空模型决定"要什么"（先验计算结构）
- 元事实库回答"有什么"（静态快照）
- 查询结果只包含`status: active`的事实
- 历史版本通过`superseded_by`追溯

#

## 五、更新机制

### 5.1 事实更新

```
人类确认新版本 → 新增事实快照（version+1）
  → 旧事实标记为historical
  → 旧事实.superseded_by = 新事实.fact_id
  → 判例库关联（如适用）
```

**不是编辑覆盖，是版本演进。**

### 5.2 约束更新

同事实更新，约束也是使用者确认的事实，可版本化。

### 5.3 自动更新（仅限日志反馈）

```
日志积累 → 查询模式分析 → 提取策略优化（空模型侧）
  → 元事实库本身不自动更新
  → 只有人类确认后才新增/修正事实
```

### 5.4 版本控制

```json
{
  "vault_id": "user_master_v1",
  "version": "2026.06.26",
  "version_history": [
    {"version": "2026.06.01", "changes": "新增医疗事实"},
    {"version": "2026.05.15", "changes": "修正设备参数"}
  ]
}
```

#

## 六、与判例库的关系

元事实库与判例库是**辩证关系**：

| | 元事实库 | 判例库 |
|--|---------|--------|
| **性质** | 肯定性：我相信什么 | 否定性：我曾因此碰壁 |
| **方向** | 指导当前行动 | 约束未来行动 |
| **更新** | 人类确认新版本 | 自动积累+人类确认 |
| **作用** | LLM代表我的立场 | 标记我的立场的边界 |
| **关系** | 判例库触发元事实库修正 | 元事实库为判例库提供前提 |

**判例库接口（预留）：**

```json
{
  "fact_id": "F001",
  "related_cases": ["C001", "C002"],
  "falsification_history": [
    {"case_id": "C001", "timestamp": "2025-06-01", "outcome": "bounced"}
  ]
}
```

#

## 七、与LLM的隔离

**元事实库对LLM完全不可见。**

LLM：
- 不知道存在哪些事实
- 不知道哪些事实被过滤
- 不知道哪些约束被启用
- 不知道元事实库的存在
- 只接收**脱敏后的结构化事实**

这是架构防火墙：即使LLM被攻击或越狱，也无法绕过元事实库的约束——因为约束在**本地空模型**中执行，不在云端。

#

## 八、跨领域复用

### 复用原则

- **因果骨架**：空模型内置，跨领域复用（纯形式，无内容）
- **本体映射**：元事实库中配置，人类维护（领域实体→形式节点）
- **事实层**：每个使用者独立，不共享

### 示例

**场景1：系统监控**
- 元骨架：`Node_A --causal--> Node_B`
- 元事实库映射：`memory.high_usage → Node_A`
- 元事实库事实：我的设备参数、我的系统日志

**场景2：医疗诊断**
- **同一套元骨架**：`Node_A --causal--> Node_B`（零修改）
- 元事实库映射（新增）：`blood_pressure.high → Node_A`
- 元事实库事实：我的病历、我的检验结果

**场景3：金融风控**
- **同一套元骨架**：`Node_A --causal--> Node_B`（零修改）
- 元事实库映射（新增）：`credit_score.low → Node_A`
- 元事实库事实：我的持仓、我的交易记录

**结论**：跨领域扩展不需要修改因果骨架，只需要在元事实库中新增**本体映射**和**使用者事实**。

#

## 九、设计原则总结

| 原则 | 含义 |
|-----|------|
| **目的中心** | 事实只在特定使用者的特定目的下被提取 |
| **主权归属** | 事实属于确认它的使用者，LLM只代表使用者 |
| **时间刻度** | 每个事实都是静态快照，有确认时间戳 |
| **版本演进** | 变化不是修改，是新增快照，旧版本保留 |
| **矛盾结构** | 允许张力（不同时间戳、规则vs事实），不允许逻辑自相矛盾 |
| **否定学习** | 判例库记录碰壁，触发元事实库修正，系统自学习 |
| **隔离防火墙** | 元事实库对LLM完全不可见，约束在本地执行 |

#

## 十、术语对照

| 术语 | 别名 | 说明 |
|-----|------|------|
| 元事实库 | Meta-Fact Vault, KB1, 隐私资料库 | 本设计的主体 |
| 空模型 | Empty Model | 先验计算结构，无内容 |
| 判例库 | Case Law | 错误记忆，否定性知识 |
| 因果骨架 | Causal Skeleton | 空模型内置的形式结构 |
| 有依据随机 | Informed Randomness | 裁决AI在张力中的选择机制 |
| 最高否决权 | Supreme Veto | 人工审计/外部锚点的最终裁决 |

#

 **元事实库不是"关于世界的知识"，是"关于使用者的档案"——使用者确认的、有时间刻度的、可版本追溯的静态事实集合。LLM在这些事实的约束下生成，不是自由发挥，是代表主人说话。**

---
