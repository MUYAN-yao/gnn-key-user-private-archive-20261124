import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(16, 10))
ax.set_xlim(0, 16)
ax.set_ylim(0, 10)
ax.axis('off')
fig.patch.set_facecolor('white')

# Titles
ax.text(8, 9.2, '关键用户识别方法架构对比', ha='center', va='center', fontsize=28, fontweight='bold', color='#222222')

ax.text(4, 8.2, '传统统计与启发式方法架构', ha='center', va='center', fontsize=20, fontweight='bold', color='#6C757D')
ax.text(12, 8.2, '本项目：融合多模型的 GNN 架构', ha='center', va='center', fontsize=20, fontweight='bold', color='#0F5132')

# Background panels
ax.add_patch(patches.FancyBboxPatch((1.0, 0.5), 6.0, 7.2, boxstyle='round,pad=0,rounding_size=0.2', facecolor='#F8F9FA', edgecolor='#DEE2E6', linewidth=2, linestyle='--'))
ax.add_patch(patches.FancyBboxPatch((9.0, 0.5), 6.0, 7.2, boxstyle='round,pad=0,rounding_size=0.2', facecolor='#F0FAF6', edgecolor='#BEE1D9', linewidth=2, linestyle='--'))

def draw_block(x, y, w, h, bg_color, edge_color, title, subtitle='', title_size=16, subtitle_size=14, rx=0.15):
    # Shadow
    ax.add_patch(patches.FancyBboxPatch((x-w/2+0.05, y-h/2-0.05), w, h, boxstyle=f'round,pad=0,rounding_size={rx}',
                                  facecolor='#000', edgecolor='none', alpha=0.1))
    # Box
    ax.add_patch(patches.FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle=f'round,pad=0,rounding_size={rx}',
                                  facecolor=bg_color, edgecolor=edge_color, linewidth=2))
    
    if subtitle:
        ax.text(x, y + 0.2, title, ha='center', va='center', fontsize=title_size, fontweight='bold', color='#222')
        ax.text(x, y - 0.25, subtitle, ha='center', va='center', fontsize=subtitle_size, color='#444')
    else:
        ax.text(x, y, title, ha='center', va='center', fontsize=title_size, fontweight='bold', color='#222')

def draw_arrow(x1, y1, x2, y2, color):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='-|>', lw=3, color=color, mutation_scale=20))

# ================= 左侧：传统架构 =================
t_x = 4.0
draw_block(t_x, 6.8, 4.8, 1.2, '#E9ECEF', '#CED4DA', '静态浅层数据输入', '提取粉丝数、转发量等单一统计指标')
draw_arrow(t_x, 6.2, t_x, 5.2, '#ADB5BD')

draw_block(t_x, 4.6, 4.8, 1.2, '#E9ECEF', '#CED4DA', '阈值过滤或传统启发式算法', '缺乏高阶拓扑信息，易陷入局部最优')
draw_arrow(t_x, 4.0, t_x, 3.0, '#ADB5BD')

draw_block(t_x, 2.4, 4.8, 1.2, '#E9ECEF', '#CED4DA', '黑盒打分与静态排名', '缺乏物理机理验证，无法揭示传播动态')
draw_arrow(t_x, 1.8, t_x, 1.4, '#ADB5BD')

draw_block(t_x, 1.0, 4.8, 0.8, '#DFE3E7', '#ADB5BD', '输出：一维节点重要性列表', '', title_size=15)

# ================= 右侧：本项目架构 =================
o_x = 12.0
draw_block(o_x, 6.8, 5.2, 1.2, '#D4EBE5', '#A3D8CE', '多源异构动态图谱构建', '融合网络拓扑与深度语义(BERT)，构建高维图数据')
draw_arrow(o_x, 6.2, o_x, 5.5, '#70CDBE')

draw_block(o_x, 4.9, 5.2, 1.2, '#FDECDA', '#F5AA61', '图神经网络 (GNN) 智能初筛', '引入注意力机制提取高阶特征，精准定位传播通道')
draw_arrow(o_x, 4.3, o_x, 3.6, '#F5AA61')

# Dual Verification block
ax.add_patch(patches.FancyBboxPatch((o_x-2.6, 2.1), 5.2, 1.5, boxstyle='round,pad=0,rounding_size=0.15',
                              facecolor='#E6F2FF', edgecolor='#A9C6EB', linewidth=2))
ax.text(o_x, 3.3, '双轨反向验证与全局寻优', ha='center', va='center', fontsize=16, fontweight='bold', color='#154360')

draw_block(o_x-1.25, 2.6, 2.3, 0.8, '#B8D4F0', '#83ADD6', '蚁群优化 (ACO)', '结合GNN先验全局寻优', title_size=14, subtitle_size=12)
draw_block(o_x+1.25, 2.6, 2.3, 0.8, '#B8D4F0', '#83ADD6', '传染病动力学', 'SIR级联传播模拟验证', title_size=14, subtitle_size=12)

draw_arrow(o_x, 2.1, o_x, 1.4, '#83ADD6')

draw_block(o_x, 1.0, 5.2, 0.8, '#D8D0E8', '#AC99D2', '系统落地：圈层结构解析与动态可视化追踪', '', title_size=15)

# ================= 对比箭头 =================
ax.annotate('架构\n降维\n打击', xy=(9.0, 4.6), xytext=(7.0, 4.6),
            arrowprops=dict(facecolor='#EB7E60', edgecolor='none', width=10, headwidth=25, headlength=20, shrink=0.05),
            fontsize=18, fontweight='bold', color='white', ha='center', va='center',
            bbox=dict(boxstyle='circle', facecolor='#EB7E60', edgecolor='none', pad=0.3))


plt.tight_layout()
plt.savefig('assets/architecture_comparison.png', dpi=500, bbox_inches='tight')
print("Architecture comparison diagram saved.")
