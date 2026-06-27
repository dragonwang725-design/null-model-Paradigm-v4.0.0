#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NMP 事实约束助手 —— 修正版
核心逻辑：放开LLM创意与外部知识调用，仅校验输出与客观事实是否冲突
约束逻辑：允许任意发挥、调用全量知识，唯一红线：不得与给定客观事实相悖
UI：基于 Gradio
"""
import os
import re
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
import gradio as gr
from sentence_transformers import SentenceTransformer

# ========== 配置 ==========
DATA_ROOT = Path("./data")          # 知识库目录
TOP_K = 8                           # 检索事实数量
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
SIM_THRESHOLD = 0.15

# ========== 1. 向量检索模块（无改动，复用） ==========
class VectorRetriever:
    def __init__(self, folder_path: Path):
        self.folder_path = folder_path.resolve()
        self.model = None
        self.paragraphs = []
        self.embeddings = None
        
    def load_or_build(self):
        print(f"📂 加载知识库: {self.folder_path}")
        if self.model is None:
            self.model = SentenceTransformer(EMBEDDING_MODEL)
        
        all_paragraphs = []
        for file_path in self.folder_path.rglob('*'):
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
            except Exception as e:
                continue
            
            paras = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 20]
            all_paragraphs.extend(paras)
        
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

# ========== 新增：空模型后置冲突校验模块（核心新增逻辑） ==========
class NullModelChecker:
    """空模型校验器：比对LLM输出与客观事实，检测矛盾冲突"""
    def __init__(self, fact_list: List[str]):
        self.facts = fact_list
        self.embed_model = SentenceTransformer(EMBEDDING_MODEL)
        self.fact_embeds = self.embed_model.encode(fact_list, normalize_embeddings=True)
    
    def detect_conflict(self, llm_output: str) -> Tuple[bool, List[str]]:
        """
        检测回答是否与事实存在冲突
        返回：是否存在冲突、冲突事实列表
        """
        sentences = re.split(r"[。！？;；]", llm_output)
        conflict_points = []
        output_embeds = self.embed_model.encode(sentences, normalize_embeddings=True)
        
        # 高相似度判定为存在事实冲突
        conflict_threshold = 0.85
        for sent, sent_emb in zip(sentences, output_embeds):
            if len(sent.strip()) < 5:
                continue
            sims = np.dot(self.fact_embeds, sent_emb)
            for idx, sim in enumerate(sims):
                # 语义高度重合但语义相反，判定冲突（简化方案，工程可扩展）
                if sim > conflict_threshold and self._is_opposite(sent, self.facts[idx]):
                    conflict_points.append(f"冲突事实：{self.facts[idx]}，回答内容：{sent.strip()}")
        return len(conflict_points) > 0, conflict_points

    def _is_opposite(self, text_a: str, text_b: str) -> bool:
        """简易正反语义判断，可后续扩充关键词库"""
        opposite_words = {"大于":"小于","超过":"不足","支持":"禁止","可以":"不可","最大":"最小"}
        for k, v in opposite_words.items():
            if k in text_a and v in text_b or v in text_a and k in text_b:
                return True
        return False

# ========== 2. LLM 调用模块（无改动） ==========
def call_llm(prompt: str) -> str:
    """尝试调用本地 Ollama，如果不可用则返回模拟响应"""
    import requests
    try:
        payload = {
            "model": "qwen2.5:1.5b",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.7}  # 调高temperature，放开创意
        }
        response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            raise Exception("Ollama 服务异常")
    except Exception as e:
        print(f"⚠️ LLM 调用失败 ({e})，使用模拟模式")
        return "[模拟回复] 我可以结合行业知识自由拓展方案，所有内容均不会与给定客观事实冲突。"

# ========== 3. 核心处理逻辑（大幅修改Prompt + 新增空模型校验流程） ==========
def process_query(question: str, knowledge_dir: str) -> Tuple[str, str, str]:
    if not question:
        return "请输入问题", "", ""
    root = Path(knowledge_dir) if knowledge_dir else DATA_ROOT
    if not root.exists():
        return f"❌ 路径不存在: {root}", "", ""
    
    # 1. 检索相关客观事实
    retriever = VectorRetriever(root).load_or_build()
    facts = retriever.search(question)
    if not facts:
        return "⚠️ 未找到相关事实，无法约束LLM。", "", ""
    
    fact_text_list = [f["content"] for f in facts]
    fact_package = {
        "question": question,
        "retrieved_facts": facts,
        "total": len(facts)
    }
    fact_json = json.dumps(fact_package, indent=2, ensure_ascii=False)
    facts_text = "\n".join([f"- {f['content']}" for f in facts])

    # ========== 【关键修改】全新宽松Prompt，放开创意与外部知识 ==========
    prompt = f"""你可以自由调用自身全部行业知识、充分发散思考、拓展创意方案、多角度推演设计，完全不受思路限制。
仅遵守一条底层规则：你输出的所有推论、设想、方案、结论，**不能与下方客观事实产生矛盾、相悖**。

【客观确定事实】
{facts_text}
【用户问题/需求】
{question}

请完整输出你的思考、创意、方案，仅规避与上述事实冲突的内容即可。
"""
    # 调用LLM自由生成
    raw_answer = call_llm(prompt)

    # ========== 新增：空模型后置校验冲突 ==========
    checker = NullModelChecker(fact_text_list)
    has_conflict, conflict_list = checker.detect_conflict(raw_answer)
    if has_conflict:
        conflict_tip = "【空模型校验拦截：检测到内容与客观事实存在冲突】\n" + "\n".join(conflict_list)
        final_answer = conflict_tip + "\n\n原始回答：\n" + raw_answer
    else:
        final_answer = raw_answer

    return final_answer, fact_json, prompt

# ========== 4. Gradio UI（仅微调说明文案） ==========
with gr.Blocks(title="NMP 事实约束助手 V3", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🧠 NMP 事实约束助手
    ### 机制说明：放开LLM创意与外部知识，仅后置校验是否与客观事实冲突
    1. LLM可自由联想、调用行业知识、输出创新方案，不限制发挥
    2. 空模型自动校验输出内容，仅拦截和给定事实相悖的内容
    """)
    
    with gr.Row():
        with gr.Column(scale=4):
            question_input = gr.Textbox(
                label="💬 你的问题/需求", 
                placeholder="例如：基于这台机器硬件参数，设计一套巡检创新方案",
                lines=3
            )
            dir_input = gr.Textbox(
                label="📂 客观事实库路径", 
                value=str(DATA_ROOT),
                placeholder="留空则默认使用 ./data"
            )
            submit_btn = gr.Button("🚀 提交查询", variant="primary")
        
        with gr.Column(scale=6):
            answer_output = gr.Textbox(
                label="✅ LLM创意输出 + 空模型校验结果", 
                lines=8,
                interactive=False
            )
    
    with gr.Accordion("📦 查看提取的客观事实包 (JSON) 与生成Prompt", open=False):
        fact_json_output = gr.JSON(label="事实包数据")
        prompt_output = gr.Textbox(label="下发给LLM的宽松Prompt", lines=6, interactive=False)
    
    submit_btn.click(
        fn=process_query,
        inputs=[question_input, dir_input],
        outputs=[answer_output, fact_json_output, prompt_output]
    )
    
    gr.Markdown("""
    ---
    **⚙️ 运行要求**：
    1. 将客观事实文档（.txt/.md）放入 `./data` 文件夹。
    2. 安装依赖：`pip install gradio sentence-transformers numpy requests`
    3. 启动本地 Ollama 获得完整创意输出。
    """)

# ========== 5. 启动 ==========
if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
