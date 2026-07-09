# 云端-本地交互协议（Cloud-Local Protocol）

> **版本**: nmp-2.0  
> **配套架构**: 三层双视角辩证（TDA）架构 + 双相理论  
> **最后更新**: 2026-06-26

#

## 前提

**对AI使用者来说，没有公共通用的事实，只有个体私域的事实。**

## 一、协议定位

这是**空模型（本地）与LLM（云端/本地大模型）之间的数据契约**，更是**使用者事实主权的代理链条**。

本协议定义：
1. 空模型向LLM发送什么（**使用者确认的、有时间刻度的私域事实**）
2. LLM向空模型返回什么（**在事实约束下、代表使用者立场的生成文本**）
3. 系统向判例库反馈什么（**事实层面的碰壁记录，驱动自学习闭环**）
4. 双方都不允许做什么（**LLM无资格越界，因为它看不到边界外**）



## 二、核心原则

### 2.1 事实主权原则

- **没有公共通用的事实，只有个体私域的事实**
- 空模型提取的每一条事实，必须有 `owner` 和 `confirmed_by`
- LLM接收的事实，不是"客观数据"，是"**使用者要求LLM服从的事实**"

### 2.2 代表原则

- LLM不是"给出建议"，是"**代表使用者说话**"
- LLM的输出立场 = 输入事实的 `owner`
- LLM不声称"我认为"，只陈述"**根据您的事实，...**"

### 2.3 静态快照原则

- 事实不是"当前状态"，是"**某时间刻度的静态快照**"
- 每个事实带 `timestamp` 和 `version`，可追溯、可验证
- LLM在生成时，明确基于哪个时间戳的事实

### 2.4 闭环反馈原则

- 每次交互不是 Stateless 的结束，是**判例库积累的输入**
- 事实层面的碰壁（预测错误、行动失败、与外部验证冲突）必须回传
- 系统通过负向积累自学习，越用越老练

### 2.5 无资格原则

- LLM**没有资格**请求额外数据、访问外部知识、修改执行计划
- 不是"被禁止"，是"**根本看不到、想不到、做不到**"
- 空模型已经替LLM完成了事实筛选，LLM只接收**领地内的东西**

## 三、消息类型总览

| 消息类型 | 方向 | 说明 |
|---------|------|------|
| `fact_constrained_request` | 本地 → 云端 | 空模型向LLM发送事实约束包 |
| `stance_response` | 云端 → 本地 | LLM在约束下生成的代表立场文本 |
| `feedback_bounce` | 本地 → 系统 | 事实层面碰壁反馈，入判例库 |
| `error` | 双向 | 协议层错误 |


## 四、请求格式（本地 → 云端）

### 4.1 消息头

```json
{
  "protocol_version": "nmp-2.0",
  "message_type": "fact_constrained_request",
  "session_id": "uuid-xxx",
  "timestamp": "2026-06-26T12:00:00Z",
  "owner": "user_001",
  "purpose": "diagnose_stomach_pain"
}
```

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `owner` | string | **事实主权者**，LLM将代表此人说话 |
| `purpose` | string | 使用者目的，空模型据此决定提取哪些事实类型 |

### 4.2 事实约束包（Fact Constraint Package）

```json
{
  "facts": [
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
      "confirmed_by": "user_001",
      "confirmed_at": "2024-03-15T10:00:00Z",
      "status": "active",
      "version": 1
    },
    {
      "fact_id": "F002",
      "content": {
        "entity": "today_log",
        "attributes": {
          "breakfast": "油条豆浆",
          "lunch": "麻辣烫",
          "dinner": null
        }
      },
      "type": "personal_fact",
      "confirmed_by": "user_001",
      "confirmed_at": "2026-06-26T08:00:00Z",
      "status": "active",
      "version": 1
    }
  ],
  "constraints": [
    {
      "constraint_id": "C001",
      "content": {
        "forbidden_entities": ["full_medical_history", "family_genetics"],
        "permitted_entities": ["medical_history", "today_log", "allergies"]
      },
      "confirmed_by": "user_001",
      "confirmed_at": "2025-01-01T00:00:00Z"
    }
  ],
  "uncertainty_boundary": [
    {
      "type": "unextractable",
      "reason": "此目的下，实体'family_genetics'被约束层禁止提取",
      "entity": "family_genetics"
    },
    {
      "type": "missing_snapshot",
      "reason": "今日用药记录尚未确认入库",
      "entity": "medication_taken_today"
    }
  ],
  "instruction": "基于以上使用者确认的事实与约束，代表使用者立场生成回答。禁止引入外部知识。禁止声称'我认为'。"
}
```

