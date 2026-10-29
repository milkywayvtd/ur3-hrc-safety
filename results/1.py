import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter

# ==== DỮ LIỆU (ms) ====
data_ms = {
    "No Human Presence": [3087.01, 3039.08, 3086.63, 3039.94, 3087.15, 3037.91, 3087.60, 3040.31, 3084.05, 3039.70],
    "When Human Is Near": [3081.07, 3039.68, 3088.95, 3040.29, 3084.54, 3033.99, 3088.08, 3033.96, 3085.67, 3040.54],
    "Human Blocks at Fixed Position": [9643.75, 11696.15, 8719.52, 9536.14, 8157.17, 13750.90, 11583.17, 11231.47, 8365.64, 7900.32],
    "Human Blocks at Dynamic Position": [16470.31, 20021.23, 16006.03, 16164.42, 16126.83, 19611.00, 12302.78, 11077.38, 11670.26, 14626.00]
}

# ==== NHÃN & MÀU ====
legend_labels_vi = {
    "No Human Presence": "Không có Sự hiện diện của Con người",
    "When Human Is Near": "Khi Con người ở gần",
    "Human Blocks at Fixed Position": "Con người cản trở ở Vị trí Cố định",
    "Human Blocks at Dynamic Position": "Con người cản trở ở Vị trí Động"
}
legend_labels_ordered = list(data_ms.keys())
legend_labels_vi_ordered = [legend_labels_vi[k] for k in legend_labels_ordered]
colors = ['#f4d03f', '#93c47d', '#6fa8dc', '#b4a7d6']

# ----------------------------------------------------
# ==== TRỤC Y BIẾN ĐỔI: Vùng lớn 6s đến 21s, Cấp số cộng +3s ====
custom_ticks_ms = np.array([
    3000, 3050, 3100, 
    5000, 
    6000, 7500, 9000, 10500, 12000, 13500, 15000, 16500, 18000, 19500, 21000 
])

y_pos_values = np.arange(len(custom_ticks_ms))
grid_ticks_indices = [0, 1, 2, 4, 6, 8, 10, 12, 14] 
grid_ticks_pos = y_pos_values[grid_ticks_indices]

# Hàm biến đổi (giữ nguyên logic)
def transform_to_y_pos(data_ms_value):
    bin_indices = np.searchsorted(custom_ticks_ms, data_ms_value, side='right') - 1
    bin_indices = np.maximum(bin_indices, 0)
    safe_upper_indices = np.minimum(bin_indices + 1, len(custom_ticks_ms) - 1)
    
    lower_ms = custom_ticks_ms[bin_indices]
    upper_ms = custom_ticks_ms[safe_upper_indices]
    lower_pos = y_pos_values[bin_indices]
    
    with np.errstate(divide='ignore', invalid='ignore'):
        ms_range = upper_ms - lower_ms
        valid_range = ms_range > 0
        y_pos = np.where(valid_range, lower_pos + (data_ms_value - lower_ms) / ms_range, lower_pos)
    
    is_out_of_range_top = data_ms_value > custom_ticks_ms[-1]
    y_pos[is_out_of_range_top] = y_pos_values[-1]
    is_out_of_range_bottom = data_ms_value < custom_ticks_ms[0]
    y_pos[is_out_of_range_bottom] = y_pos_values[0]
    
    return y_pos

# Áp dụng biến đổi cho dữ liệu
data_transformed = {}
for k, v in data_ms.items():
    data_transformed[k] = transform_to_y_pos(np.array(v)).tolist()

# ----------------------------------------------------
# ==== VẼ BIỂU ĐỒ ====
plt.style.use('default')
plt.figure(figsize=(8, 6.5))
ax = plt.gca()
positions = np.arange(1, len(data_transformed) + 1)
lw = 1.2 

for i, (label, values) in enumerate(data_transformed.items()):
    box = ax.boxplot(values,
                     positions=[positions[i]],
                     patch_artist=True,
                     widths=0.6, 
                     showfliers=False,
                     medianprops=dict(color='black', linewidth=1.5),
                     whiskerprops=dict(color='black', linewidth=lw), 
                     capprops=dict(color='black', linewidth=lw),     
                     boxprops=dict(linewidth=lw, color='black'))     
    
    for patch in box['boxes']:
        patch.set_facecolor(colors[i])
        patch.set_edgecolor('black')
        patch.set_alpha(0.9)

# ==== CÀI ĐẶT TRỤC Y TÙY CHỈNH ====
ax.set_yticks(grid_ticks_pos) 

def y_tick_formatter(y_pos, pos):
    try:
        idx = np.where(y_pos_values == y_pos)[0][0]
        tick_ms = custom_ticks_ms[idx]
        tick_s = tick_ms / 1000.0
        
        if tick_ms <= 3100:
            return f"{tick_s:.2f}"
        elif tick_ms == 5000:
            return f"{tick_s:.1f}"
        elif tick_ms % 1000 == 0:
            return f"{tick_s:.0f}"
        else:
            return f"{tick_s:.1f}"
            
    except IndexError:
        return ""

ax.yaxis.set_major_formatter(FuncFormatter(y_tick_formatter))

plt.ylim(-0.2, y_pos_values[-1] + 0.5) 
# Đã đổi thành "Thời gian (s)"
plt.ylabel("Thời gian (s)", fontsize=12) 
plt.title("Thời gian Thực hiện một Quy trình di chuyển", fontsize=13) 

# Thêm lưới cho các vạch chính
plt.grid(axis='y', linestyle='--', alpha=0.6, which='major', color='gray') 

# Loại bỏ nhãn X và vạch đánh dấu
plt.xticks(positions, [''] * len(data_transformed)) 
plt.tick_params(axis='x', length=0) 
plt.tick_params(axis='y', length=4) 

# Đã xóa dòng: plt.text(0.5, 1.07, "Hình 1", transform=ax.transAxes, ha="center", fontsize=11, weight='bold') 

# ==== LEGEND (TIẾNG VIỆT) ====
legend_patches = [Patch(facecolor=colors[i], edgecolor='black', label=legend_labels_vi_ordered[i]) for i in range(len(colors))]
plt.legend(handles=legend_patches,
           loc='lower center',
           bbox_to_anchor=(0.5, -0.25), 
           ncol=2,
           frameon=False,
           fontsize=10)

# Đã sửa lỗi cắt cụt
plt.tight_layout(rect=[0, 0, 1, 1])
plt.show()