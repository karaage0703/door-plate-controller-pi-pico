#!/usr/bin/env python3
"""
デバイスケース生成スクリプト

このスクリプトは、CadQueryを用いてW:55mm H:30mm D:20mmのデバイスに対応するケース（下部プレートおよび側面のみ、上部はオープン）の3Dモデルを作成します.
- 内部（デバイス収納部）の寸法は幅55mm、奥行20mmです.
- 下部プレートの厚さは2mm、側壁の厚さは2mm、側壁の高さは10mmとしています.
- 上面はディスプレイやボタンが存在するため空放状態としています.

Usage:
    python device_case.py
生成されたモデルは、「device_case.stl」としてエクスポートされます.

Requires:
    cadquery

Created by: Your Name
Date: 2025-03-16
"""

import cadquery as cq

# パラメータ定義 (単位: mm)
W_INNER = 55  # デバイス収納部の内部幅
D_INNER = 30  # デバイス収納部の内部奥行
WALL_THICKNESS = 2  # 壁および底板の厚さ
BOTTOM_THICKNESS = 2  # 底板の厚さ
WALL_HEIGHT = 20  # 側壁の高さ（上部オープン）

# 外形寸法 (底板は内部寸法に両側の壁厚を加算)
W_OUTER = W_INNER + 2 * WALL_THICKNESS  # 55 + 2*2 = 59mm
D_OUTER = D_INNER + 2 * WALL_THICKNESS  # 20 + 2*2 = 24mm

# 底板の生成 (XY平面上に中央配置、Z方向は下部から底板厚さ分)
bottom = cq.Workplane("XY").box(W_OUTER, D_OUTER, BOTTOM_THICKNESS, centered=(True, True, False))

# 側壁の生成：外側と内側の形状からリング状の壁を作成する
walls_outer = cq.Workplane("XY").workplane(offset=BOTTOM_THICKNESS).rect(W_OUTER, D_OUTER).extrude(WALL_HEIGHT)

walls_inner = cq.Workplane("XY").workplane(offset=BOTTOM_THICKNESS).rect(W_INNER, D_INNER).extrude(WALL_HEIGHT)

walls = walls_outer.cut(walls_inner)
# USBコネクタ用の穴を作成（短辺側の中央部の下部分に配置）
# パラメータ：幅10mm、厚さ3mm（壁方向）、高さ6mm
# 外側のY座標：外枠の短辺 = -D_OUTER/2 = -12mm
# 穴の中心は、外側から1.5mm内側に配置 -> Y = -12 + 1.5 = -10.5mm
# Z座標は底板から2mmの厚みを考慮し、下端から3mm上 -> Z = 2 + 3 = 5mm
hole = cq.Workplane("XY").box(3, 10, 6, centered=True).translate((-28, 0, 5))
case_result = bottom.union(walls).cut(hole)

# STLファイルとしてエクスポート
cq.exporters.export(case_result, "device_case.stl")

if __name__ == "__main__":
    pass
