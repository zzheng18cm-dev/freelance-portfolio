"""
本地文档 AI 问答 (Mini-RAG)
---------------------------
把 docs/ 目录下的 .txt / .md 文档作为知识库，对用户提问：
  1) 检索：纯 Python TF-IDF 找出最相关的文档片段（无需任何向量库/重型依赖）
  2) 生成：把相关片段作为上下文，调用大模型 API 给出有依据的回答

演示了 RAG（检索增强生成）的完整链路。检索部分纯标准库即可跑；
配置大模型 API 后即可生成答案（兼容 OpenAI 格式的接口，国内中转/官方均可）。

依赖: requests   ->  pip install requests
配置(环境变量):
    set LLM_API_KEY=你的key
    set LLM_BASE_URL=https://api.xxx.com/v1   (默认 OpenAI 兼容)
    set LLM_MODEL=gpt-4o-mini                 (或任意可用模型)
运行: python rag.py
"""

import os
import re
import math
import glob
from collections import Counter

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
TOP_K = 3            # 取最相关的前 K 个片段
CHUNK_SIZE = 300     # 每个片段约多少字


def load_chunks():
    """读取 docs 下所有文档，切成片段。"""
    chunks = []
    for path in glob.glob(os.path.join(DOCS_DIR, "*.txt")) + glob.glob(os.path.join(DOCS_DIR, "*.md")):
        text = open(path, encoding="utf-8").read()
        # 按段落聚合到约 CHUNK_SIZE 字
        buf = ""
        for para in re.split(r"\n\s*\n", text):
            para = para.strip()
            if not para:
                continue
            if len(buf) + len(para) > CHUNK_SIZE and buf:
                chunks.append((os.path.basename(path), buf))
                buf = para
            else:
                buf = (buf + "\n" + para).strip()
        if buf:
            chunks.append((os.path.basename(path), buf))
    return chunks


def tokenize(s):
    # 中文按字、英文按词，简单有效
    return re.findall(r"[a-zA-Z]+|[一-鿿]", s.lower())


def build_tfidf(chunks):
    docs_tokens = [tokenize(c[1]) for c in chunks]
    df = Counter()
    for toks in docs_tokens:
        for t in set(toks):
            df[t] += 1
    n = len(chunks)
    idf = {t: math.log((n + 1) / (df[t] + 1)) + 1 for t in df}
    vectors = []
    for toks in docs_tokens:
        tf = Counter(toks)
        vec = {t: (tf[t] / len(toks)) * idf.get(t, 0) for t in tf}
        vectors.append(vec)
    return vectors, idf


def cosine(a, b):
    dot = sum(a.get(t, 0) * b.get(t, 0) for t in set(a) | set(b))
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0


def retrieve(query, chunks, vectors, idf):
    q_toks = tokenize(query)
    tf = Counter(q_toks)
    q_vec = {t: (tf[t] / max(len(q_toks), 1)) * idf.get(t, 0) for t in tf}
    scored = sorted(
        ((cosine(q_vec, vectors[i]), chunks[i]) for i in range(len(chunks))),
        key=lambda x: x[0], reverse=True,
    )
    return [c for s, c in scored[:TOP_K] if s > 0]


def answer_with_llm(query, contexts):
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        return None  # 没配 key，只返回检索结果
    import requests
    base = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    ctx = "\n\n".join(f"[来源:{src}]\n{txt}" for src, txt in contexts)
    prompt = (f"只根据下面的资料回答问题，资料里没有就说不知道，并标出来源文件。\n\n"
              f"资料:\n{ctx}\n\n问题: {query}")
    resp = requests.post(
        f"{base}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.2},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def main():
    chunks = load_chunks()
    if not chunks:
        print(f"docs 目录下没有文档，请把 .txt/.md 放进 {DOCS_DIR}")
        return
    vectors, idf = build_tfidf(chunks)
    print(f"已加载 {len(chunks)} 个文档片段。输入问题（回车退出）：")
    while True:
        q = input("\n你问: ").strip()
        if not q:
            break
        hits = retrieve(q, chunks, vectors, idf)
        if not hits:
            print("知识库里没找到相关内容。")
            continue
        ans = answer_with_llm(q, hits)
        if ans:
            print("\nAI 答:", ans)
        else:
            print("\n[未配置大模型API，先展示检索到的相关片段]")
            for src, txt in hits:
                print(f"\n--- 来源 {src} ---\n{txt[:200]}")


if __name__ == "__main__":
    main()
