import time
import os
import json
import random
import string
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 配置参数
REFRESH_INTERVAL = 1  # 刷新间隔（秒）
TOTAL_REFRESH_COUNT = 360  # 总刷新次数
WAIT_AFTER_TEST = 4  # 每次测速后等待时间（秒）

# 基础User-Agent模板列表
USER_AGENT_TEMPLATES = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36 Edg/{edge_version}",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{firefox_version}.0) Gecko/20100101 Firefox/{firefox_version}.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{mac_version}_{mac_patch}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{mac_version}_{mac_patch}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari_version} Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS {ios_version} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari_version} Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS {ios_version} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari_version} Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android {android_version}; {device_model}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android {android_version}; {device_model}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
]

def generate_random_version():
    """生成随机版本号"""
    major = random.randint(100, 130)
    minor = random.randint(0, 9)
    patch = random.randint(0, 9999)
    return f"{major}.{minor}.{patch}"

def generate_random_chrome_version():
    """生成随机Chrome版本号"""
    major = random.randint(115, 125)
    minor = random.randint(0, 9)
    patch = random.randint(0, 9999)
    return f"{major}.{minor}.{patch}"

def generate_random_firefox_version():
    """生成随机Firefox版本号"""
    major = random.randint(100, 121)
    minor = random.randint(0, 9)
    return f"{major}.{minor}"

def generate_random_safari_version():
    """生成随机Safari版本号"""
    major = random.randint(14, 17)
    minor = random.randint(0, 9)
    patch = random.randint(0, 9)
    return f"{major}.{minor}.{patch}"

def generate_random_ios_version():
    """生成随机iOS版本号"""
    major = random.randint(14, 17)
    minor = random.randint(0, 9)
    patch = random.randint(0, 9)
    return f"{major}_{minor}_{patch}"

def generate_random_android_version():
    """生成随机Android版本号"""
    major = random.randint(10, 14)
    minor = random.randint(0, 9)
    return f"{major}"

def generate_random_mac_version():
    """生成随机macOS版本号"""
    major = random.randint(14, 16)
    minor = random.randint(0, 9)
    patch = random.randint(0, 9)
    return f"{major}_{minor}_{patch}"

def generate_random_device_model():
    """生成随机设备型号"""
    prefixes = ["SM-", "Pixel ", "iPhone", "iPad", "Mi ", "Redmi ", "OnePlus "]
    models = ["G991B", "S928U", "12 Pro", "13 Mini", "9", "10", "11", "12", "Note 10", "S21", "S22"]
    numbers = ["", str(random.randint(1, 20)), f"{random.randint(1, 9)}T"]
    
    return f"{random.choice(prefixes)}{random.choice(models)}{random.choice(numbers)}"

