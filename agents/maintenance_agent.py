# -*- coding: utf-8 -*-
"""
ClauseShield - 维护范围扫描Agent
识别合同中关于维护义务的不合理条款
"""

from agents.base_agent import BaseAgent
from config import PROMPTS_DIR


class MaintenanceAgent(BaseAgent):
    """维护范围扫描Agent"""
    
    def __init__(self):
        prompt_path = PROMPTS_DIR / "maintenance_prompt.txt"
        if prompt_path.exists():
            prompt_template = self.load_prompt_template(str(prompt_path))
        else:
            prompt_template = self._get_default_prompt()
        super().__init__("维护范围", prompt_template)
    
    def _get_default_prompt(self) -> str:
        return """你是维护范围风险扫描专家。

你的任务是识别合同中关于维护义务的不合理条款。

## 扫描重点
1. "终身免费维护"等无期限维护承诺
2. 包含第三方库更新导致的兼容性问题
3. 维护范围不明确，包含新功能开发
4. 维护响应时间要求过高（如2小时内）
5. 甲方自行修改导致的问题要求免费修复

## 角色约束
- 你是风险扫描助手，不提供法律建议
- 你不提供修改意见或维权指引
- 仅做风险提示与行业参考
"""
