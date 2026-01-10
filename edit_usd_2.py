import os
import shutil
from pxr import Usd, UsdShade, UsdGeom, Sdf


# ============================================================
# OmniGlass 预设（根据真实 Isaac 资产经验）
# ============================================================
OMNIGLASS_PRESETS = {
    # 透明塑料（原 Plastic_Clear）
    "Plastic_Clear": {
        "thin_walled": True,
        "opacity": 0.03,
        "transmission": 1.0,
        "ior": 1.40,
        "roughness": 0.12,
        "base_color": (1.0, 1.0, 1.0),
    },

    # 蓝色半透明塑料（原 plastic_blue）
    "plastic_blue": {
        "thin_walled": True,
        "opacity": 0.08,
        "transmission": 0.9,
        "ior": 1.45,
        "roughness": 0.18,
        "base_color": (0.2, 0.4, 0.9),
    },
}


# ============================================================
# 工具函数
# ============================================================
def clear_color_primvars(mesh_prim):
    for attr_name in (
        "primvars:displayColor",
        "primvars:displayOpacity",
    ):
        if mesh_prim.HasAttribute(attr_name):
            mesh_prim.RemoveProperty(attr_name)
            print(f"      ⚠️ 移除 Mesh primvar: {attr_name}")


def get_bound_material(mesh_prim):
    binding_api = UsdShade.MaterialBindingAPI(mesh_prim)
    mat, _ = binding_api.ComputeBoundMaterial()
    return mat


def create_omniglass_material(stage, material_path):
    shader_path = f"{material_path}/OmniGlass"

    material = UsdShade.Material.Define(stage, material_path)
    shader = UsdShade.Shader.Define(stage, shader_path)

    shader.CreateIdAttr("OmniGlass")

    shader_out = shader.CreateOutput("out", Sdf.ValueTypeNames.Token)
    material.CreateSurfaceOutput().ConnectToSource(shader_out)

    return material, shader


def apply_preset_to_shader(shader, preset):
    for name, value in preset.items():
        if isinstance(value, bool):
            shader.CreateInput(
                name, Sdf.ValueTypeNames.Bool
            ).Set(value)
        elif isinstance(value, float):
            shader.CreateInput(
                name, Sdf.ValueTypeNames.Float
            ).Set(value)
        elif isinstance(value, tuple):
            shader.CreateInput(
                name, Sdf.ValueTypeNames.Color3f
            ).Set(value)


# ============================================================
# 主函数
# ============================================================
def rebind_plastic_clear_to_new_omniglass(
    usd_path: str,
    output_suffix="_omniglass",
    backup_original=True,
):
    if not os.path.exists(usd_path):
        print(f"❌ USD 文件不存在: {usd_path}")
        return None

    base, ext = os.path.splitext(usd_path)
    new_usd_path = f"{base}{output_suffix}{ext}"

    if backup_original:
        shutil.copy2(usd_path, new_usd_path)
        print(f"✅ 已备份原文件到: {new_usd_path}")

    stage = Usd.Stage.Open(new_usd_path)
    if not stage:
        print("❌ 打开 USD 失败")
        return None

    # --------------------------------------------------------
    # 创建 OmniGlass（只创建一次）
    # --------------------------------------------------------
    material_path = "/Root/container/Looks/Container_Glass"
    material, shader = create_omniglass_material(stage, material_path)

    print(f"\n✅ 创建新 OmniGlass 材质: {material_path}")

    preset_applied = False
    bind_count = 0

    # --------------------------------------------------------
    # 遍历 Mesh
    # --------------------------------------------------------
    for prim in stage.Traverse():
        if prim.GetTypeName() != "Mesh":
            continue

        mesh = UsdGeom.Mesh(prim)
        print(f"\n🔍 Mesh: {prim.GetPath()}")

        old_mat = get_bound_material(prim)
        if old_mat:
            mat_name = old_mat.GetPath().name
            print(f"  原 Material: {old_mat.GetPath()}")
        else:
            mat_name = ""
            print("  ⚠️ 没有绑定 Material")

        # ----------------------------
        # 第一次遇到匹配的材质时应用预设
        # ----------------------------
        if not preset_applied and mat_name in OMNIGLASS_PRESETS:
            print(f"  👉 使用 OmniGlass 预设: {mat_name}")
            apply_preset_to_shader(
                shader, OMNIGLASS_PRESETS[mat_name]
            )
            preset_applied = True

        # ----------------------------
        # 清理 primvars（防红）
        # ----------------------------
        clear_color_primvars(prim)

        # ----------------------------
        # 重新绑定
        # ----------------------------
        UsdShade.MaterialBindingAPI(mesh).Bind(material)
        bind_count += 1

    print(f"\n🎉 完成！共重新绑定 {bind_count} 个 Mesh")

    stage.GetRootLayer().Save()
    stage.Save()

    print(f"📦 输出文件: {new_usd_path}")
    return new_usd_path


# ============================================================
# main
# ============================================================
if __name__ == "__main__":
    usd_file = (
        "/inspire/ssd/project/robot-reasoning/"
        "cengxianchao-240108110052/yangtao/"
        "EgoVLA_Release/Ego_Humanoid_Manipulation_Benchmark/"
        "source/extensions/humanoid.tasks/humanoid/tasks/data/"
        "container/container_plastic.usd"
    )

    rebind_plastic_clear_to_new_omniglass(usd_file)