**关键变化：**

| 维度 | nmp-1.0（旧） | nmp-2.0（新） |
|------|-------------|-------------|
| 事实性质 | "脱敏后的结构化数据" | "**使用者确认的私域事实快照**" |
| 约束来源 | 系统预设隐私规则 | "**使用者确认的约束事实**" |
| 缺失说明 | "数据缺失" | "**此目的下不可触碰/未确认入库**" |
| 指令 | "禁止引入外部知识" | "**代表使用者立场，禁止声称'我认为'**" |


## 五、响应格式（云端 → 本地）

### 5.1 成功响应

```json
{
  "protocol_version": "nmp-2.0",
  "message_type": "stance_response",
  "session_id": "uuid-xxx",
  "timestamp": "2026-06-26T12:00:02Z",
  "owner": "user_001",
  "purpose": "diagnose_stomach_pain",

  "stance": {
    "representing": "user_001",
    "based_on_facts": ["F001", "F002"],
    "based_on_constraints": ["C001"],
    "confidence": 0.85
  },

  "generated_text": "根据您的病历（慢性胃炎中度，2024年确诊）和今日饮食（早餐油条豆浆、午餐麻辣烫），推测胃部不适可能与午餐辛辣刺激有关。建议...",

  "reasoning_trace": [
    {
      "step": 1,
      "premise": "F001: 慢性胃炎中度",
      "inference": "胃黏膜存在慢性炎症基础"
    },
    {
      "step": 2,
      "premise": "F002: 午餐麻辣烫",
      "inference": "辛辣刺激可能诱发炎症反应"
    }
  ],

  "uncertainty_acknowledged": [
    {
      "type": "fact_boundary",
      "description": "未获取今日用药记录，建议中不涉及药物交互"
    },
    {
      "type": "external_knowledge_excluded",
      "description": "未引入通用医学知识，仅基于使用者提供的事实推理"
    }
  ],

  "fallback": {
    "trigger_condition": "若症状持续或加重",
    "action": "建议使用者确认最新病历事实并重新查询"
  }
}
```

**关键变化：**

| 维度 | nmp-1.0（旧） | nmp-2.0（新） |
|------|-------------|-------------|
| 输出定位 | "策略建议" | "**代表使用者立场的生成文本**" |
| 置信度 | 模型内部概率 | "**在事实约束下的推理置信度**" |
| 推理说明 | "总体推理" | "**基于哪条事实、哪步推导**"（可追溯） |
| 不确定性 | "知识缺失" | "**主人事实未覆盖，故不涉及**" |

### 5.2 错误响应

```json
{
  "protocol_version": "nmp-2.0",
  "message_type": "error",
  "session_id": "uuid-xxx",
  "error_code": "INSUFFICIENT_FACTS_FOR_PURPOSE",
  "error_message": "当前目的所需的核心事实未被确认入库，无法代表使用者立场生成回答",
  "missing_facts": [
    {
      "entity": "medical_history",
      "reason": "owner=user_001 未确认任何病历事实",
      "action_required": "请使用者确认或导入病历事实"
    }
  ],
  "fallback": {
    "action": "拒绝生成",
    "reason": "无事实，不立场"
  }
}
```

## 六、反馈格式（本地 → 判例库系统）

**新增消息类型**，驱动自学习闭环。

```json
{
  "protocol_version": "nmp-2.0",
  "message_type": "feedback_bounce",
  "session_id": "uuid-xxx",
  "timestamp": "2026-06-26T14:00:00Z",
  "owner": "user_001",
  "purpose": "diagnose_stomach_pain",

  "original_request": {
    "fact_ids": ["F001", "F002"],
    "generated_text_hash": "sha256-xxx"
  },

  "bounce_type": "fact_mismatch",
  "bounce_description": "使用者按建议服药后症状未缓解，就医检查发现实际为急性阑尾炎",

  "fact_level_feedback": [
    {
      "fact_id": "F001",
      "issue": "事实过时",
      "detail": "2024年慢性胃炎记录未能反映2026年新增急性病症",
      "suggested_action": "元事实库需更新病历事实版本"
    },
    {
      "fact_id": "F002",
      "issue": "事实相关但非因果",
      "detail": "饮食记录与腹痛关联度被高估，掩盖了器质性病变"
    }
  ],

  "action_outcome": {
    "user_action": "按建议休息+服药",
    "actual_outcome": "症状加重，急诊手术",
    "cost": "延误治疗24小时"
  },

  "audit_trail": {
    "empty_model_extracted": "F001, F002",
    "llm_generated": "sha256-xxx",
    "arbitration_result": "passed",
    "human_audit": "pending"
  }
}
```

