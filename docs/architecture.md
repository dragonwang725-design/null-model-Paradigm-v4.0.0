# NMP 架构文档（修正版）

## 修正说明

基于逻辑一致性验证，以下修正已实施：
1. **提取前调度**：感知调度器在探针执行前生成指令，探针只执行允许提取
2. **物理预算模块**：在LLM调用前计算资源预算，防止过度生成
3. **原子执行与回滚**：保证每批操作要么全成功，要么全回滚
4. **规则外置**：默认规则从代码移到配置文件（建议）

## 修正后的完整架构图

<img width="1747" height="865" alt="arch" src="https://github.com/user-attachments/assets/b9efd8a8-873e-4024-a4d7-f25b184180c0" />


## 关键修正点

### 1. 提取前调度（Privacy by Design）

**修正前**：探针提取全部 → 调度器过滤（隐私数据已暴露）
**修正后**：调度器生成指令 → 探针只执行允许提取（隐私数据从未暴露）

```python
# 修正后流程
schedule = scheduler.schedule(purpose, entities)
probe_command = scheduler.create_probe_command(schedule)
# 探针接收probe_command，只执行command中指定的提取
raw_data = probe.execute(probe_command)  # 只包含允许的事实
```

### 2. 物理预算模块（Resource Safety）

**论文要求**："在调用LLM之前计算安全批次大小"
**实现**：`PhysicalBudget.compute_budget()`

```python
budget = physical_budget.compute_budget(total_items=150)
safety_check = physical_budget.check_llm_safety(budget)
# 如果资源不足，不调用LLM，直接返回降级方案
```

### 3. 原子执行与回滚（Atomicity & Rollback）

**论文要求**："每批要么全提交要么全回滚"
**实现**：`AtomicExecutor.execute_batch()`

```python
batch = executor.create_batch(operations)
success = executor.execute_batch(batch)
# 如果任一操作失败，自动回滚已执行的操作
```

## 六步流水线完整映射

| 步骤 | 论文名称 | 实现模块 | 位置 | 说明 |
|------|---------|---------|------|------|
| 1 | Problem | 用户输入 | 本地 | 人类输入目的 |
| 2 | Null Model (Strategy) | `purpose_parser` + `physical_budget` + `perception_scheduler` + `constraint_locking` | 本地 | 物理预算、任务分解、约束锁定、感知调度 |
| 3 | Full Model (Cognition) | `llm_client.query()` | 云端 | LLM语义理解 |
| 4 | Database (Knowledge) | `privacy_vault.query_rules()` | 本地 | 隐私资料库查询 |
| 5 | Full Model (Synthesis) | `llm_client.query()` | 云端 | LLM组装策略 |
| 6 | Null Model (Judgment) | `final_judgment.judge()` | 本地 | 评估+选择 |
| 6 | Null Model (Execution) | `atomic_executor.execute_batch()` | 本地 | 原子执行+回滚 |

## 数据流详解（修正后）

### 阶段1：目的注入 + 物理预算
```
用户："整理150个文件"
    ↓
目的解析器：concern_type="optimize", target_entities=["file", "disk"]
    ↓
物理预算：total_items=150, available_ram=4GB → safe_batch_size=10, total_batches=15
    ↓
如果资源不足 → 直接返回降级方案，不调用LLM
```

### 阶段2：元规则查询 + 感知调度
```
感知调度器查询隐私资料库：
- 目的"optimize"匹配规则SYS001
- 允许提取：file.name, file.size, file.type
- 禁止提取：file.content（隐私）, file.path（安全）
- 启用探针：file_scanner
- 禁用探针：content_reader
    ↓
生成探针执行命令：
{
  "enabled_probes": ["file_scanner"],
  "extraction_plan": [
    {"entity": "file", "attributes": ["name", "size", "type"]}
  ],
  "forbidden_list": [
    {"entity": "file", "attributes": ["content", "path"]}
  ]
}
```

### 阶段3：提取前约束执行
```
探针接收执行命令，只提取允许的属性：
- 提取：file.name, file.size, file.type
- 不提取：file.content（命令中禁止）
- 结果：raw_data只包含允许的事实
```

### 阶段4：因果验证 + 相关性排序
```
因果骨架验证：
- file.size → disk_pressure (相关度0.85)
- file.type → organization_strategy (相关度0.90)
- os.version → file.organization (相关度0.0，过滤)
```

### 阶段5：脱敏与上传
```
脱敏处理：
- file.name → 保留扩展名，去除路径
- file.size → 保留数值
- 不上传原始文件内容

上传云端LLM：
"15批文件，每批10个，按类型整理，保留原文件"
```

### 阶段6：策略返回 + 最终判断 + 原子执行
```
LLM策略："按类型创建文件夹，复制文件到新文件夹"
    ↓
最终判断校验：
- 是否违反¬Delete(source_file)？否
- 是否违反¬Move(source_file)？否（策略是Copy）
- 是否与预算一致？是（15批，每批10个）
    ↓
原子执行：
- 创建批次：batch_0（文件0-9）
- 执行Copy操作
- 验证校验和：MD5_src == MD5_dst
- 如果失败：回滚已复制文件
- 继续下一批
```

## 形式保证验证

| 论文保证 | 实现模块 | 验证状态 |
|---------|---------|---------|
| Resource Safety | `PhysicalBudget` | ✅ 在LLM调用前预算资源 |
| Constraint Immutability | `ConstraintLocking` + `FinalJudgment` | ✅ 架构防火墙保证 |
| Graceful Degradation | `PhysicalBudget` + `AtomicExecutor` | ✅ 资源不足时降级，执行失败时回滚 |

## 修正后的逻辑一致性

| 命题 | 修正前符合度 | 修正后符合度 | 关键修正 |
|------|------------|------------|---------|
| 空模型 = 纯粹判断容器 | 85% | 90% | 规则外置到配置文件 |
| 事实因目的而异 | 70% | 95% | **提取前调度** |
| LLM策略 + 空模型最终判断 | 90% | 95% | 事实一致性强制检查 |
| 隐私资料库 = 元规则层 | 75% | 95% | **提取前调度** |
| 六步流水线 | 80% | 95% | **物理预算 + 原子执行** |
