# -*- coding: utf-8 -*-
"""
ClauseShield - Agent基类
封装DeepSeek API调用，提供统一的扫描接口
"""

import json
import os
from typing import List, Optional
from openai import AsyncOpenAI
import asyncio

import config
from config import RiskItem


class BaseAgent:
    """
    合同风险扫描Agent基类
    
    所有专项Agent应继承此类，实现特定领域的风险扫描
    """
    
    def __init__(self, category: str, prompt_template: str):
        """
        初始化Agent
        
        Args:
            category: 风险类别名称
            prompt_template: Prompt模板文本
        """
        self.category = category
        self.prompt_template = prompt_template
        self.client = AsyncOpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL,
            timeout=config.REQUEST_TIMEOUT
        )
    
    async def scan(self, contract_text: str, few_shot_examples: List[dict]) -> List[RiskItem]:
        """
        扫描合同文本，识别风险条款
        
        Args:
            contract_text: 合同全文
            few_shot_examples: Few-Shot示例列表
            
        Returns:
            风险项目列表
        """
        # 构建Prompt
        prompt = self._build_prompt(contract_text, few_shot_examples)
        
        # 调用API（带重试）
        for attempt in range(config.MAX_RETRIES + 1):
            try:
                response = await self.client.chat.completions.create(
                    model=config.DEFAULT_MODEL,
                    messages=[
                        {"role": "system", "content": "你是一个合同风险扫描助手，专门识别合同中的潜在风险条款。你不提供法律建议，仅做风险提示。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=config.TEMPERATURE,
                    max_tokens=config.MAX_TOKENS,
                    response_format={"type": "json_object"}
                )
                
                # 解析JSON响应
                result_text = response.choices[0].message.content
                result = json.loads(result_text)
                
                # 转换为RiskItem列表
                risk_items = self._parse_result(result, contract_text)
                return risk_items
                
            except Exception as e:
                if attempt < config.MAX_RETRIES:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"⚠️ {self.category}扫描失败（第{attempt + 1}次），{wait_time}秒后重试: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"❌ {self.category}扫描最终失败: {e}")
                    return []
        
        return []
    
    def _build_prompt(self, contract_text: str, few_shot_examples: List[dict]) -> str:
        """
        构建完整的Prompt
        
        Args:
            contract_text: 合同文本
            few_shot_examples: Few-Shot示例
            
        Returns:
            完整的Prompt文本
        """
        # 构建Few-Shot示例文本
        examples_text = ""
        for i, example in enumerate(few_shot_examples[:3], 1):  # 最多使用3个示例
            examples_text += f"""
示例 {i}:
- 风险类别: {example.get('category', '')}
- 风险等级: {example.get('risk_level', '')}
- 典型条款: {example.get('legal_jargon', '')}
- 风险说明: {example.get('plain_risk', '')}
- 行业常规: {example.get('common_practice', '')}
"""
        
        prompt = f"""{self.prompt_template}

## Few-Shot示例
{examples_text}

## 待扫描合同文本
```
{contract_text[:8000]}  # 限制长度避免超出token限制
```

## 输出要求
请以JSON格式输出扫描结果，格式如下：
{{
    "risks": [
        {{
            "clause_text": "风险条款原文（100字以内）",
            "risk_level": "高危/警告/提示",
            "confidence": 85,
            "category": "{self.category}",
            "description": "白话解释这个条款为什么有风险",
            "common_practice": "行业常规做法是什么",
            "suggestion": "建议关注点（非法律建议）"
        }}
    ]
}}

如果没有发现风险，请返回：{{"risks": []}}
"""
        return prompt
    
    def _parse_result(self, result: dict, contract_text: str) -> List[RiskItem]:
        """
        解析API返回结果
        
        Args:
            result: API返回的JSON对象
            contract_text: 原始合同文本
            
        Returns:
            RiskItem列表
        """
        risk_items = []
        
        risks = result.get("risks", [])
        if not isinstance(risks, list):
            return []
        
        for risk in risks:
            try:
                # 验证risk_level
                risk_level = risk.get("risk_level", "提示")
                if risk_level not in ["高危", "警告", "提示"]:
                    risk_level = "提示"
                
                # 验证confidence
                confidence = risk.get("confidence", 50)
                if not isinstance(confidence, int):
                    confidence = int(confidence) if isinstance(confidence, (int, float)) else 50
                confidence = max(0, min(100, confidence))  # 限制在0-100
                
                item = RiskItem(
                    clause_text=risk.get("clause_text", "")[:500],
                    risk_level=risk_level,
                    confidence=confidence,
                    category=risk.get("category", self.category),
                    description=risk.get("description", ""),
                    common_practice=risk.get("common_practice", ""),
                    suggestion=risk.get("suggestion", "")
                )
                risk_items.append(item)
            except Exception as e:
                print(f"⚠️ 解析风险项时出错: {e}")
                continue
        
        return risk_items
    
    def load_prompt_template(self, prompt_path: str) -> str:
        """
        从文件加载Prompt模板
        
        Args:
            prompt_path: Prompt文件路径
            
        Returns:
            Prompt模板文本
        """
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️ 加载Prompt模板失败: {e}")
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """获取默认Prompt模板"""
        return f"""你是{self.category}风险扫描专家。

你的任务是识别合同中与{self.category}相关的潜在风险条款。

## 角色约束
- 你是风险扫描助手，不提供法律建议
- 你不提供修改意见或维权指引
- 仅做风险提示与行业参考

## 扫描重点
识别合同中可能不利于乙方的条款，特别是：
1. 权利义务明显不平衡的条款
2. 使用模糊表述逃避责任的条款
3. 超出行业惯例的不合理要求
"""
