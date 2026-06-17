# 本地文档 AI 问答 (Mini-RAG)

把本地文档当知识库，向 AI 提问，AI **基于你的文档**作答并标注来源——这就是企业知识库 / 智能客服的核心（RAG，检索增强生成）。

## 两步链路
1. **检索**：纯 Python TF-IDF 算相关度，从文档里找出最相关的片段（无需向量数据库，零重型依赖）
2. **生成**：把片段作为上下文喂给大模型，得到有依据、可溯源的回答

## 运行
```bash
pip install requests
# 配置大模型 API（OpenAI 兼容，官方或国内中转皆可）
set LLM_API_KEY=你的key
set LLM_BASE_URL=https://api.xxx.com/v1
set LLM_MODEL=gpt-4o-mini
python rag.py
```
把你的 `.txt / .md` 文档丢进 `docs/` 即可。**没配 API key 也能跑**——会直接展示检索到的相关片段（演示检索部分）。

示例：问"病假工资怎么算？"→ 命中 `示例-公司请假制度.md`，答"按基本工资 80% 发放"。

## 技术点
- 文档分块、TF-IDF 向量化、余弦相似度检索（纯标准库手写）
- 大模型 API 调用、Prompt 约束"只根据资料回答 + 标来源"防幻觉

## 可扩展
换成向量嵌入（embedding）+ 向量库（FAISS/Chroma）提升检索精度、支持 PDF/Word、做成网页或微信问答机器人、多文档管理后台。
