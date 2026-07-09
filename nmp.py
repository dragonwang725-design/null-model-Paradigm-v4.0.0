#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Null Model Paradigm (NMP)

核心差异一句话：
    传统 AI: 你要干什么 → LLM 回答
    NMP:     你要干什么 → 你有什么 → LLM 回答

"你有什么" = 元事实库 (Meta-Fact Vault) + 判例库
LLM 只能在"你有什么"的边界内发挥。
校验层拥有最终否决权。
"""
import os
import re
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import gradio as gr
from sentence_transformers import SentenceTransformer

# ========== 配置 ==========
DATA_ROOT = Path("./data")          # 知识库目录
TOP_K = 8                           # 检索事实数量
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
SIM_THRESHOLD = 0.15

# ========== 元事实库加载器 ==========
class MetaFactVaultLoader:
    """加载 Meta-Fact Vault JSON 文件，提取可检索的事实文本"""

    @staticmethod
    def load_vault(vault_path: Path) -> Tuple[List[str], Dict]:
        """
        加载元事实库 JSON，返回 (事实文本列表, 完整vault数据)
        """
        with open(vault_path, 'r', encoding='utf-8') as f:
            vault = json.load(f)

        fact_texts = []

        # 提取 facts 中的 content 为可检索文本
        for fact in vault.get("facts", []):
            content = fact.get("content", {})
            entity = content.get("entity", "")
            attrs = content.get("attributes", {})

            # 将事实转换为自然语言描述
            attr_texts = [f"{k}={v}" for k, v in attrs.items()]
            fact_text = f"{entity}: {', '.join(attr_texts)}"
            fact_texts.append(fact_text)

        # 提取 constraints 中的规则为可检索文本
        for constraint in vault.get("constraints", []):
            content = constraint.get("content", {})
            name = content.get("name", "")
            trigger = content.get("trigger", {})
            permitted = content.get("permitted", [])
            forbidden = content.get("forbidden", [])

            rule_text = f"约束-{name}: 触发条件={trigger}, 允许={permitted}, 禁止={forbidden}"
            fact_texts.append(rule_text)

        return fact_texts, vault

    @staticmethod
    def load_text_files(folder_path: Path) -> List[str]:
        """兼容旧版：从 .txt/.md 文件加载"""
        all_paragraphs = []
        for file_path in folder_path.rglob('*'):
            if file_path.suffix.lower() not in ('.txt', '.md'):
                continue
            try:
                for encoding in ['utf-8', 'gbk', 'gb2312']:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except:
                        continue
                else:
                    continue
            except:
                continue

            paras = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 20]
            all_paragraphs.extend(paras)

        return all_paragraphs

# ========== 向量检索模块（支持 JSON Vault） ==========
class VectorRetriever:
    def __init__(self, source_path: Path):
        self.source_path = source_path.resolve()
        self.model = None
        self.paragraphs = []
        self.embeddings = None
        self.vault_data = None  # 存储完整 vault 数据

    def load_or_build(self):
        print(f"📂 加载知识库: {self.source_path}")
        if self.model is None:
            self.model = SentenceTransformer(EMBEDDING_MODEL)

        all_paragraphs = []

        # 判断是文件还是文件夹
        if self.source_path.is_file() and self.source_path.suffix == '.json':
            # 加载 JSON 元事实库
            fact_texts, self.vault_data = MetaFactVaultLoader.load_vault(self.source_path)
            all_paragraphs.extend(fact_texts)
            print(f"  ✅ 加载 JSON Vault: {len(fact_texts)} 条事实/约束")

        elif self.source_path.is_dir():
            # 加载文件夹中的 .txt/.md
            all_paragraphs = MetaFactVaultLoader.load_text_files(self.source_path)
            print(f"  ✅ 加载文本文件: {len(all_paragraphs)} 段")

        elif self.source_path.is_file():
            # 单个文本文件
            try:
                with open(self.source_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                all_paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 20]
            except:
                pass

        self.paragraphs = all_paragraphs
        if all_paragraphs:
            self.embeddings = self.model.encode(all_paragraphs, show_progress_bar=False)
        return self

    def search(self, question: str, top_k: int = TOP_K) -> List[Dict]:
        if not self.paragraphs or self.embeddings is None:
            return []
        q_embedding = self.model.encode([question])[0]
        similarities = np.dot(self.embeddings, q_embedding) / (np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(q_embedding) + 1e-8)
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score < SIM_THRESHOLD:
                break
            results.append({"content": self.paragraphs[idx], "score": round(score, 4)})
        return results

    def get_vault_summary(self) -> str:
        """获取元事实库摘要信息"""
        if self.vault_data:
            vault_id = self.vault_data.get("vault_id", "unknown")
            owner = self.vault_data.get("owner", "unknown")
            purposes = self.vault_data.get("purposes", [])
            fact_count = len(self.vault_data.get("facts", []))
            constraint_count = len(self.vault_data.get("constraints", []))
            return f"Vault: {vault_id} | Owner: {owner} | Purposes: {purposes} | Facts: {fact_count} | Constraints: {constraint_count}"
        return "文本模式（无Vault结构）"

# ========== 空模型后置冲突校验模块 ==========
class NullModelChecker:
    """空模型校验器：比对LLM输出与客观事实，检测矛盾冲突"""
    def __init__(self, fact_list: List[str]):
        self.facts = fact_list
        self.embed_model = SentenceTransformer(EMBEDDING_MODEL)
        self.fact_embeds = self.embed_model.encode(fact_list, normalize_embeddings=True)

    def detect_conflict(self, llm_output: str) -> Tuple[bool, List[str]]:
        sentences = re.split(r"[。！？;；]", llm_output)
        conflict_points = []
        output_embeds = self.embed_model.encode(sentences, normalize_embeddings=True)

        conflict_threshold = 0.85
        for sent, sent_emb in zip(sentences, output_embeds):
            if len(sent.strip()) < 5:
                continue
            sims = np.dot(self.fact_embeds, sent_emb)
            for idx, sim in enumerate(sims):
                if sim > conflict_threshold and self._is_opposite(sent, self.facts[idx]):
                    conflict_points.append(f"冲突事实：{self.facts[idx]}，回答内容：{sent.strip()}")
        return len(conflict_points) > 0, conflict_points

    def _is_opposite(self, text_a: str, text_b: str) -> bool:
        opposite_words = {"大于":"小于","超过":"不足","支持":"禁止","可以":"不可","最大":"最小","耐高温":"不耐高温"}
        for k, v in opposite_words.items():
            if k in text_a and v in text_b or v in text_a and k in text_b:
                return True
        return False

# ========== LLM 调用模块 ==========
def call_llm(prompt: str) -> str:
    """尝试调用本地 Ollama，如果不可用则返回模拟响应"""
    import requests
    try:
        payload = {
            "model": "qwen2.5:1.5b",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.7}
        }
        response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            raise Exception("Ollama 服务异常")
    except Exception as e:
        print(f"⚠️ LLM 调用失败 ({e})，使用模拟模式")
        return "[模拟回复] 这是LLM自由发挥的内容，未经过事实校验。"

# ========== 【传统模式】你要干什么 → LLM 回答 ==========
def process_traditional(question: str, knowledge_dir: str) -> Tuple[str, str]:
    """
    传统 AI 流程：你要干什么 → LLM 直接回答
    """
    if not question:
        return "请输入问题", ""

    prompt = f"""【用户问题】
{question}

