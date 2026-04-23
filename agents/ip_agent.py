# -*- coding: utf-8 -*-
"""
ClauseShield - IP归属扫描Agent
识别合同中关于知识产权归属的不公平条款
"""

from agents.base_agent import BaseAgent
from config import PROMPTS_DIR


class IPAgent(BaseAgent):
    """IP归属扫描Agent"""
    
    def __init__(self):
        prompt_path = PROMPTS_DIR / "ip_prompt.txt"
        if prompt_path.exists():
            prompt_template = self.load_prompt_template(str(prompt_path))
        else:
            prompt_template = self._get_default_prompt()
        super().__init__("IP归属", prompt_template)
    
    def _get_default_prompt(self) -> str:
        return """你是IP归属风险扫描专家。

你的任务是识别合同中关于知识产权归属的潜在风险条款。

## 扫描重点
1. "全部知识产权归甲方"等完全转让条款
2. Work for Hire（雇佣作品）条款
3. 剥夺署名权的条款
4. 禁止在作品集展示的条款
5. 开源组件归属权被剥夺的条款

## 角色约束
- 你是风险扫描助手，不提供法律建议
- 你不提供修改意见或维权指引
- 仅做风险提示与行业参考
"""
