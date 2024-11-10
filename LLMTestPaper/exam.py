import pandas as pd

def normalize_answer(answer):
    """标准化答案格式"""
    if pd.isna(answer):
        return None
    
    # 转换为字符串并去除空格
    answer = str(answer).strip().upper()
    
    # 如果答案已经是单个字母，直接返回
    if answer in 'ABCDE':
        return answer
        
    # 处理带有选项说明的答案
    if '选项' in answer:
        answer = answer.split('选项')[-1].strip()
        if answer[0] in 'ABCDE':
            return answer[0]
            
    # 处理带冒号的答案
    if '：' in answer or ':' in answer:
        answer = answer.split('：')[0].split(':')[0]
    
    # 提取第一个出现的有效答案字母
    for char in answer:
        if char in 'ABCDE':
            return char
            
    return None

def regrade_answers(file_path):
    """重新评分已有的答案文件"""
    # 读取CSV文件
    df = pd.read_csv(file_path)
    
    # 标准化正确答案和模型答案
    df['correct_answer_normalized'] = df['correct_answer'].apply(normalize_answer)
    df['model_answer_normalized'] = df['model_answer'].apply(normalize_answer)
    
    # 重新评分，添加详细的比较信息
    def compare_answers(row):
        correct = row['correct_answer_normalized']
        model = row['model_answer_normalized']
        
        # 打印调试信息
        print(f"Question {row['question_number']}:")
        print(f"Original correct answer: {row['correct_answer']}")
        print(f"Original model answer: {row['model_answer']}")
        print(f"Normalized correct answer: {correct}")
        print(f"Normalized model answer: {model}")
        print(f"Match: {correct == model}\n")
        
        return correct == model if pd.notna(model) and pd.notna(correct) else False
    
    df['is_correct_new'] = df.apply(compare_answers, axis=1)
    
    # 保存结果
    new_file_path = file_path.rsplit('.', 1)[0] + '_regraded.csv'
    df.to_csv(new_file_path, index=False)
    
    # 计算统计信息
    total_questions = len(df)
    correct_answers = df['is_correct_new'].sum()
    accuracy = correct_answers / total_questions * 100
    
    print(f"\n评分统计:")
    print(f"总题数: {total_questions}")
    print(f"正确题数: {correct_answers}")
    print(f"正确率: {accuracy:.2f}%")
    print(f"结果已保存至: {new_file_path}")
    
    return df

if __name__ == "__main__":
    file_path = "model_answers_20241110_155314.csv"  # 替换为你的文件路径
    results_df = regrade_answers(file_path)
    
    # 输出错误的题目（可选）
    wrong_answers = results_df[~results_df['is_correct_new']]
    print("\n错误题目详情:")
    for _, row in wrong_answers.iterrows():
        print(f"\n题号 {row['question_number']}:")
        print(f"类别: {row['category']}")
        print(f"正确答案: {row['correct_answer']}")
        print(f"模型答案: {row['model_answer']}")