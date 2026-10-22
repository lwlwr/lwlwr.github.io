# 李文睿 · 2027 届算法岗位个人主页

面向大模型后训练、基础模型组与 Agent 算法岗位的静态主页。

- [主页](https://lwlwr.github.io/)
- [GRPO：项目范围与复现方案](docs/grpo.md)
- [Agent：数据与评测工程](docs/agent.md)
- [TTS：诊断与导出验证](docs/tts.md)
- [RAG：工程范围与评测设计](docs/rag.md)
- [内容与证据原则](docs/evidence-policy.md)
- [可运行的 Countdown 表达式评测工具](tools/README.md)

## 本地检查

Python 3.10+，无第三方依赖。

```sh
python -m unittest discover -s tools -p 'test_*.py' -v
python tools/countdown_eval.py tools/examples/countdown.synthetic.jsonl
python -m http.server 8000
```

最后一条命令在浏览器打开 http://localhost:8000。无需构建，无外部字体、脚本或图片依赖。

工具和合成示例是 2026-10-23 新增的独立补充，**不是历史训练代码或模型实验结果**。当前仓库不含模型训练入口、checkpoint 或历史预测，不声称已复现历史 GRPO 成绩。实验方案是后续复现的验收要求，不代表实验已完成。

维护主页时同步修改内容更新时间；未公开或尚未完成的代码不能用空链接冒充。企业项目只展示职责及通用工程方法，不提交内部材料。
