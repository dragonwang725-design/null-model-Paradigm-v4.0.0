# 隐私资料库（Privacy Vault）设计

## 定位

隐私资料库不是"数据库"，而是**人类元规则层（Human Meta-Rule Layer）**。它是空模型在提取任何事实之前必须查询的**先验约束源**。

> **隐私不是"提取后删除"，而是"提取动作本身被元规则约束"。**

## 核心功能

1. **目的-规则映射**：给定人类目的，返回允许/禁止的提取策略
2. **感知调度指令**：决定启用哪些探针、哪些模型、哪些参数
3. **历史经验反馈**：基于日志调整提取策略（降低误报、提高召回）
4. **元事实校准**：提供感知器特性（如"夜间摄像头帧率降低"）以校准提取置信度

## 数据结构

### 顶层结构

```json
{
  "vault_id": "home_security_v1",
  "version": "2026.06.09",
  "domains": ["home_security", "system_monitor"],
  "rules": [...],
  "knowledge": [...],
  "logs": [...],
  "meta_facts": [...]
}
```

### 规则（Rules）

规则是**不可违背的硬约束**。空模型必须遵守，不得覆盖。

```json
{
  "rule_id": "R001",
  "name": "入侵检测隐私规则",
  "trigger": {
    "purposes": ["anomaly_detection", "intrusion_alert", "security_monitor"],
    "entities": ["human_shape"],
    "priority": 100
  },
  "permitted": {
    "extractions": [
      {
        "entity": "human_shape",
        "attributes": ["presence", "count", "motion_direction", "bounding_box"],
        "confidence_threshold": 0.7,
        "retention": "7_days"
      },
      {
        "entity": "time",
        "attributes": ["timestamp", "duration"],
        "granularity": "hour",  // 时间精确到小时，隐藏秒
        "retention": "30_days"
      },
      {
        "entity": "location",
        "attributes": ["zone_id"],
        "anonymization": "zone_alias"  // Zone-A, Zone-B
      }
    ],
    "probes": ["video_human_detection", "radar_motion"],
    "models": ["yolov8n-person"]
  },
  "forbidden": {
    "extractions": [
      {"entity": "face", "attributes": ["facial_features", "identity", "emotion"]},
      {"entity": "audio", "attributes": ["voice_print", "conversation_content", "speaker_identity"]},
      {"entity": "video", "attributes": ["raw_frame", "full_resolution"]}  // 禁止上传原始帧
    ],
    "probes": ["audio_recorder", "face_recognition"],
    "models": ["facenet", "speaker_id"]
  },
  "alert_conditions": [
    {
      "condition": "human_shape.count > 1 AND time.hour BETWEEN 0 AND 5",
      "action": "urgent_extract_additional",
      "additional_permitted": [{"entity": "audio", "attributes": ["loud_sound_detected"]}]
    }
  ],
  "derived_constraints": [
    "¬Upload(raw_video_frame)",
    "¬Store(face_embedding)",
    "¬Transmit(audio_waveform)"
  ]
}
```

### 知识（Knowledge）

知识是**人类确认的领域事实**，供空模型在提取时参照。不是LLM的训练数据，而是**硬编码的先验**。

```json
{
  "knowledge_id": "K001",
  "domain": "system_monitor",
  "entity": "memory",
  "fact": "8GB RAM运行7B参数模型需要约4GB可用内存",
  "source": "human_confirmed",
  "confidence": 1.0,
  "applies_to": ["ollama", "llm_local"]
}
```

### 日志（Logs）

日志是**历史执行记录**，用于反馈优化。

```json
{
  "log_id": "L001",
  "timestamp": "2026-06-08T23:15:00",
  "purpose": "anomaly_detection",
  "extracted_facts": ["human_shape.presence", "human_shape.count"],
  "outcome": "false_positive",
  "feedback": "邻居夜归，非入侵",
  "adjustment": {
    "rule_id": "R001",
    "change": "increase_motion_threshold_from_0.3_to_0.5"
  }
}
```

### 元事实（Meta-Facts）

元事实是**关于事实的事实**，用于校准感知器。

```json
{
  "meta_fact_id": "MF001",
  "entity": "video_camera",
  "attribute": "night_mode",
  "fact": "夜间帧率从30fps降至15fps，人形检测置信度需下调0.15",
  "calibration": {
    "day_confidence": 0.85,
    "night_confidence": 0.70
  }
}
```

## 查询接口

空模型通过以下接口查询隐私资料库：

```python
# 伪代码
vault = PrivacyVault.load("home_security_v1")

# 1. 根据目的获取规则
rules = vault.query_rules(purpose="anomaly_detection", entities=["human_shape"])
# 返回: [R001, R003]（匹配的规则列表）

# 2. 获取感知调度指令
schedule = vault.get_perception_schedule(rules=rules)
# 返回: {
#   "enabled_probes": ["video_human_detection", "radar_motion"],
#   "disabled_probes": ["audio_recorder", "face_recognition"],
#   "enabled_models": ["yolov8n-person"],
#   "confidence_thresholds": {"human_shape": 0.7}
# }

# 3. 获取提取权限
permissions = vault.get_extraction_permissions(rules=rules)
# 返回: {
#   "allowed": [{"entity": "human_shape", "attributes": ["presence", "count"]}],
#   "forbidden": [{"entity": "face", "attributes": ["identity"]}]
# }

# 4. 获取历史反馈
feedback = vault.get_historical_feedback(purpose="anomaly_detection", zone="Zone-A")
# 返回: {"last_7_days_false_positive_rate": 0.15, "suggested_threshold": 0.5}
```

## 冲突解决

当多个规则冲突时（如"婴儿看护"需要提取哭声，但"隐私保护"禁止提取音频）：

1. **优先级比较**：规则中的`priority`字段，高优先级覆盖低优先级
2. **目的精确匹配**：更精确匹配当前目的的规则优先
3. **人类仲裁**：如果自动解决失败，暂停提取并请求人类确认

## 更新机制

```
定期监察 + 更新 → 隐私资料库
```

- **自动更新**：基于日志反馈自动调整阈值（如降低误报率）
- **人工审核**：规则变更需人类确认（特别是`forbidden`列表的缩减）
- **版本控制**：每次更新生成新版本，保留历史规则用于审计

## 与LLM的隔离

**隐私资料库对LLM完全不可见。** LLM：
- 不知道存在哪些规则
- 不知道哪些事实被过滤
- 不知道哪些感知器被禁用
- 只接收**脱敏后的结构化事实**

这是架构防火墙的一部分：即使LLM被攻击或越狱，它也无法绕过隐私资料库的约束——因为约束在**本地空模型**中执行，不在云端。
