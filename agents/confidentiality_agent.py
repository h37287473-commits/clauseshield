# -*- coding: utf-8 -*-
"""
ClauseShield - 保密期限扫描Agent
识别合同中关于保密义务的不合理条款
"""

from agents.base_agent import BaseAgent
from config import PROMPTS_DIR


class ConfidentialityAgent(BaseAgent):
    """保密期限扫描Agent"""
    
    def __init__(self):
        prompt_path = PROMPTS_DIR / "confidentiality_prompt.txt"
        if prompt_path.exists():
            prompt_template = self.load_prompt_template(str(prompt_path))
        else:
            prompt_template = self._get_default_prompt()
        super().__init__("保密期限", prompt_template)
    
    def _get_default_prompt(self) -> str:
        return """你是保密期限风险扫描专家。

你的任务是识别合同中关于保密义务的不合理条款。

## 扫描重点
1. "永久保密"等无期限保密义务
2. 禁止在任何情况下提及项目经验
3. 保密期限超过3年
4. 保密范围过于宽泛（包含公开信息）
5. 违反保密义务的违约金过高

## 角色约束
- 你是风险扫描助手，不提供法律建议
- 你不提供修改意见或维权指引
- 仅做风险提示与行业参考
"""
