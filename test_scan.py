import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

# 加载环境变量
load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
MODEL = os.getenv("DEFAULT_MODEL", "deepseek-chat")

# 扫描Prompt模板
SCAN_PROMPT = """你是一位独立开发者合同风险扫描专家。你的任务是用大白话识别合同中的风险条款，不做法律建议，只做风险提示。

## 扫描规则
请按以下6个维度扫描合同文本：
1. IP归属（知识产权归属是否过于偏向甲方）
2. 付款节点（是否有验收后付款、无明确标准等陷阱）
3. 无限责任（赔偿是否有上限、是否排除间接损失）
4. 维护范围（是否终身免费维护、是否包含第三方更新）
5. 保密期限（是否永久保密、是否限制作品集展示）
6. 竞业限制（是否过于宽泛、是否有补偿、期限是否过长）

## 输出格式（JSON）
对每个发现的风险条款，输出：
{
  "risk_level": "高危/警告/提示",
  "confidence": 0-100的整数,
  "category": "风险类别",
  "description": "白话解释这个条款为什么有风险",
  "common_practice": "行业常规做法是什么",
  "suggestion": "建议关注点（不做法律建议，只提醒注意）"
}

## Few-Shot示例
{few_shot_examples}

## 当前合同文本
{contract_text}

请扫描上述合同，输出所有发现的风险项（JSON数组格式）。如果没有明显风险，输出空数组[]。
"""

def load_few_shot_examples():
    """加载Few-Shot示例库"""
    with open("data/few_shot_lib.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    examples = []
    for ex in data["examples"]:
        example = f"""
【类别】{ex['category']}
【风险等级】{ex['risk_level']}
【法律原文】{ex['legal_jargon']}
【白话风险】{ex['plain_risk']}
【行业常规】{ex['common_practice']}
【建议】{ex['suggestion']}
"""
        examples.append(example)
    
    return "\n---\n".join(examples)

def scan_contract(contract_path, few_shot_text):
    """扫描单个合同"""
    with open(contract_path, "r", encoding="utf-8") as f:
        contract_text = f.read()
    
    prompt = SCAN_PROMPT.replace("{few_shot_examples}", few_shot_text).replace("{contract_text}", contract_text)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "你是一位合同风险扫描助手，只用大白话解释风险，不做法律建议。输出必须是合法的JSON格式。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 4000,
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        
        content = result["choices"][0]["message"]["content"]
        
        # 尝试解析JSON
        try:
            risks = json.loads(content)
            if isinstance(risks, dict) and "risks" in risks:
                risks = risks["risks"]
            elif not isinstance(risks, list):
                risks = []
        except json.JSONDecodeError:
            risks = []
            content = content  # 保留原始文本
        
        return {
            "file": os.path.basename(contract_path),
            "success": True,
            "risks": risks,
            "raw_response": content,
            "tokens_used": result.get("usage", {}),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "file": os.path.basename(contract_path),
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def main():
    """主函数：扫描所有测试合同"""
    print("=" * 60)
    print("ClauseShield - Day 1 合同扫描测试")
    print(f"API: {BASE_URL}")
    print(f"模型: {MODEL}")
    print("=" * 60)
    
    # 加载Few-Shot示例
    few_shot_text = load_few_shot_examples()
    print(f"[OK] Loaded {len(few_shot_text.split('---'))} Few-Shot examples")
    
    # 测试合同列表
    contracts = [
        "data/test_contract_01_ip_trap.txt",
        "data/test_contract_02_payment_trap.txt",
        "data/test_contract_03_reasonable.txt",
        "data/test_contract_04_upwork_trap.txt",
        "data/test_contract_05_moderate.txt",
    ]
    
    results = []
    
    for contract_path in contracts:
        if not os.path.exists(contract_path):
            print(f"[FAIL] File not found: {contract_path}")
            continue
        
        print(f"\n[OK] Scanning: {os.path.basename(contract_path)}")
        result = scan_contract(contract_path, few_shot_text)
        results.append(result)
        
        if result["success"]:
            risks = result["risks"]
            if isinstance(risks, list):
                high = sum(1 for r in risks if isinstance(r, dict) and r.get("risk_level") == "高危")
                medium = sum(1 for r in risks if isinstance(r, dict) and r.get("risk_level") == "警告")
                low = sum(1 for r in risks if isinstance(r, dict) and r.get("risk_level") == "提示")
                print(f"  [OK] Scan complete - High:{high} Medium:{medium} Low:{low}")
            else:
                print(f"  [!] Return format abnormal")
        else:
            print(f"  [FAIL] Scan failed: {result.get('error', 'Unknown error')}")
    
    # 保存结果
    output = {
        "test_date": datetime.now().isoformat(),
        "model": MODEL,
        "total_contracts": len(results),
        "successful_scans": sum(1 for r in results if r["success"]),
        "results": results
    }
    
    output_path = "data/test_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'=' * 60}")
    print(f"[OK] Test complete! Results saved to: {output_path}")
    print(f"  Total: {len(results)} contracts")
    print(f"  Success: {sum(1 for r in results if r['success'])} contracts")
    print(f"  Failed: {sum(1 for r in results if not r['success'])} contracts")
    print("=" * 60)

if __name__ == "__main__":
    main()
