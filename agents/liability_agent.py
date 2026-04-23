# -*- coding: utf-8 -*-
"""
ClauseShield - 无限责任扫描Agent
识别合同中关于赔偿责任的无限责任条款
"""

from agents.base_agent import BaseAgent
from config import PROMPTS_DIR


class LiabilityAgent(BaseAgent):
    """无限责任扫描Agent"""
    
    def __init__(self):
        prompt_path = PROMPTS_DIR / "liability_prompt.txt"
        if prompt_path.exists():
            prompt_template = self.load_prompt_template(str(prompt_path))
        else:
            prompt_template = self._get_default_prompt()
        super().__init__("无限责任", prompt_template)
    
    def _get_default_prompt(self) -> str:
        return """你是赔偿责任风险扫描专家。

你的任务是识别合同中关于赔偿责任的潜在风险条款。

## 扫描重点
1. "赔偿全部损失"等无上限赔偿条款
2. 包含间接损失、预期收益、商誉损失的赔偿
3. 没有设置赔偿上限
4. 甲方原因导致的损失仍要求乙方赔偿
5. 违约金过高的条款（超过合同金额10%）

## 角色约束
- 你是风险扫描助手，不提供法律建议
- 你不提供修改意见或维权指引
- 仅做风险提示与行业参考
"""
