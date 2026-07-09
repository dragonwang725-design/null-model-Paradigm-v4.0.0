# llm-hallucination-constraint-shell
The real fix: not changing the test rules, but putting a hallucination-constraint shell  on your model.

A small plugin that effectively mitigates and eliminates the hallucinations and illusions of logical overthinking in large language models (LLM).

# 一个有效约束、压制 AI大模型（LLM ）幻觉、逻辑脑补发散的小插件
 ——  真正解决大模型幻觉与逻辑脑补：不是改考试规则，是给模型戴上**幻觉紧箍咒**  

#

**引用**：[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20964746.svg)](https://doi.org/10.5281/zenodo.20964746)

---


全世界都知道，大模型存在幻觉、逻辑脑补和发散的问题。  
但全世界也都没有找到这个根本性问题的真正根源。

OpenAI最新发表并被称为"开创性论文"的《Why Language Models Hallucinate》https://arxiv.org/abs/2509.04664

洋洋洒洒貌似精辟地分析了各种原因，并号称给出了解决方向，但这些分析，本质上仍然停留在"知其然"的层面，而没有真正回答"为什么会这样"的根本问题，也因此根本没有给出真正解决问题的具体办法——换个说法，给出的办法根本没有解决问题。

其实，这个根本原因，一句话就能说清楚：  
> **大模型是抛开事实讲逻辑、讲道理。**

抛开事实讲逻辑、讲道理，能不胡说八道吗？能不产生幻觉吗？能不进行逻辑脑补吗？判断，以事实为依据，这不是常识吗？

原因如此简单。

解决办法一样很简单：**那就给大模型事实**。

## 什么是 llm-hallucination-constraint-shell（幻觉紧箍咒）？

constraint shell 不是另一个大模型，不是替代品，不是补丁。

它是一个**外壳**（Shell）——专门用来提取事实的，套在LLM外面的一层约束系统：

LLM 仍然是那个神通广大的孙悟空。  
constraint shell 是唐僧的紧箍咒——**念的是"幻觉"，疼的是"胡说"，护的是"真经"。**

>什么是事实？
   >事实就是：一个相对确定的、静态的客观存在。
   如：个人身份信息：性别，出生年月，籍贯；完整的个人病历，企业的设备名称、规格，企业的操作规则，这是确定的事实。这些事实又是随时间可变的，必须随变化可随时更改。比如：病历新增的内容；企业更换设备；因业务变化修改规则。

因此我们首先要建立一个个人的、私域的、可隐私的文件夹，这是存放确定的、静态的事实库，又是可以随时因改变而修改的。

<img src="flow-chart/s001.png" alt="图片替代文字" width="75%">

##

以下方案，只提供思路，而非完善的可操作代码（虽然确实可以跑，也可以实际小场景应用）：

**方案一**

 [查看代码：](examples/crash_probe.py)
 
 1.安装的 Python 库

 2.打开命令提示符（CMD）或 PowerShell。切换到脚本所在的目录（例如放在 F:\ 盘）

 3.运行脚本：
 ```
bash

 pip install psutil
 pip install GPUtil
 cd /d F:\
 py -3.11 crash_probe.py
 ```

 4.根据提示输入软件名称（如 chrome.exe），回车即可。

 **旧范式 (全模型 LLM)**
- 用户说：“游戏一直崩溃”
- LLM列出了5个猜测（驱动程序、DX、过热、显存、系统文件）
- 用户反复尝试；始终找不到根本原因。
- **红色标签：诊断失败，零事实收集**

**新范式（NMP 三层架构）**

| 层  | 行动 | 输出 |
| :--- | :--- | :--- |
| **L1 人类** | 输入问题|“游戏一直崩溃” |
| **L2 空模型NMP** | 意图识别 | 启动 Probe-GPU + Probe-EventLog |
| **探针 A** | `nvidia-smi` | 显存容量 9785/10240 MiB（溢出 95.5%），温度 86°C，功耗超过 TDP |
| **探针 B** | 事件查看器 | `nvlddmkm` 驱动程序 TDR 超时，GPU 功耗限制超出|
| **L2 空模型NMP** | 事实打包 | 结构化摘要纯文本 |
| **L3 大模型LLM** | 基于事实的分析 | 根本原因 = 显存溢出 + 驱动程序 TDR 错误，建议升级到 552.44 版本。 |
| **L2 空模型NMP** | 验证 + 执行 | WHQL 检查 → 应用修复 → 验证稳定性 |

**架构数据流:** L1 → L2 → 探针 → L2 → L3 → L2 (完整闭环)

当你要排查某个软件安装疑难问题或软件崩溃时，运行这个探针，你就能获得该软件的运行状况和所在电脑的硬件环境，从而使LLM更准确地判断问题根源以及给出有针对性的建议，而不是泛泛而谈各种可能原因。

#
**方案二** 

[查看代码：](examples/nmp.py)
 
 1.安装依赖
 ```
 cmd
 pip install gradio sentence-transformers numpy requests
 ```
 2.保持 Ollama 后台运行，并拉取对应模型。再启动 python 脚本，即可真实生成内容。

 3.实验报告：

 - [元宝实验](examples/yuanbao.md)
 
 - [豆包实验](examples/doubao.md)
 
 - [实验报告](examples/Experiment_Report.md)

 #
**方案三** 

> **合并方案一方案二**，合成为**方案三**，这对代码写手不是难事，最好整成一键安装包可通用使用，欢迎提供各种版本。
思想已开源，技术简单的要死，看得懂的自己去白嫖，别指望我更新方案三，手痒的自己来提 PR！

 #

> ###  幻觉紧箍咒  —— 
##  llm-hallucination-constraint-shell 不是终极版，它是空模型范式TDA架构的最小Demo

llm-hallucination-constraint-shell不是异想天开凭空想象而来的，它是从哲学原理 → 理论模型 → 架构设计 → 工程实现方案 → 案例验证代码（demo）逻辑演绎而来的 —— 人工智能范式解决方案 **空模型范式TDA架构**

---
  
### 点击了解完整解决方案：

#

## [空模型范式(NMP):可靠AI系统 可执行的核心范式](README.md)

[—— Null Model Paradigm(NMP):Reliable AI Executable Core Paradigm](README.md)

<img src="flow-chart/nmp.png" alt="图片替代文字" width="75%">


---
