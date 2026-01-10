"""
探查 USD 文件中所有材质相关属性（修复 IsValid() 版本兼容问题）
找到金属度属性的真实路径和名称
"""
import os
from pxr import Usd, UsdShade, Sdf

def is_valid_material(mat):
    """兼容不同版本的 Material 验证"""
    try:
        return mat.IsValid()
    except AttributeError:
        return bool(mat)

def is_valid_shader(shader):
    """兼容不同版本的 Shader 验证"""
    try:
        return shader.IsValid()
    except AttributeError:
        return bool(shader)

def safe_get_attr_value(attr):
    """安全获取属性值，避免报错"""
    try:
        return attr.Get()
    except:
        return "无法读取"

def explore_material_attributes(usd_path):
    """遍历并打印所有材质相关属性"""
    print(f"\n===== 开始探查文件: {usd_path} =====")
    
    # 打开 USD 文件（延迟加载）
    stage = Usd.Stage.Open(usd_path, Usd.Stage.LoadNone)
    if not stage:
        print("❌ 无法打开文件")
        return
    
    # 存储所有找到的属性
    all_attrs = []
    
    # 遍历所有 Prim（简化遍历逻辑，避免路径解析错误）
    for prim in stage.Traverse():
        try:
            prim_path = str(prim.GetPath())
            if not prim_path or prim_path == "/":
                continue
            
            # 1. 尝试转换为材质/着色器
            mat = UsdShade.Material(prim)
            shader = UsdShade.Shader(prim)
            is_mat = is_valid_material(mat)
            is_shad = is_valid_shader(shader)
            
            # 只处理材质/着色器相关 Prim
            if not (is_mat or is_shad):
                continue
            
            print(f"\n📌 Prim 路径: {prim_path}")
            print(f"   类型: {'Material' if is_mat else 'Shader'}")
            
            # 2. 打印所有普通属性
            attrs = prim.GetAttributes()
            for attr in attrs:
                attr_name = attr.GetName()
                attr_type = attr.GetTypeName()
                attr_value = safe_get_attr_value(attr)
                all_attrs.append((prim_path, attr_name, attr_value))
                print(f"   属性: {attr_name} = {attr_value} (类型: {attr_type})")
            
            # 3. 打印 Shader Input/Output（如果是着色器）
            if is_shad:
                # 获取所有 Input
                try:
                    inputs = shader.GetInputs()
                    if inputs:
                        print("   Inputs:")
                        for inp in inputs:
                            inp_name = inp.GetFullName()
                            inp_value = safe_get_attr_value(inp)
                            all_attrs.append((prim_path, inp_name, inp_value))
                            print(f"     - {inp_name} = {inp_value}")
                except:
                    pass
                
                # 获取所有 Output
                try:
                    outputs = shader.GetOutputs()
                    if outputs:
                        print("   Outputs:")
                        for out in outputs:
                            out_name = out.GetFullName()
                            out_value = safe_get_attr_value(out)
                            print(f"     - {out_name} = {out_value}")
                except:
                    pass
        
        except Exception as e:
            # 跳过出错的 Prim，继续处理
            continue
    
    # 4. 搜索所有包含 "metal" 的属性（不区分大小写）
    print("\n===== 搜索包含 'metal' 的属性 =====")
    metal_attrs = []
    for prim_path, attr_name, value in all_attrs:
        if "metal" in attr_name.lower() and value != "无法读取":
            metal_attrs.append((prim_path, attr_name, value))
    
    if metal_attrs:
        for prim_path, attr_name, value in metal_attrs:
            print(f"🔍 找到金属度相关属性:")
            print(f"   Prim 路径: {prim_path}")
            print(f"   属性名称: {attr_name}")
            print(f"   当前值: {value}")
    else:
        print("❌ 未找到包含 'metal' 的属性")
        # 打印所有浮点/数值型属性（金属度通常是数值）
        print("\n===== 所有数值型属性（前30个） =====")
        numeric_attrs = []
        for prim_path, attr_name, value in all_attrs:
            if isinstance(value, (int, float)):
                numeric_attrs.append((prim_path, attr_name, value))
        
        for i, (prim_path, attr_name, value) in enumerate(numeric_attrs[:30]):
            print(f"{i+1}. {prim_path} → {attr_name} = {value}")

if __name__ == "__main__":
    # 探查你的两个文件
    files = [
        # "/inspire/ssd/project/robot-reasoning/cengxianchao-240108110052/yangtao/EgoVLA_Release/Ego_Humanoid_Manipulation_Benchmark/source/extensions/humanoid.tasks/humanoid/tasks/data/can/can_fanta.usd",
        # "/inspire/ssd/project/robot-reasoning/cengxianchao-240108110052/yangtao/EgoVLA_Release/Ego_Humanoid_Manipulation_Benchmark/source/extensions/humanoid.tasks/humanoid/tasks/data/can/can_sprite.usd"
        "/inspire/ssd/project/robot-reasoning/cengxianchao-240108110052/yangtao/EgoVLA_Release/Ego_Humanoid_Manipulation_Benchmark/source/extensions/humanoid.tasks/humanoid/tasks/data/container/container_plastic.usd"
    ]
    
    for file in files:
        explore_material_attributes(file)
        print("\n" + "-"*100)