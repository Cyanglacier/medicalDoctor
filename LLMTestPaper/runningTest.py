import pandas as pd
import requests
import json
from time import sleep
from datetime import datetime

def read_questions(file_path):
    """读取CSV文件"""
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

def query_local_llm(question_text):
    """调用本地LLM模型"""
    url = "http://127.0.0.1:9991/v1/chat/completions"
    
    # 将system提示合并到user消息中
    messages = [
        {
            "role": "user", 
            "content": "你现在是一名中医医生。接下来你需要回答我提出的问题，您只需要回答A、B、C、D即可。\n\n" + question_text
        }
    ]
    
    data = {
        "messages": messages,
        "model": "local-model",
        "temperature": 0.3
    }
    
    try:
        response = requests.post(
            url, 
            json=data, 
            headers={"Content-Type": "application/json"}
        )
        response_data = response.json()
        
        if response.status_code != 200:
            print(f"API返回错误状态码: {response.status_code}")
            print(f"错误信息: {response_data}")
            return None
            
        return response_data['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error querying model: {e}")
        return None

def process_questions():
    # 读取CSV文件
    df = read_questions('tcm_exam_sample_500.csv') ##这里改成你想读的csv文件名称，必须在一个目录里
    if df is None:
        return
    
    # 创建结果列表
    results = []
    
    # 获取当前时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 遍历每个问题
    for index, row in df.iterrows():
        print(f"Processing question {index + 1}/{len(df)}")
        
        # 提取问题文本
        question_text = row['题目']
        correct_answer = row['答案']
        category = row['范围']
        
        # 获取模型回答
        model_answer = query_local_llm(question_text)
        
        # 记录结果
        result = {
            "question_number": index + 1,
            "category": category,
            "question": question_text,
            "correct_answer": correct_answer,
            "model_answer": model_answer,
            "is_correct": model_answer.strip().upper() == correct_answer.strip().upper() if model_answer else False
        }
        results.append(result)
        
        # 实时保存结果到JSON文件
        output_file = f'model_answers_{timestamp}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 同时保存为CSV格式
        output_csv = f'model_answers_{timestamp}.csv'
        results_df = pd.DataFrame(results)
        results_df.to_csv(output_csv, index=False, encoding='utf-8')
        
        # 添加短暂延迟
        sleep(0.5)
    
    # 计算正确率
    correct_count = sum(1 for r in results if r['is_correct'])
    accuracy = (correct_count / len(results)) * 100 if results else 0
    
    # 打印统计信息
    print("\n=== 统计信息 ===")
    print(f"总题数: {len(results)}")
    print(f"正确数: {correct_count}")
    print(f"正确率: {accuracy:.2f}%")
    
    return results

if __name__ == "__main__":
    print("开始处理题目...")
    results = process_questions()
    print("处理完成！")