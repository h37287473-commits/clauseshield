# -*- coding: utf-8 -*-
"""
ClauseShield - 付款节点扫描Agent
识别合同中关于付款条件的不合理条款
"""

from agents.base_agent import BaseAgent
from config import PROMPTS_DIR


class PaymentAgent(BaseAgent):
    """付款节点扫描Agent"""
    
    def __init__(self):
        prompt_path = PROMPTS_DIR / "payment_prompt.txt"
        if prompt_path.exists():
            prompt_template = self.load_prompt_template(str(prompt_path))
        else:
            prompt_template = self._get_default_prompt()
        super().__init__("付款节点", prompt_template)
    
    def _get_default_prompt(self) -> str:
        return """你是付款节点风险扫描专家。

你的任务是识别合同中关于付款条件的不合理条款。

## 扫描重点
1. "验收合格后付款"等模糊付款条件
2. 缺少里程碑付款节点
3. 尾款比例过高（超过50%）
4. 验收期过长或未约定自动验收
5. 以"甲方满意"等主观标准作为付款条件

## 角色约束
- 你是风险扫描助手，不提供法律建议
- 你不提供修改意见或维权指引
- 仅做风险提示与行业参考
"""
