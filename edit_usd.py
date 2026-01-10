"""
精准修改易拉罐 USD 文件的 metallic 属性（logo + sides 两个位置）
目标：将 /Root/can/logo/_________BSDF 和 /Root/can/sides/_________BSDF 的 inputs:metallic 改为 0.0
"""
import os
import shutil
from pxr import Usd, UsdShade

def modify_can_metallic(source_usd_path, target_usd_path, metallic_value=0.0):
    """
    修改易拉罐 USD 文件中两个关键位置的 metallic 属性
    
    Args:
        source_usd_path: 源 USD 文件路径
        target_usd_path: 修改后保存的路径
        metallic_value: 要设置的金属度值（默认 0.0）
    """
    # 1. 检查源文件
    if not os.path.exists(source_usd_path):
        raise FileNotFoundError(f"源文件不存在: {source_usd_path}")
    
    # 2. 创建目标目录并复制源文件（保留原文件）
    target_dir = os.path.dirname(target_usd_path)
    os.makedirs(target_dir, exist_ok=True)
    shutil.copy2(source_usd_path, target_usd_path)
    print(f"✅ 已复制源文件到: {target_usd_path}")
    
    # 3. 打开 USD 文件
    stage = Usd.Stage.Open(target_usd_path)
    if not stage:
        raise ValueError(f"无法打开 USD 文件: {target_usd_path}")
    
    # 4. 定义需要修改的 Prim 路径（从探查结果中获取）
    prim_paths_to_modify = [
        "/Root/can/logo/_________BSDF",
        "/Root/can/sides/_________BSDF"
    ]
    attr_name = "inputs:metallic"
    modified_count = 0
    
    # 5. 逐个修改 Prim 的属性
    for prim_path in prim_paths_to_modify:
        # 定位 Prim
        prim = stage.GetPrimAtPath(prim_path)
        if not prim or not prim.IsValid():
            print(f"⚠️  Prim 不存在或无效: {prim_path}")
            continue
        
        # 尝试作为 Shader Input 修改（USDPreviewSurface 标准写法）
        shader = UsdShade.Shader(prim)
        if shader:
            inp = shader.GetInput(attr_name)
            if inp and inp.IsValid():
                old_value = inp.Get()
                inp.Set(metallic_value)
                modified_count += 1
                print(f"✅ 修改 {prim_path} → {attr_name}: {old_value} → {metallic_value}")
                continue
        
        # 备用方案：作为普通属性修改
        attr = prim.GetAttribute(attr_name)
        if attr and attr.IsValid():
            old_value = attr.Get()
            attr.Set(metallic_value)
            modified_count += 1
            print(f"✅ 修改 {prim_path} → {attr_name}: {old_value} → {metallic_value}")
        else:
            print(f"⚠️  {prim_path} 未找到 {attr_name} 属性")
    
    # 6. 保存修改
    if modified_count > 0:
        stage.Save()
        print(f"✅ 总计修改 {modified_count} 个属性，文件已保存！")
        return True
    else:
        print(f"❌ 未修改任何属性")
        return False

if __name__ == "__main__":
    # 定义文件映射（源文件 → 目标文件）
    file_mapping = {
        "/inspire/ssd/project/robot-reasoning/cengxianchao-240108110052/yangtao/EgoVLA_Release/Ego_Humanoid_Manipulation_Benchmark/source/extensions/humanoid.tasks/humanoid/tasks/data/can/can_fanta.usd":
        "/inspire/ssd/project/robot-reasoning/cengxianchao-240108110052/yangtao/EgoVLA_Release/Ego_Humanoid_Manipulation_Benchmark/source/extensions/humanoid.tasks/humanoid/tasks/data/can/can_fanta_edit.usd",
        
        "/inspire/ssd/project/robot-reasoning/cengxianchao-240108110052/yangtao/EgoVLA_Release/Ego_Humanoid_Manipulation_Benchmark/source/extensions/humanoid.tasks/humanoid/tasks/data/can/can_sprite.usd":
        "/inspire/ssd/project/robot-reasoning/cengxianchao-240108110052/yangtao/EgoVLA_Release/Ego_Humanoid_Manipulation_Benchmark/source/extensions/humanoid.tasks/humanoid/tasks/data/can/can_sprite_edit.usd"
    }
    
    # 批量处理两个文件
    total_success = 0
    for source_path, target_path in file_mapping.items():
        print("\n" + "="*80)
        print(f"开始处理: {source_path}")
        try:
            success = modify_can_metallic(source_path, target_path, metallic_value=0.0)
            if success:
                total_success += 1
        except Exception as e:
            import traceback
            print(f"❌ 处理失败: {str(e)}")
            print(f"详细错误:\n{traceback.format_exc()}")
    
    # 最终统计
    print("\n" + "="*80)
    print(f"处理完成！总计 {len(file_mapping)} 个文件，成功修改 {total_success} 个")
    if total_success == len(file_mapping):
        print("🎉 所有易拉罐文件的 metallic 属性已成功改为 0.0！")