import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 创建画布，背景设为极浅的灰白色以模仿参考图的干净质感
fig, ax = plt.subplots(figsize=(16, 12))
fig.patch.set_facecolor('#FAFBFC')
ax.set_facecolor('#FAFBFC')
ax.set_xlim(0, 20)
ax.set_ylim(4.0, 18.5)
ax.axis('off')

# ----------------- 标题与分隔线 -----------------
# 左右两栏小标题
ax.text(5.5, 17.6, '传统基线方法技术架构', ha='center', va='center', fontsize=20, fontweight='bold', color='#222222')
ax.text(14.5, 17.6, '本项目融合 GNN 与复杂网络架构', ha='center', va='center', fontsize=20, fontweight='bold', color='#222222')

# 中央垂直分隔线
ax.plot([10, 10], [5.0, 18], color='#D0D7DE', lw=1.5)

# ----------------- 外围虚线大框 -----------------
# 左侧大框
left_dash_box = patches.FancyBboxPatch((1.5, 4.5), 8.0, 12.0, boxstyle='round,pad=0,rounding_size=0.2',
                                       facecolor='none', edgecolor='#A5B0BA', lw=1.5, linestyle='--')
ax.add_patch(left_dash_box)

# 右侧大框
right_dash_box = patches.FancyBboxPatch((10.5, 4.5), 8.0, 12.0, boxstyle='round,pad=0,rounding_size=0.2',
                                        facecolor='none', edgecolor='#A5B0BA', lw=1.5, linestyle='--')
ax.add_patch(right_dash_box)

# ----------------- 绘图辅助函数 -----------------
def draw_node(x, y, w, h, bg, edge, title, subtitle='', rx=0.15, text_color='#24292F'):
    # 绘制矩形节点
    rect = patches.FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle=f'round,pad=0,rounding_size={rx}',
                                  facecolor=bg, edgecolor=edge, lw=1.2)
    ax.add_patch(rect)
    
    if subtitle:
        ax.text(x, y + h*0.15, title, ha='center', va='center', fontsize=16, fontweight='bold', color=text_color)
        ax.text(x, y - h*0.2, subtitle, ha='center', va='center', fontsize=13, color='#57606A')
    else:
        ax.text(x, y, title, ha='center', va='center', fontsize=16, fontweight='bold', color=text_color)

def draw_arrow(x1, y1, x2, y2, color='#8C959F', dashed=False, zorder=2):
    ls = '--' if dashed else '-'
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1), 
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5, ls=ls, mutation_scale=15), zorder=zorder)

def draw_arrow_path(pts, color='#8C959F', dashed=False, zorder=2):
    ls = '--' if dashed else '-'
    for i in range(len(pts)-2):
        ax.plot([pts[i][0], pts[i+1][0]], [pts[i][1], pts[i+1][1]], color=color, lw=1.5, ls=ls, zorder=zorder)
    ax.annotate('', xy=pts[-1], xytext=pts[-2], 
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5, ls=ls, mutation_scale=15), zorder=zorder)

# ----------------- 左侧：传统架构绘制 -----------------
lx = 5.5
lw = 7.0
lh = 1.4
ly_step = 2.2
ly_start = 14.9

l_bg = '#E4EEF5'
l_border = '#B3CDE0'

draw_node(lx, ly_start, lw, lh, l_bg, l_border, '静态数据输入', '仅含粉丝数、转发量等浅层一维统计指标')
draw_arrow(lx, ly_start-lh/2, lx, ly_start-ly_step+lh/2)

draw_node(lx, ly_start-ly_step, lw, lh, l_bg, l_border, '手工特征工程', '低维特征向量拼接，缺乏节点间的深层拓扑关系表示')
draw_arrow(lx, ly_start-ly_step-lh/2, lx, ly_start-2*ly_step+lh/2)

draw_node(lx, ly_start-2*ly_step, lw, lh, '#E9ECEF', '#CED4DA', '识别算法层', 'PageRank / 阈值过滤 / 传统机器学习，易陷入局部特征')
draw_arrow(lx, ly_start-2*ly_step-lh/2, lx, ly_start-3*ly_step+lh/2)

draw_node(lx, ly_start-3*ly_step, lw, lh, '#E9ECEF', '#CED4DA', '验证机制', '多数缺乏真实物理演化过程的动态反馈与验证')
draw_arrow(lx, ly_start-3*ly_step-lh/2, lx, ly_start-4*ly_step+lh/2)

draw_node(lx, ly_start-4*ly_step, lw, lh, '#DDE4EB', '#AAB6C4', '最终结果输出', '仅能输出静态、一维的用户重要性排名榜单')


# ----------------- 右侧：本项目架构绘制 -----------------
rx = 14.5
rw = 7.0
rh = 1.4

# 1. 数据层
draw_node(rx, 15.5, rw, lh, '#F1F4F9', '#C5D4E3', '多源开放数据采集与异构图谱构建', 'NLP文本语义提取 + 时序频次赋权，结构化存入Neo4j')
draw_arrow(rx, 15.5-lh/2, rx, 13.5+lh/2, dashed=True)