**字段说明：**

| 字段 | 说明 |
|------|------|
| `bounce_type` | 碰壁类型：`fact_mismatch` / `prediction_failed` / `external_validation_rejected` / `user_rejected` |
| `fact_level_feedback` | 哪条事实导致问题，建议如何修正 |
| `action_outcome` | 使用者按输出行动后的实际结果 |
| `audit_trail` | 完整追溯链，供人工审计 |

**判例库积累后触发：**
- 元事实库版本更新（人类确认）
- 裁决AI阈值τ调整（历史先验漂移）
- 空模型提取策略优化（同类错误预判拦截）

## 七、架构防火墙

### 7.1 核心原则

> **LLM不是"被限制"，是"无资格"。**

| 操作 | 空模型 | LLM | 说明 |
|------|--------|-----|------|
| 读取本地文件/传感器 | ✓ | ✗ | LLM无本地文件系统概念 |
| 查询元事实库 | ✓ | ✗ | LLM不知道元事实库存在 |
| 写入本地/执行命令 | ✓ | ✗ | LLM零写入、零执行权限 |
| 请求额外数据 | ✗ | ✗ | 单次请求-响应，LLM无请求资格 |
| 使用外部知识 | ✗ | ✗ | 空模型已筛选，LLM接收不到外部知识 |
| 修改执行计划 | ✓ | ✗ | LLM只返回文本，不返回可执行结构 |
| 返回外部链接 | ✗ | ✗ | 防止钓鱼/恶意链接 |
| 声称"我认为/我知道" | ✗ | ✗ | 协议层禁止，LLM只能"根据您的事实" |

### 7.2 防火墙的本质

```
旧思维（nmp-1.0）：
  LLM是危险的野兽 → 给它戴手铐 → 防止它作恶

新思维（nmp-2.0）：
  LLM没有自己的事实 → 它只活在空模型画的领地里 → 
  领地外的东西它看不到、想不到、做不到 → 无需手铐，因为无手
```

## 八、安全机制

1. **TLS 1.3**：所有通信加密
2. **请求签名**：空模型请求带 HMAC-SHA256 签名，防篡改
3. **响应校验**：LLM响应带校验和，防中间人
4. **超时回退**：LLM响应超时（默认30秒），空模型回退到默认值或拒绝服务
5. **速率限制**：防止LLM被滥用
6. **事实溯源**：每条事实可追溯到元事实库版本和确认者
7. **判例库隔离**：反馈数据本地存储，不上传云端，保护使用者隐私



## 九、版本演进

| 版本 | 特性 |
|------|------|
| nmp-1.0 | 基础事实+策略交换，防火墙式限制 |
| **nmp-2.0** | **事实主权+代表立场+闭环反馈+无资格原则** |
| nmp-2.1 | 支持多轮协商（LLM请求澄清特定事实，空模型响应查询） |
| nmp-3.0 | 支持跨使用者事实授权（企业授权员工访问特定事实子集） |


## 十、术语对照

| 术语 | 说明 |
|------|------|
| 空模型 | Empty Model，本地先验计算结构，无内容 |
| LLM | Full Model，云端/本地大语言模型，概率生成 |
| 元事实库 | Meta-Fact Vault，使用者确认的静态事实快照集合 |
| 判例库 | Case Law，错误碰壁记录，否定性知识 |
| 事实约束包 | Fact Constraint Package，空模型向LLM发送的事实+约束集合 |
| 立场响应 | Stance Response，LLM在事实约束下代表使用者生成的文本 |
| 碰壁反馈 | Bounce Feedback，事实层面的错误反馈，入判例库 |
| 无资格原则 | Disqualification Principle，LLM无资格越界，而非被限制 |

#

> **本协议的核心不是"限制LLM"，是"让LLM没有资格代表自己，只能资格代表使用者"。**
>
> **LLM不拥有事实，不拥有立场，不拥有判断。它只拥有：在主人画出的领地里，替主人说话的能力。**

#

---
