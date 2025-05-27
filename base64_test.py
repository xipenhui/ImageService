import base64
import requests
import os

def test_process_base64():
    # 1. 设置API地址
    api_url = "http://127.0.0.1:51060/api/process/base64/randombg"
    
    # 2. 读取图片并转换为base64
    image_path = os.path.join("input-images", "qiche.png")  # 确保这个路径下有测试图片
    
    try:
        with open(image_path, "rb") as image_file:
            # 读取图片并转换为base64
            image_bytes = image_file.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # 构建请求数据
            payload = {
                "image_base64": image_base64
            }
            
            # 发送请求
            response = requests.post(api_url, json=payload)
            
            # 检查响应状态
            if response.status_code == 200:
                result = response.json()
                print("处理成功!")
                print(f"分割后的图片路径: {result.get('segmented_path')}")
                print(f"最终图片路径: {result.get('final_path')}")
                
                # 如果需要，可以将返回的base64保存为图片
                if result.get('result_base64'):
                    # 移除base64前缀（如果有）
                    base64_data = result['result_base64']
                    if ',' in base64_data:
                        base64_data = base64_data.split(',')[1]
                    
                    # 解码并保存图片
                    output_path = "output/result.png"
                    img_data = base64.b64decode(base64_data)
                    with open(output_path, "wb") as f:
                        f.write(img_data)
                    print(f"结果已保存到: {output_path}")
            else:
                print(f"请求失败: {response.status_code}")
                print(response.text)
                
    except FileNotFoundError:
        print(f"找不到图片文件: {image_path}")
    except Exception as e:
        print(f"发生错误: {str(e)}")

def test_process_path():
    # 1. 设置API地址
    api_url = "http://127.0.0.1:51060/api/process/path/randombg"
    
    # 2. 准备测试图片路径
    input_image = os.path.abspath(os.path.join("input-images", "qiche.png"))
    
    try:
        # 构建请求数据
        payload = {
            "input_image": input_image,
            # 不设置 bg_color，使用随机背景色
            # 不设置 output_image，使用默认命名
        }
        
        # 发送请求
        response = requests.post(api_url, json=payload)
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            print("\n路径处理测试成功!")
            print(f"分割后的图片路径: {result.get('segmented_path')}")
            print(f"最终图片路径: {result.get('final_path')}")
        else:
            print(f"\n请求失败: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n发生错误: {str(e)}")

def main():
    """运行所有测试用例"""
    # 确保输出目录存在
    os.makedirs("output", exist_ok=True)
    
    print("=== 测试 Base64 接口 ===")
    test_process_base64()
    
    print("\n=== 测试 Path 接口 ===")
    test_process_path()

if __name__ == "__main__":
    main()



