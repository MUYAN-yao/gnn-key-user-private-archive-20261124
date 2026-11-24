import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(16, 9))
ax.set_xlim(0, 16)
ax.set_ylim(0, 9)
ax.axis('off')
fig.patch.set_facecolor('white')

# Colors
trad_bg = '#F3F4F6'
trad_edge = '#CED4DA'
trad_text = '#495057'

our_bg = '#E8F3EB'
our_edge = '#70CDBE'
our_text = '#111111'

dim_bg = '#FDECDA'
dim_edge = '#F5AA61'

# Draw Title
ax.text(8, 8.2, '传统方法 vs 本项目基于多模型融合关键用户识别方法对比', ha='center', va='center', fontsize=26, fontweight='bold', color='#222222')

# Columns headers
# Left Header
ax.add_patch(patches.FancyBboxPatch((2.0, 6.9), 4.0, 0.6, boxstyle='round,pad=0,rounding_size=0.1', facecolor='#E2E6EA', edgecolor='none'))
ax.text(4.0, 7.2, '传统关键用户识别方法', ha='center', va='center', fontsize=20, fontweight='bold', color='#495057')

# Right Header
ax.add_patch(patches.FancyBboxPatch((10.0, 6.9), 4.0, 0.6, boxstyle='round,pad=0,rounding_size=0.1', facecolor='#D4EBE5', edgecolor='none'))
ax.text(12.0, 7.2, '本项目创新与融合方法', ha='center', va='center', fontsize=20, fontweight='bold', color='#0F5132')

dimensions = [
    "数据维\n度与\n特征",
    "核心识\n别模型",
    "寻优与\n验证",
    "分析与\n产出"
]

trad_texts = [
    "过度依赖粉丝数、转发量等\n浅层统计指标，特征单一",
    "基于阈值过滤或传统浅层\n机器学习模型，难以深挖拓扑",
    "缺乏物理演化过程的模拟验证\n难以跳出局部最优",
    "仅输出静态节点排名\n无法揭示传播网络内在结构"
]

our_texts = [
    "融合网络拓扑与深度语义，构建\n异构动态信息传播图与高维特征",
    "构建图神经网络(GNN)模型\n实现高阶特征提取与智能初筛",
    "引入蚁群优化(ACO)进行全局寻优\n结合传染病动力学实现双轨验证",
    "结合社区发现还原圈层结构\n动态可视化与传播路径追踪"
]

y_starts = [5.6, 4.1, 2.6, 1.1]

def draw_rounded_box(x, y, w, h, bg, edge, text, font_size=16, font_weight='normal', text_color='#111', rx=0.2):
    # Shadow
    shadow = patches.FancyBboxPatch((x-w/2+0.05, y-h/2-0.05), w, h, boxstyle=f'round,pad=0,rounding_size={rx}',
                                  facecolor='#000', edgecolor='none', alpha=0.1)
    ax.add_patch(shadow)
    
    rect = patches.FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle=f'round,pad=0,rounding_size={rx}',
                                  facecolor=bg, edgecolor=edge, linewidth=2)
    ax.add_patch(rect)
    ax.text(x, y, text, ha='center', va='center', fontsize=font_size, fontweight=font_weight, color=text_color)

# Draw Central spine
ax.plot([8, 8], [0.8, 6.5], color='#CCCCCC', lw=2, linestyle=':')

for i in range(4):
    y = y_starts[i]
    
    # Connectors
    ax.plot([4, 8], [y, y], color='#CED4DA', lw=2)
    ax.plot([8, 12], [y, y], color='#A3D8CE', lw=2)
    
    # Arrow heads for connector pointing to our project
    ax.annotate('', xy=(8.7, y), xytext=(7.3, y), arrowprops=dict(arrowstyle='->', lw=3, color='#F5AA61'))

    # Draw traditional box on the left
    draw_rounded_box(4, y, 4.4, 1.1, trad_bg, trad_edge, trad_texts[i], font_size=16, text_color=trad_text)
    
    # Draw our project box on the right
    draw_rounded_box(12, y, 4.6, 1.1, our_bg, our_edge, our_texts[i], font_size=17, font_weight='bold', text_color=our_text)
    
    # Draw dimension circle/box in the middle
    ax.add_patch(patches.Circle((8, y), 0.5, facecolor='#FFFFFF', edgecolor=dim_edge, lw=2.5, zorder=5))
    ax.add_patch(patches.Circle((8, y), 0.42, facecolor=dim_bg, edgecolor='none', zorder=5))
    ax.text(8, y, dimensions[i], ha='center', va='center', fontsize=14, fontweight='bold', color='#A66A2B', zorder=6)

# Add column background patches
ax.add_patch(patches.Rectangle((1.5, 0.4), 5.0, 6.2, facecolor='#F8F9FA', edgecolor='#DEE2E6', linewidth=1.5, linestyle='--', zorder=-1))
ax.add_patch(patches.Rectangle((9.5, 0.4), 5.0, 6.2, facecolor='#F4FAF8', edgecolor='#BEE1D9', linewidth=1.5, linestyle='--', zorder=-1))

plt.tight_layout()
plt.savefig('assets/traditional_vs_gnn_comparison.png', dpi=500, bbox_inches='tight')
print("Comparison diagram saved.")