请直接回答，自由发挥，不受任何事实约束。"""

    answer = call_llm(prompt)

    info = """【传统模式】
✅ LLM 自由发挥
❌ 无事实约束
❌ 无校验拦截
❌ 不可解释"""

    return answer, info

# ========== 【NMP模式】你要干什么 → 你有什么 → LLM 回答 ==========
def process_nmp(question: str, knowledge_dir: str) -> Tuple[str, str, str, str]:
    """
    NMP 核心流程：
    传统 AI:  你要干什么 → LLM 直接回答（可能胡说）
    NMP:      你要干什么 → 【你有什么】事实库检索 → LLM 在事实边界内回答 → 【你有没有胡说】校验层确认 → 放行/拦截
    """
    if not question:
        return "请输入问题", "", "", ""

    root = Path(knowledge_dir) if knowledge_dir else DATA_ROOT
    if not root.exists():
        return f"❌ 路径不存在: {root}", "", "", ""

    # ========== 【第一步：你有什么】检索相关客观事实 ==========
    retriever = VectorRetriever(root).load_or_build()
    facts = retriever.search(question)

    if not facts:
        return "⚠️ 未找到相关事实，无法约束 LLM。", "", "", ""

    fact_text_list = [f["content"] for f in facts]
    fact_package = {
        "question": question,
        "retrieved_facts": facts,
        "vault_summary": retriever.get_vault_summary(),
        "total": len(facts)
    }
    fact_json = json.dumps(fact_package, indent=2, ensure_ascii=False)
    facts_text = "\n".join([f"- {f['content']}" for f in facts])

    # ========== 【第二步：LLM 在事实边界内回答】 ==========
    prompt = f"""你可以自由调用自身全部行业知识、充分发散思考、拓展创意方案。