# 2. 算法核心
draw_node(rx, 13.5, rw, lh, '#E9F5F1', '#A2D9CE', 'GNN 核心智能初筛 (改进 GAT)', '引入注意力机制，自适应聚合高阶拓扑，锁定关键传播通道')

# 3. 验证与寻优复合框
# 外部浅色大框
veri_box_y = 10.65
veri_box_h = 3.1
veri_rect = patches.FancyBboxPatch((rx-rw/2, veri_box_y-veri_box_h/2), rw, veri_box_h, boxstyle='round,pad=0,rounding_size=0.15',
                                   facecolor='#F8F9FA', edgecolor='#D0D7DE', lw=1.2, zorder=1)
ax.add_patch(veri_rect)
ax.text(rx, veri_box_y + 0.95, '复杂网络理论双轨验证与寻优', ha='center', va='center', fontsize=15, fontweight='bold', color='#24292F',
        bbox=dict(facecolor='#F8F9FA', edgecolor='none', pad=2.0), zorder=3)

# 内部双节点
draw_node(rx-1.7, veri_box_y-0.35, 3.0, 1.2, '#FFF4E6', '#F5C6CB', '蚁群算法 (ACO)', '结合 GNN 先验\n避免算力爆炸全局寻优')
draw_node(rx+1.7, veri_box_y-0.35, 3.0, 1.2, '#F3E8FF', '#D1B3FF', '传染病动力学', 'SIR/SIS 模型 MCMC 模拟\n真实级联覆盖率反向验证')

# 箭头连接 GNN 到验证模块 (改为在文本下方分叉，避免线条穿过文字两侧)
ax.plot([rx, rx], [13.5-lh/2, 11.2], color='#8C959F', lw=1.5, zorder=2)
ax.plot([rx-1.7, rx+1.7], [11.2, 11.2], color='#8C959F', lw=1.5, zorder=2)
draw_arrow(rx-1.7, 11.2, rx-1.7, veri_box_y-0.35+0.6, zorder=2)
draw_arrow(rx+1.7, 11.2, rx+1.7, veri_box_y-0.35+0.6, zorder=2)

# 内部模块之间互相虚线连接表示协同 (稍微错开高度避免重叠)
draw_arrow(rx-0.2, veri_box_y-0.3, rx+0.2, veri_box_y-0.3, dashed=True)
draw_arrow(rx+0.2, veri_box_y-0.4, rx-0.2, veri_box_y-0.4, dashed=True)

# 箭头连接验证模块到系统 (改为向下汇聚成单箭头，避免重叠)
ax.plot([rx-1.7, rx-1.7], [veri_box_y-0.35-0.6, 9.3], color='#8C959F', lw=1.5, zorder=2)
ax.plot([rx+1.7, rx+1.7], [veri_box_y-0.35-0.6, 9.3], color='#8C959F', lw=1.5, zorder=2)
ax.plot([rx-1.7, rx+1.7], [9.3, 9.3], color='#8C959F', lw=1.5, zorder=2)
draw_arrow(rx, 9.3, rx, 7.5+lh/2, zorder=2)

# 4. 系统落地层
draw_node(rx, 7.5, rw, lh, '#FEF0E6', '#FAD2A8', '交互式可视化舆情分析系统落地', '模块度解析社区圈层结构，动态前端大屏追踪时序扩散路径')

# 底部分布式数据库图标 (参考原图风格，放在系统下方)
draw_node(rx, 5.5, rw, 1.0, '#E6F0FA', '#A9C4EB', '关键用户实时排行榜与分析报告', '')
draw_arrow(rx, 7.5-lh/2, rx, 5.5+0.5)


# ----------------- 底部说明文字 -----------------
# 左侧说明
# desc_left = "基于模块化的传统特征提取与启发式\n算法，特征维度低、组件紧密耦合，\n缺乏演化物理过程的约束与验证。"
# ax.text(1.5, 1.6, desc_left, ha='left', va='top', fontsize=15, color='#24292F', linespacing=1.8)

# 右侧说明
# desc_right = "基于深度图学习的分布式混合架构，\n具备高维度拓扑提取、动力学双轨\n验证、高可解释性与可视化落地优势。"
# ax.text(10.5, 1.6, desc_right, ha='left', va='top', fontsize=15, color='#24292F', linespacing=1.8)

# 右下角图例
# ax.plot([16, 17], [4.6, 4.6], color='#8C959F', lw=1.5)
# ax.annotate('', xy=(17.2, 4.6), xytext=(17, 4.6), arrowprops=dict(arrowstyle='->', color='#8C959F', lw=1.5, mutation_scale=15))
# ax.text(17.4, 4.6, '数据与演化流', ha='left', va='center', fontsize=13, color='#57606A')

# ax.plot([16, 17], [4.1, 4.1], color='#8C959F', lw=1.5, ls='--')
# ax.annotate('', xy=(17.2, 4.1), xytext=(17, 4.1), arrowprops=dict(arrowstyle='->', color='#8C959F', lw=1.5, ls='--', mutation_scale=15))
# ax.text(17.4, 4.1, '协同约束与控制', ha='left', va='center', fontsize=13, color='#57606A')


plt.tight_layout()
plt.savefig('assets/architecture_comparison_v2.png', dpi=500, bbox_inches='tight')
print("New architecture comparison diagram saved based on reference style.")
