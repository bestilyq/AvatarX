import re

# 数字到汉字的逐换法映射
digit_to_chinese = {
    '0': '零', '1': '一', '2': '二', '3': '三', '4': '四',
    '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'
}

# 常见单位列表
default_units = [
    "元", "米", "厘米", "毫米", "千米", "英尺", "加仑", "升", "毫升", 
    "公斤", "瓦", "度", "秒", "分钟", "小时", "天", "月", "日", "种", "个", "人"
]

# 小数部分逐换
def convert_decimal_part(decimal_str):
    return ''.join(digit_to_chinese[d] for d in decimal_str)

# 阿拉伯数字转中文数字
def arabic_to_chinese(num_str, full_form=False):
    num_str = str(num_str)
    if full_form:  # 全部逐位读出
        return ''.join(digit_to_chinese[ch] for ch in num_str)
    else:  # 按位数处理
        result = []
        num_str = num_str[::-1]
        for i, digit in enumerate(num_str):
            chinese_digit = digit_to_chinese[digit]
            unit = ["", "十", "百", "千", "万", "亿"][i % 6] if i < 6 else ""
            if chinese_digit == '零':
                if not result or result[-1] != '零':
                    result.append(chinese_digit)
            else:
                result.append(chinese_digit + unit)
        return ''.join(result[::-1]).rstrip('零').replace('一十', '十')

# 特殊处理：负数、百分比、年份
def handle_special_cases(text):
    # 百分比处理
    text = re.sub(r'(\d+)\.?(\d*)%', lambda m: f"百分之{arabic_to_chinese(m.group(1), full_form=False)}点{convert_decimal_part(m.group(2))}" if m.group(2) else f"百分之{arabic_to_chinese(m.group(1), full_form=False)}", text)
    # 年前/年后处理
    text = re.sub(r'(\d+)(年前|年后)', lambda m: arabic_to_chinese(m.group(1), full_form=False) + m.group(2), text)
    # 年份处理
    text = re.sub(r'(\d{4})年', lambda m: arabic_to_chinese(m.group(1), full_form=True) + '年', text)
    # 负数处理
    text = re.sub(r'-(\d+)', lambda m: "负" + arabic_to_chinese(m.group(1), full_form=False), text)
    return text

# 带单位处理
def replace_with_units(match):
    num_part = match.group(1)
    unit_part = match.group(2)
    return arabic_to_chinese(num_part, full_form=False) + unit_part

# 纯数字处理（逐换法）
def handle_pure_numbers(match):
    return arabic_to_chinese(match.group(1), full_form=True)

# 删除重复单位
def remove_duplicate_units(text, units):
    for unit in units:
        text = re.sub(rf"({unit})\1", unit, text)
    return text

# 小数点转换成“点”
def convert_dot_to_point(text):
    return text.replace('.', '点')

# 替换单位间的斜杠为“每”
def convert_slash_to_per(text):
    return re.sub(r'(\w+)\s*/\s*(\w+)', r'\1每\2', text)

# 处理带小数点的阿拉伯数字，和百分比处理相同
def handle_decimal_numbers(text):
    # 处理小数部分
    text = re.sub(r'(\d+)\.(\d+)', lambda m: f"{arabic_to_chinese(m.group(1), full_form=False)}点{convert_decimal_part(m.group(2))}", text)
    return text

def convert_numbers_to_chinese(text, additional_units=None):
    if additional_units:
        # 将外部单位字符串转换成列表
        additional_units_list = [unit.strip() for unit in additional_units.split(",")]
        # 合并到默认单位列表
        units = list(set(default_units + additional_units_list))  # 防止重复单位
    else:
        units = default_units  # 如果没有额外的单位，恢复到默认单位列表

    text = handle_special_cases(text)
    text = handle_decimal_numbers(text)  # 新增：处理带小数点的阿拉伯数字
    units_pattern = r'(\d+)(?=(' + '|'.join(units) + r'))'
    text = re.sub(units_pattern, lambda m: replace_with_units(m), text)
    text = re.sub(r'(\d+)(?=\D|$)', handle_pure_numbers, text)
    text = remove_duplicate_units(text, units)
    text = convert_dot_to_point(text)
    text = convert_slash_to_per(text)
    return text

if __name__ == "__main__":
    text = convert_numbers_to_chinese("1000年后的3025年有50015人参加，增长率50.68%，而500年前只有1000人。还有500种服务，费用平均3000.6元/人。")
    print(text)