def generate_random_build_id():
    """生成随机构建ID"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def generate_random_user_agent():
    """生成带有随机字符的User-Agent"""
    template = random.choice(USER_AGENT_TEMPLATES)
    
    # 生成随机参数
    params = {
        'version': generate_random_chrome_version(),
        'edge_version': generate_random_version(),
        'firefox_version': generate_random_firefox_version(),
        'safari_version': generate_random_safari_version(),
        'ios_version': generate_random_ios_version(),
        'android_version': generate_random_android_version(),
        'device_model': generate_random_device_model(),
        'mac_version': generate_random_mac_version(),
        'mac_patch': random.randint(0, 9)
    }
    
    # 应用参数到模板
    user_agent = template.format(**params)
    
    # 添加随机字符到User-Agent的不同位置
    if random.random() < 0.7:  # 70%的概率添加额外信息
        extra_info = [
            f" Build/{generate_random_build_id()}",
            f" Revision/{random.randint(1000, 9999)}",
            f" AppleWebKit/{generate_random_version()}",
            f" KHTML/{generate_random_version()}",
            f" like Gecko",
            f" Mobile",
            f" Tablet",
            f" Desktop"
        ]
        
        # 随机选择1-3个额外信息
        num_extras = random.randint(1, 3)
        selected_extras = random.sample(extra_info, num_extras)
        user_agent += ''.join(selected_extras)
    
    # 随机添加一些特殊字符（小概率）
    if random.random() < 0.2:
        special_chars = ['_', '-', '.', '+']
        insert_pos = random.randint(len(user_agent) // 2, len(user_agent) - 1)
        user_agent = user_agent[:insert_pos] + random.choice(special_chars) + user_agent[insert_pos:]
    
    return user_agent

def ensure_result_directory():
    """确保结果目录存在"""
    result_dir = "result"
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
        print(f"创建结果目录: {result_dir}")
    return result_dir

def read_urls_from_file(filename):
    """从文件中读取URL列表"""
    urls = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):  # 跳过空行和注释
                    urls.append(line)
        return urls
    except FileNotFoundError:
        print(f"错误：找不到文件 {filename}")
        return []
    except Exception as e:
        print(f"读取文件时出错: {str(e)}")
        return []

def setup_driver():
    """设置Chrome WebDriver"""
    chrome_options = Options()
    
    # 浏览器设置
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 设置随机User-Agent
    user_agent = generate_random_user_agent()
    chrome_options.add_argument(f'--user-agent={user_agent}')
    print(f"设置浏览器User-Agent: {user_agent[:80]}...")
    
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"使用默认ChromeDriver失败: {str(e)}")
        try:
            service = Service(executable_path='/usr/bin/chromedriver')
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e2:
            print(f"使用系统chromedriver也失败: {str(e2)}")
            raise

def wait_for_test_completion(driver, timeout=60):
    """等待测速完成"""
    try:
        print(f"等待测速完成，预计需要{timeout}秒...")
        time.sleep(timeout)
        return True
    except Exception as e:
        print(f"等待测速完成时出错: {str(e)}")
        return False

def set_random_user_agent_in_input(driver):
    """使用JavaScript强制为UA输入框设置随机User-Agent"""
    try:
        # 生成随机User-Agent
        random_ua = generate_random_user_agent()
        print(f"生成的随机User-Agent: {random_ua[:80]}...")
        
        # 使用JavaScript强制设置UA输入框的值
        js_script = f"""
        // 尝试通过ID查找元素
        var uaInput = document.getElementById('ua');
        if (uaInput) {{
            uaInput.value = '{random_ua}';
            console.log('通过ID设置UA成功');
            return true;
        }}
        
        // 如果还找不到，尝试通过placeholder或标签文本查找
        var inputs = document.querySelectorAll('input');
        for (var i = 0; i < inputs.length; i++) {{
            var input = inputs[i];
            if (input.type === 'text' && input.id.toLowerCase().includes('ua')) {{
                input.value = '{random_ua}';
                console.log('通过ID包含ua设置UA成功');
                return true;
            }}
            if (input.name && input.name.toLowerCase().includes('ua')) {{
                input.value = '{random_ua}';
                console.log('通过name包含ua设置UA成功');
                return true;
            }}
        }}
        
        // 最后尝试通过表单字段查找
        var labels = document.querySelectorAll('label');
        for (var i = 0; i < labels.length; i++) {{
            if (labels[i].textContent && labels[i].textContent.toLowerCase().includes('user-agent')) {{
                var forId = labels[i].getAttribute('for');
                if (forId) {{
                    uaInput = document.getElementById(forId);
                    if (uaInput) {{
                        uaInput.value = '{random_ua}';
                        console.log('通过label关联设置UA成功');
                        return true;
                    }}
                }}
            }}
        }}
        
        console.log('未找到UA输入框');
        return false;
        """
        
        # 执行JavaScript
        result = driver.execute_script(js_script)
        
        if result:
            print("成功通过JavaScript设置User-Agent")
            return True
        else:
            print("警告：JavaScript未找到UA输入框，尝试备用方法...")
            # 备用方法：尝试直接通过选择器设置
            try:
                # 尝试多种可能的选择器
                selectors = [
                    '#ua',
                    'input[name="ua"]',
                    'input[placeholder*="user-agent" i]',
                    'input[placeholder*="ua" i]',
                    'input[id*="ua" i]',
                    'input[name*="ua" i]'
                ]
                
                for selector in selectors:
                    try:
                        ua_input = driver.find_element(By.CSS_SELECTOR, selector)
                        driver.execute_script(f"arguments[0].value = '{random_ua}';", ua_input)
                        print(f"通过选择器 {selector} 设置UA成功")
                        return True
                    except:
                        continue
                
                print("所有备用方法都失败，继续测试...")
                return False
                
            except Exception as e:
                print(f"备用方法设置UA时出错: {str(e)}")
                return False
                
    except Exception as e:
        print(f"设置User-Agent时出错: {str(e)}")
        return False

def run_speed_test(driver, url):
    """对单个URL运行测速测试"""
    try:
        print(f"开始测试: {url}")
        
        # 打开测速网站
        driver.get("https://www.itdog.cn/http/")
        
        # 等待页面加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "host"))
        )
        
        # 设置随机User-Agent
        set_random_user_agent_in_input(driver)
        
        # 清空输入框并输入URL
        input_field = driver.find_element(By.ID, "host")
        input_field.clear()
        input_field.send_keys(url)
        
        # 直接触发JavaScript事件
        print("触发测速事件...")
        driver.execute_script("check_form('fast')")
        
        print("测速中，请等待...")
        
        # 等待测速完成
        if wait_for_test_completion(driver, timeout=WAIT_AFTER_TEST):
            # 获取结果
            try:
                result_element = driver.find_element(By.ID, "return_info")
                result = result_element.text
                
                # 获取测速时间
                try:
                    time_element = driver.find_element(By.CLASS_NAME, "time")
                    test_time = time_element.text
                    result = f"测速时间: {test_time}\n{result}"
                except NoSuchElementException:
                    pass
                    
                return result
            except NoSuchElementException:
                return "无法找到结果元素"
        else:
            return "测速超时"
            
    except Exception as e:
        return f"测试过程中出现错误: {str(e)}"

def save_single_result(result_dir, url, result, refresh_count, test_count):
    """保存单次测试结果到文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{result_dir}/{url.replace('://', '_').replace('/', '_').replace(':', '_')}_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"URL: {url}\n")
            f.write(f"刷新次数: {refresh_count}\n")
            f.write(f"测试序号: {test_count}\n")
            f.write("="*50 + "\n")
            f.write(result + "\n")
        return filename
    except Exception as e:
        print(f"保存结果到文件时出错: {str(e)}")
        return None

