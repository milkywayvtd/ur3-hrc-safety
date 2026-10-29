import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# ==== DỮ LIỆU GỐC (ms) ====
data_ms_new = {
    "Không có Người": [3087.01, 3039.08, 3086.63, 3039.94, 3087.15, 3037.91, 3087.60, 3040.31, 3084.05, 3039.70],
    "Khi Người ở Gần": [3081.07, 3039.68, 3088.95, 3040.29, 3084.54, 3033.99, 3088.08, 3033.96, 3085.67, 3040.54],
    "Người Chặn ở Vị trí Cố định": [9643.75, 11696.15, 8719.52, 9536.14, 8157.17, 13750.90, 11583.17, 11231.47, 8365.64, 7900.32],
    "Người Chặn ở Vị trí Động": [16470.31, 20021.23, 16006.03, 16164.42, 16126.83, 19611.00, 12302.78, 11077.38, 11670.26, 14626.00]
}


labels = list(data_ms_new.keys())
data_values = list(data_ms_new.values())

# Chia dữ liệu, vị trí và màu sắc
data_left = data_values[:2]
data_right = data_values[2:]

positions_left = np.array([1, 2])
positions_right = np.array([3, 4])
positions_all = np.concatenate((positions_left, positions_right))

colors = ['#ffc000', '#93c47d', '#6fa8dc', '#b4a7d6']
colors_left = colors[:2]
colors_right = colors[2:]
# Tạo hình và trục trái (ax1)
fig, ax1 = plt.subplots(figsize=(10, 6))

# Tạo trục phải (ax2) có chung trục X với ax1
ax2 = ax1.twinx()

# --- ĐỊNH DẠNG CHUNG ---
lw = 1.0
box_width = 0.55
box_edge_color = 'black'
median_props = dict(color='black', linewidth=1.2)
whisker_props = dict(color='black', linewidth=lw)
cap_props = dict(color='black', linewidth=lw)
box_props = dict(linewidth=lw, color=box_edge_color)

# --- VẼ TRỤC Y TRÁI (ax1): 2 Hộp đầu tiên ---
bp_left = ax1.boxplot(data_left,
                      positions=positions_left,
                      patch_artist=True,
                      widths=box_width,
                      showfliers=False,
                      whis='range', 
                      medianprops=median_props,
                      whiskerprops=whisker_props,
                      capprops=cap_props,
                      boxprops=box_props)

# Tô màu cho boxplot trục trái
for patch, color in zip(bp_left['boxes'], colors_left):
    patch.set_facecolor(color)
    patch.set_edgecolor('black')
    patch.set_alpha(0.9)


# --- VẼ TRỤC Y PHẢI (ax2): 2 Hộp cuối cùng ---
bp_right = ax2.boxplot(data_right,
                       positions=positions_right,
                       patch_artist=True,
                       widths=box_width,
                       showfliers=False,
                       whis='range',
                       medianprops=median_props,
                       whiskerprops=whisker_props,
                       capprops=cap_props,
                       boxprops=box_props)

# Tô màu cho boxplot trục phải
for patch, color in zip(bp_right['boxes'], colors_right):
    patch.set_facecolor(color)
    patch.set_edgecolor('black')
    patch.set_alpha(0.9)


# --- THIẾT LẬP TRỤC VÀ NHÃN ---

# Trục X (chung)
ax1.set_xticks(positions_all)
ax1.set_xticklabels([''] * len(labels)) # Ẩn nhãn X
ax1.tick_params(axis='x', length=0)

# Trục Y Trái (ax1)
ax1.set_ylabel("Thời gian (ms)", color='black', fontsize=30)
ax1.tick_params(axis='y', labelsize=20)
ax1.set_ylim(3000, 3100) # Giới hạn phù hợp cho nhóm 3000
ax1.grid(axis='y', linestyle='--', alpha=0.3)

# Trục Y Phải (ax2)

ax2.tick_params(axis='y', labelsize=20)
ax2.set_ylim(0, 21000) # Giới hạn phù hợp cho nhóm 10000 - 20000
# Thêm dòng kẻ đứng tại vị trí 2.5 (giữa vị trí 2 và 3)
ax1.axvline(x=2.5, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
# Tiêu đề
plt.title("Thời gian Thực hiện một Quy trình di chuyển", fontsize=30)

# --- CHÚ THÍCH (Legend) ---
legend_patches = [
    Patch(facecolor=color, edgecolor='black', label=label)
    for color, label in zip(colors, labels)
]

ax1.legend(handles=legend_patches,
           loc='lower center',
           bbox_to_anchor=(0.5, -0.25),
           ncol=2,
           frameon=False,
           fontsize=25)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()