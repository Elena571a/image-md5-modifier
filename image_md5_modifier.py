"""
图片MD5修改工具 - 用于生成多个不同MD5的图片版本
通过多种方式轻微修改图片，确保每个版本的MD5都不同
"""

import os
import hashlib
import random
import argparse
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np


def calculate_md5(file_path):
    """计算文件的MD5值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def modify_image_method1(image, seed):
    """方法1: 添加微小的随机噪声"""
    random.seed(seed)
    np.random.seed(seed % (2**32))  # numpy的seed需要是32位整数
    img_array = np.array(image)
    noise = np.random.randint(-3, 4, img_array.shape, dtype=np.int16)
    img_array = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(img_array)


def modify_image_method2(image, seed):
    """方法2: 轻微调整亮度"""
    random.seed(seed)
    enhancer = ImageEnhance.Brightness(image)
    factor = 1.0 + random.uniform(-0.02, 0.02)  # 轻微的亮度调整
    return enhancer.enhance(factor)


def modify_image_method3(image, seed):
    """方法3: 轻微调整对比度"""
    random.seed(seed)
    enhancer = ImageEnhance.Contrast(image)
    factor = 1.0 + random.uniform(-0.02, 0.02)
    return enhancer.enhance(factor)


def modify_image_method4(image, seed):
    """方法4: 轻微调整饱和度"""
    random.seed(seed)
    enhancer = ImageEnhance.Color(image)
    factor = 1.0 + random.uniform(-0.02, 0.02)
    return enhancer.enhance(factor)


def modify_image_method5(image, seed):
    """方法5: 添加极小的模糊然后锐化"""
    random.seed(seed)
    blurred = image.filter(ImageFilter.GaussianBlur(radius=0.1))
    return blurred.filter(ImageFilter.SHARPEN)


def modify_image_method6(image, seed):
    """方法6: 轻微调整锐度"""
    random.seed(seed)
    enhancer = ImageEnhance.Sharpness(image)
    factor = 1.0 + random.uniform(-0.02, 0.02)
    return enhancer.enhance(factor)


def modify_image_method7(image, seed):
    """方法7: 轻微旋转（小于0.2度）然后裁剪回原尺寸"""
    random.seed(seed)
    angle = random.uniform(-0.1, 0.1)
    rotated = image.rotate(angle, expand=False, fillcolor='white')
    return rotated


def modify_image_method8(image, seed):
    """方法8: 组合多种轻微调整"""
    random.seed(seed)
    # 轻微调整大小然后缩放回来
    scale = 1.0 + random.uniform(-0.001, 0.001)
    new_width = int(image.width * scale)
    new_height = int(image.height * scale)
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    final = resized.resize((image.width, image.height), Image.Resampling.LANCZOS)
    # 再添加轻微亮度调整
    enhancer = ImageEnhance.Brightness(final)
    return enhancer.enhance(1.0 + random.uniform(-0.005, 0.005))


# 所有修改方法的列表
MODIFICATION_METHODS = [
    modify_image_method1,
    modify_image_method2,
    modify_image_method3,
    modify_image_method4,
    modify_image_method5,
    modify_image_method6,
    modify_image_method7,
    modify_image_method8,
]


def process_image(input_path, output_dir=None, num_versions=3):
    """
    处理图片，生成多个不同MD5的版本
    
    Args:
        input_path: 输入图片路径
        output_dir: 输出目录，如果为None则使用输入文件所在目录
        num_versions: 要生成的版本数量（默认3个）
    """
    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        print(f"错误: 文件不存在 - {input_path}")
        return
    
    # 创建输出目录
    if output_dir is None:
        output_dir = os.path.dirname(input_path) or "."
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取原始图片
    try:
        original_image = Image.open(input_path)
        # 转换为RGB模式（确保兼容性）
        if original_image.mode != 'RGB':
            original_image = original_image.convert('RGB')
    except Exception as e:
        print(f"错误: 无法打开图片 - {e}")
        return
    
    # 获取原始文件名（不含扩展名）
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    file_ext = os.path.splitext(input_path)[1] or '.jpg'
    
    # 计算原始图片的MD5
    original_md5 = calculate_md5(input_path)
    print(f"原始图片MD5: {original_md5}")
    print(f"开始生成 {num_versions} 个不同版本...\n")
    
    # 生成多个版本
    generated_md5s = set([original_md5])
    version_count = 0
    
    for i in range(num_versions):
        # 使用随机种子
        seed = random.randint(1, 999999)
        
        # 随机选择2-4种方法组合使用，增强效果
        num_methods = random.randint(2, 4)
        selected_methods = random.sample(MODIFICATION_METHODS, min(num_methods, len(MODIFICATION_METHODS)))
        
        max_retries = 10  # 最多重试10次
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            try:
                # 组合应用多种修改方法
                modified_image = original_image.copy()
                current_seed = seed + retry_count * 1000
                
                for method_idx, method in enumerate(selected_methods):
                    method_seed = current_seed + method_idx * 100
                    modified_image = method(modified_image, method_seed)
                
                # 确保是RGB模式
                if modified_image.mode != 'RGB':
                    modified_image = modified_image.convert('RGB')
                
                # 生成输出文件名
                output_filename = f"{base_name}_v{i+1:02d}{file_ext}"
                output_path = os.path.join(output_dir, output_filename)
                
                # 保存图片（使用不同的质量参数确保MD5不同）
                quality = 95 + (i % 5) + (retry_count % 3)  # 质量在95-102之间变化
                if file_ext.lower() in ['.jpg', '.jpeg']:
                    modified_image.save(output_path, 'JPEG', quality=quality, optimize=True)
                elif file_ext.lower() == '.png':
                    modified_image.save(output_path, 'PNG', optimize=True)
                else:
                    modified_image.save(output_path)
                
                # 计算新文件的MD5
                new_md5 = calculate_md5(output_path)
                
                # 检查MD5是否唯一
                if new_md5 in generated_md5s:
                    retry_count += 1
                    if retry_count < max_retries:
                        # 如果重复，使用新的随机种子和更强的修改方法组合
                        seed = random.randint(1, 999999)
                        # 使用更多方法组合（3-5种）
                        num_retry_methods = random.randint(3, 5)
                        retry_methods = random.sample(MODIFICATION_METHODS, min(num_retry_methods, len(MODIFICATION_METHODS)))
                        
                        modified_image = original_image.copy()
                        for method_idx, method in enumerate(retry_methods):
                            method_seed = seed + method_idx * 100 + retry_count * 1000
                            modified_image = method(modified_image, method_seed)
                        
                        if modified_image.mode != 'RGB':
                            modified_image = modified_image.convert('RGB')
                        continue
                    else:
                        print(f"警告: 版本 {i+1} 经过 {max_retries} 次尝试后仍可能重复MD5")
                
                # MD5唯一，成功
                generated_md5s.add(new_md5)
                version_count += 1
                success = True
                
                file_size = os.path.getsize(output_path) / 1024  # KB
                if retry_count > 0:
                    print(f"✓ 版本 {i+1:2d}: {output_filename} (重试 {retry_count} 次)")
                else:
                    print(f"✓ 版本 {i+1:2d}: {output_filename}")
                print(f"  MD5: {new_md5}")
                print(f"  大小: {file_size:.2f} KB\n")
                
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    print(f"✗ 生成版本 {i+1} 时出错: {e}\n")
                    break
                continue
        
        if not success:
            continue
    
    print(f"\n完成! 成功生成 {version_count} 个版本")
    print(f"所有版本保存在: {os.path.abspath(output_dir)}")
    print(f"共 {len(generated_md5s)} 个不同的MD5值")


def main():
    parser = argparse.ArgumentParser(
        description='图片MD5修改工具 - 生成多个不同MD5的图片版本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python image_md5_modifier.py image.jpg          # 默认生成3张
  python image_md5_modifier.py image.jpg -n 5     # 生成5张
  python image_md5_modifier.py image.jpg -o output_folder
  python image_md5_modifier.py image.jpg -n 10    # 生成10张
        """
    )
    parser.add_argument('input', help='输入图片路径')
    parser.add_argument('-o', '--output', default=None, help='输出目录（默认：与输入文件同目录）')
    parser.add_argument('-n', '--num', type=int, default=3, help='要生成的版本数量（默认：3）')
    
    args = parser.parse_args()
    
    process_image(args.input, args.output, args.num)


if __name__ == '__main__':
    main()