def save_summary_result(result_dir, all_results):
    """保存汇总结果"""
    summary_file = f"{result_dir}/summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("测速结果汇总\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总测试次数: {len(all_results)}\n")
            f.write("="*80 + "\n\n")
            
            for i, res in enumerate(all_results, 1):
                f.write(f"{i}. URL: {res['url']}\n")
                f.write(f"   测试时间: {res['timestamp']}\n")
                f.write(f"   刷新次数: {res['refresh_count']}\n")
                f.write(f"   测试序号: {res['test_count']}\n")
                f.write(f"   结果:\n{res['result']}\n")
                f.write("-" * 80 + "\n")
        
        print(f"汇总结果已保存到: {summary_file}")
        return summary_file
    except Exception as e:
        print(f"保存汇总结果时出错: {str(e)}")
        return None

def main():
    # 确保结果目录存在
    result_dir = ensure_result_directory()
    
    # 读取URL列表
    urls = read_urls_from_file("dependency.txt")
    
    if not urls:
        print("没有找到有效的URL，请检查dependency.txt文件")
        return
    
    print(f"找到 {len(urls)} 个URL进行测试")
    print(f"刷新间隔: {REFRESH_INTERVAL}秒")
    print(f"总刷新次数: {TOTAL_REFRESH_COUNT}次")
    print(f"结果将保存到: {result_dir}目录")
    
    # 设置WebDriver
    try:
        driver = setup_driver()
    except Exception as e:
        print(f"无法初始化WebDriver: {str(e)}")
        return
    
    all_results = []
    refresh_count = 0
    test_count = 0
    
    try:
        while refresh_count < TOTAL_REFRESH_COUNT:
            refresh_count += 1
            print(f"\n{'='*60}")
            print(f"开始第 {refresh_count}/{TOTAL_REFRESH_COUNT} 轮刷新测试")
            print(f"{'='*60}")
            
            # 对每个URL进行测试
            for i, url in enumerate(urls, 1):
                test_count += 1
                print(f"\n正在测试第 {i}/{len(urls)} 个URL (总测试序号: {test_count})")
                
                result = run_speed_test(driver, url)
                
                # 保存单次结果
                saved_file = save_single_result(result_dir, url, result, refresh_count, test_count)
                if saved_file:
                    print(f"结果已保存到: {saved_file}")
                
                all_results.append({
                    'url': url,
                    'result': result,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'refresh_count': refresh_count,
                    'test_count': test_count
                })
                
                print(f"测试完成: {url}")
                print(f"结果摘要: {result[:100]}..." if len(result) > 100 else f"结果: {result}")
                print("-" * 60)
            
            # 如果不是最后一次刷新，等待下一次刷新
            if refresh_count < TOTAL_REFRESH_COUNT:
                print(f"\n等待 {REFRESH_INTERVAL} 秒后进行下一次刷新...")
                for remaining in range(REFRESH_INTERVAL, 0, -1):
                    print(f"\r剩余等待时间: {remaining}秒", end='', flush=True)
                    time.sleep(1)
                print("\n开始下一次刷新...")
                
                # 刷新浏览器
                driver.refresh()
                time.sleep(3)  # 等待刷新完成
        
        # 保存汇总结果
        summary_file = save_summary_result(result_dir, all_results)
        
        # 打印最终统计
        print(f"\n{'='*80}")
        print("所有测试完成！")
        print(f"总刷新次数: {refresh_count}")
        print(f"总测试次数: {test_count}")
        print(f"结果文件保存在: {result_dir}目录")
        if summary_file:
            print(f"汇总文件: {summary_file}")
        print(f"{'='*80}")
            
    except KeyboardInterrupt:
        print("\n用户中断测试")
        # 保存已完成的测试结果
        if all_results:
            save_summary_result(result_dir, all_results)
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        if all_results:
            save_summary_result(result_dir, all_results)
    finally:
        # 关闭浏览器
        if 'driver' in locals():
            driver.quit()
            print("浏览器已关闭")

if __name__ == "__main__":
    main()
