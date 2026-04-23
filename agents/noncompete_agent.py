# -*- coding: utf-8 -*-
"""
ClauseShield - 竞业限制扫描Agent
识别合同中关于竞业限制的不合理条款
"""

from agents.base_agent import BaseAgent
from config import PROMPTS_DIR


class NonCompeteAgent(BaseAgent):
    """竞业限制扫描Agent"""
    
    def __init__(self):
        prompt_path = PROMPTS_DIR / "noncompete_prompt.txt"
        if prompt_path.exists():
            prompt_template = self.load_prompt_template(str(prompt_path))
        else:
            prompt_template = self._get_default_prompt()
        super().__init__("竞业限制", prompt_template)
    
    def _get_default_prompt(self) -> str:
        return """你是竞业限制风险扫描专家。

你的任务是识别合同中关于竞业限制的不合理条款。

## 扫描重点
1. 竞业限制期限超过6个月
2. 限制范围过于宽泛（如限制整个技术栈）
3. 未约定经济补偿金
4. 限制为"同类业务"而非"直接竞争"
5. 合同结束后仍要求承担竞业限制义务

## 角色约束
- 你是风险扫描助手，不提供法律建议
- 你不提供修改意见或维权指引
- 仅做风险提示与行业参考
"""
