import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# ==== DỮ LIỆU (ms) ====
data_ms = {
    "Không có Người": [16.95, 14.98, 18.01, 15.86, 15.70, 15.39, 16.43, 15.03, 16.43, 20.40],
    "Khi Người ở Gần": [13.81, 12.55, 16.93, 14.05, 12.09, 13.72, 10.51, 9.93, 16.53, 14.80],
    "Người Chặn ở Vị trí Cố định": [12.20, 11.65, 37.94, 11.48, 37.36, 31.36, 28.36, 11.36, 12.45, 19.76],
    "Người Chặn ở Vị trí Động": [38.93, 47.49, 15.06, 12.25, 11.84, 51.74, 39.65, 43.05, 44.87, 13.43]
}

# Chuyển ms → s
data = {k: (np.array(v) / 1000.0).tolist() for k, v in data_ms.items()}

labels = list(data.keys())
data_values = list(data.values())
positions = np.arange(1, len(data) + 1)

# ==== MÀU ====
colors = ['#ffc000', '#93c47d', '#6fa8dc', '#b4a7d6']

# ==== VẼ ====
plt.figure(figsize=(10, 6))
ax = plt.gca()

for i, values in enumerate(data_values):
    lw = 1.0
    box_width = 0.55
    box_edge_color = 'black'
    
    box = ax.boxplot(values,
                     positions=[positions[i]],
                     patch_artist=True,
                     widths=box_width,
                     showfliers=False,
                     whis='range',  # Đảm bảo râu kéo đến giá trị min/max
                     medianprops=dict(color='black', linewidth=1.2),
                     whiskerprops=dict(color='black', linewidth=lw),
                     capprops=dict(color='black', linewidth=lw),
                     boxprops=dict(linewidth=lw, color=box_edge_color))

    # Tô màu box
    for patch in box['boxes']:
        patch.set_facecolor(colors[i])
        patch.set_edgecolor('black')
        patch.set_alpha(0.9)

# ==== TRỤC ====
plt.yscale('linear')
plt.ylabel("Thời gian (s)", fontsize=30)
plt.title("Thời gian Tính toán Quỹ đạo (giây) ", fontsize=30,)
#mv làm tròn
max_val = max([max(v) for v in data_values])
y_max = np.ceil(max_val * 100) / 100.0
y_max = max(0.06, y_max)

y_ticks = np.arange(0, y_max + 0.01, 0.01)
plt.ylim(0, y_max)
plt.yticks(y_ticks, [f"{t:.2f}" for t in y_ticks], fontsize=30)

plt.xticks(positions, [''] * len(data))


plt.grid(axis='y', linestyle='--', alpha=0.5)





# ==== LEGEND ====
legend_patches = [
    Patch(facecolor=colors[i], edgecolor='black', label=labels[i])
    for i in range(len(colors))
]


plt.legend(handles=legend_patches,
           loc='lower center',
           bbox_to_anchor=(0.5, -0.22),
           ncol=2,
           frameon=False,
           fontsize=25)

# ==== FIGTEXT ====
plt.figtext(0.5, -0.15, "Hình 13: Đồ thị thời gian tính toán quỹ đạo",
            ha="center", fontsize=13)

plt.tight_layout(rect=[0, 0, 1, 0.90])
plt.show()