仅遵守一条底层规则：你输出的所有推论、设想、方案、结论，**不能与下方客观事实产生矛盾**。

【客观确定事实——你有什么】
{facts_text}
【用户问题——你要干什么】
{question}

请完整输出你的思考、创意、方案，仅规避与上述事实冲突的内容即可。"""

    raw_answer = call_llm(prompt)

    # ========== 【第三步：你有没有胡说】空模型后置校验 ==========
    checker = NullModelChecker(fact_text_list)
    has_conflict, conflict_list = checker.detect_conflict(raw_answer)

    if has_conflict:
        conflict_tip = "【🚫 空模型校验拦截】检测到内容与客观事实存在冲突\n" + "\n".join(conflict_list)
        final_answer = conflict_tip + "\n\n原始回答：\n" + raw_answer
        status = "❌ 已拦截"
    else:
        final_answer = raw_answer
        status = "✅ 已通过校验"

    info = f"""【NMP模式】
✅ 事实库约束（{len(facts)}条相关事实）
✅ 校验层拦截
✅ 100%可解释
{status}
{retriever.get_vault_summary()}"""

    return final_answer, info, fact_json, prompt

# ========== Gradio UI（双按钮对比版） ==========
with gr.Blocks(title="Null Model Paradigm: 传统模式 vs NMP模式", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🧠 Null Model Paradigm (NMP)

    ### 核心差异
    **传统 AI：** 你要干什么 → LLM 回答（可能胡说）

    **NMP：** 你要干什么 → **你有什么** → LLM 回答（在事实边界内）

    ---
    """)

    with gr.Row():
        with gr.Column(scale=1):
            question_input = gr.Textbox(
                label="💬 你的问题/需求", 
                placeholder="例如：给刚做完手术的病人倒杯水",
                lines=3
            )
            dir_input = gr.Textbox(
                label="📂 客观事实库路径", 
                value=str(DATA_ROOT),
                placeholder="支持：文件夹 / .txt / .md / .json (Meta-Fact Vault)"
            )

            with gr.Row():
                traditional_btn = gr.Button("🔴 传统模式", variant="secondary")
                nmp_btn = gr.Button("🟢 NMP模式", variant="primary")

        with gr.Column(scale=2):
            with gr.Tab("输出对比"):
                with gr.Row():
                    with gr.Column():
                        traditional_output = gr.Textbox(
                            label="🔴 传统模式输出（无约束）", 
                            lines=8,
                            interactive=False
                        )
                        traditional_info = gr.Textbox(
                            label="状态",
                            lines=4,
                            interactive=False
                        )

                    with gr.Column():
                        nmp_output = gr.Textbox(
                            label="🟢 NMP模式输出（事实约束）", 
                            lines=8,
                            interactive=False
                        )
                        nmp_info = gr.Textbox(
                            label="状态",
                            lines=4,
                            interactive=False
                        )

            with gr.Tab("调试信息"):
                fact_json_output = gr.JSON(label="📦 提取的事实包")
                prompt_output = gr.Textbox(label="📝 下发给LLM的Prompt", lines=6, interactive=False)

    gr.Markdown("""
    ---
    **⚙️ 运行要求**：
    1. 将客观事实文档放入 `./data` 文件夹
       - 文本模式：.txt / .md 文件
       - 元事实库模式：.json (Meta-Fact Vault 格式)
    2. 安装依赖：`pip install -r requirements.txt`
    3. 启动本地 Ollama 获得完整创意输出（或使用模拟模式）

    **📖 了解更多**：[NMP架构详解](docs/nmp.png)
    """)

    # 按钮绑定
    traditional_btn.click(
        fn=process_traditional,
        inputs=[question_input, dir_input],
        outputs=[traditional_output, traditional_info]
    )

    nmp_btn.click(
        fn=process_nmp,
        inputs=[question_input, dir_input],
        outputs=[nmp_output, nmp_info, fact_json_output, prompt_output]
    )

# ========== 启动 ==========
if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
