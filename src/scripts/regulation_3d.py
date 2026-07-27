"""
kenchiku-quest 法規ワールド — Blender(bpy) 3D可視化スクリプト
敷地・道路斜線・隣地斜線・可建築高さを3D表示
"""

import bpy
import math
from mathutils import Vector

# ===== 敷地データ =====
site = {
    "width": 15.0,      # m
    "depth": 20.0,      # m
    "road_width": 6.0,  # m
    "road_direction": "south",  # south/north/east/west
    "district": "第一種住居",
    "bCR_max": 60.0,    # 建蔽率上限 %
    "fAR_max": 200.0,   # 容積率上限 %
    "sun_slope": 1.25,  # 北側斜線 1:1.25 (H=1.25L)
    "road_slope": 1.5,  # 道路斜線 1:1.5
}

def clear_scene():
    """シーンをクリア"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    # マテリアルも削除
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)
    # ライト・カメラも削除
    for obj in bpy.data.objects:
        if obj.type in ('LIGHT', 'CAMERA'):
            bpy.data.objects.remove(obj, do_unlink=True)

def create_ground(site_w, site_d):
    """敷地地面（グリッド）"""
    bpy.ops.mesh.primitive_plane_add(size=1, location=(site_w/2, site_d/2, 0))
    ground = bpy.context.active_object
    ground.name = "敷地"
    ground.scale = (site_w, site_d, 1)
    ground.dimensions = (site_w, site_d, 0.01)
    
    mat = bpy.data.materials.new(name="敷地マット")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.05, 0.1, 0.05, 1)
    bsdf.inputs["Roughness"].default_value = 0.9
    ground.data.materials.append(mat)
    return ground

def create_road(site_w, site_d, road_w, direction="south"):
    """道路"""
    if direction == "south":
        loc = (site_w/2, -road_w/2, 0.01)
        scale = (site_w, road_w, 0.01)
    elif direction == "north":
        loc = (site_w/2, site_d + road_w/2, 0.01)
        scale = (site_w, road_w, 0.01)
    elif direction == "east":
        loc = (site_w + road_w/2, site_d/2, 0.01)
        scale = (road_w, site_d, 0.01)
    else:  # west
        loc = (-road_w/2, site_d/2, 0.01)
        scale = (road_w, site_d, 0.01)
    
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    road = bpy.context.active_object
    road.name = "道路"
    road.scale = scale
    
    mat = bpy.data.materials.new(name="道路マット")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.15, 0.15, 0.18, 1)
    road.data.materials.append(mat)

def draw_line(points, name, color=(1,0,0,1), thickness=0.03):
    """3Dライン描画"""
    curve = bpy.data.curves.new(name, type='CURVE')
    curve.dimensions = '3D'
    spline = curve.splines.new('POLY')
    spline.points.add(len(points)-1)
    for i, p in enumerate(points):
        spline.points[i].co = (p[0], p[1], p[2], 1)
    
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    
    # 太さ
    curve.bevel_depth = thickness
    
    # マテリアル（Emission BSDFで発光）
    mat = bpy.data.materials.new(name=f"{name}_マット")
    mat.use_nodes = True
    # 全ノード削除 + 新規Emission BSDF
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    for n in list(nodes):
        nodes.remove(n)
    
    emi_node = nodes.new(type='ShaderNodeEmission')
    emi_node.inputs["Color"].default_value = color
    emi_node.inputs["Strength"].default_value = 3.0
    
    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    links.new(emi_node.outputs[0], out_node.inputs[0])
    
    # outputノードをアクティブに
    out_node.is_active_output = True
    
    obj.data.materials.append(mat)
    return obj

def create_sun_slope(site_w, site_d, slope_hl=1.25):
    """北側斜線（日影規制）— 北側境界から1:1.25で傾斜する面"""
    # 北側境界線（depthの端）
    base_y = site_d
    max_h = site_w * slope_hl
    
    points = [
        (0, base_y, 0),
        (site_w, base_y, 0),
        (site_w, base_y, max_h),
        (0, base_y, max_h),
    ]
    
    # 面を作成
    mesh = bpy.data.meshes.new("北側斜線面")
    obj = bpy.data.objects.new("北側斜線", mesh)
    bpy.context.collection.objects.link(obj)
    
    import bmesh
    bm = bmesh.new()
    verts = [bm.verts.new(p) for p in points]
    bm.faces.new(verts)
    bm.to_mesh(mesh)
    bm.free()
    
    mat = bpy.data.materials.new(name="斜線マット")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (1.0, 0.8, 0.0, 1)
    bsdf.inputs["Alpha"].default_value = 0.3
    mat.blend_method = 'BLEND'
    obj.data.materials.append(mat)
    return obj

def create_building(x, y, w, d, h, name="建物"):
    """建物ボリューム"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x + w/2, y + d/2, h/2))
    bldg = bpy.context.active_object
    bldg.name = name
    bldg.scale = (w, d, h)
    
    # 判定（斜線に違反してるか）
    violates = False
    # 簡易判定：高さ > 北側斜線の高さ @ 建物位置
    # 実際は厳密にチェック
    
    mat = bpy.data.materials.new(name=f"{name}_マット")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    if violates:
        bsdf.inputs["Base Color"].default_value = (1.0, 0.1, 0.1, 0.5)
        mat.blend_method = 'BLEND'
    else:
        bsdf.inputs["Base Color"].default_value = (0.4, 0.6, 1.0, 0.6)
        mat.blend_method = 'BLEND'
    bldg.data.materials.append(mat)
    return bldg

def setup_camera(site_w, site_d):
    """カメラ設定"""
    bpy.ops.object.camera_add(location=(site_w/2, -15, 20))
    cam = bpy.context.active_object
    cam.rotation_euler = (1.1, 0, 0)
    cam.name = "法規カメラ"
    bpy.context.scene.camera = cam
    
    # ライト
    bpy.ops.object.light_add(type='SUN', location=(site_w+10, -10, 30))
    light = bpy.context.active_object
    light.rotation_euler = (1.0, 0.5, 0)

def main():
    """法規3D可視化を実行"""
    clear_scene()
    
    s = site
    create_ground(s["width"], s["depth"])
    create_road(s["width"], s["depth"], s["road_width"], s["road_direction"])
    create_sun_slope(s["width"], s["depth"], s["sun_slope"])
    
    # 道路斜線
    road_line = [
        (0, -s["road_width"], 0),
        (0, -s["road_width"], s["road_width"] * s["road_slope"]),
        (s["width"], -s["road_width"], s["road_width"] * s["road_slope"]),
        (s["width"], -s["road_width"], 0),
    ]
    draw_line(road_line[:2], "道路斜線左", color=(0,1,1,1), thickness=0.05)
    draw_line(road_line[2:], "道路斜線右", color=(0,1,1,1), thickness=0.05)
    
    # 建物（テスト配置）
    # 合法例
    create_building(2, 2, 6, 8, 10, "建物A（合法）")
    # 違反例（斜線超過）
    # create_building(2, 2, 6, 8, 25, "建物B（違反）")
    
    setup_camera(s["width"], s["depth"])
    
    print(f"[法規3D] 敷地 {s['width']}m × {s['depth']}m 生成完了")
    print(f"  建蔽率上限: {s['bCR_max']}%  容積率上限: {s['fAR_max']}%")

if __name__ == "__main__":
    main()
