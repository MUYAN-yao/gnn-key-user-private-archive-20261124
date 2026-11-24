import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 任务数据 (任务名, 起始月, 持续月, 所属阶段, 是否为关键里程碑)
tasks_data = [
    # 第一阶段 (月 0-2)
    ("深入调研国内外相关文献", 0, 1, 1, False),
    ("社交媒体数据集获取(Weibo/Twitter)", 0, 1.5, 1, False),
    ("数据清洗、预处理与环境搭建", 1, 1, 1, True), # 产出文档、数据集
    
    # 第二阶段 (月 2-6)
    ("PyTorch框架与基础GNN模型构建", 2, 1.5, 2, False),
    ("注意力机制模块代码编写", 3, 1.5, 2, False),
    ("传染病模型与社区发现算法接入", 4, 1.5, 2, False),
    ("开展多组对比实验(PageRank等)", 5, 1, 2, False),
    ("实验数据记录与算法调优分析", 5.5, 0.5, 2, True), # 产出核心算法库
    
    # 第三阶段 (月 6-9)
    ("系统前后端架构设计", 6, 1, 3, False),
    ("动态图可视化与交互模块开发", 6.5, 1.5, 3, False),
    ("GNN模型封装与前端API对接", 7.5, 1, 3, False),
    ("大规模网络渲染性能优化", 8, 1, 3, False),
    ("系统原型V1.0内部集成测试", 8.5, 0.5, 3, True), # 产出测试版、操作手册
    
    # 第四阶段 (月 9-12)
    ("学术论文撰写与高水平期刊投稿", 9, 2, 4, False),
    ("实验日志整理与项目报告撰写", 10, 1.5, 4, False),
    ("结题答辩PPT制作与排练", 11, 1, 4, False),
    ("项目正式结题与成果验收", 11.5, 0.5, 4, True) # 软著证书、结题报告
]

colors = {
    1: '#8FB4DC', # 浅蓝
    2: '#70CDBE', # 浅绿
    3: '#F5AA61', # 浅橙
    4: '#AC99D2'  # 浅紫
}

phase_names = {
    1: "阶段一：需求分析与数据准备",
    2: "阶段二：核心算法设计与调优",
    3: "阶段三：系统开发与集成测试",
    4: "阶段四：成果凝练与结题答辩"
}

tasks_data.reverse()
n_tasks = len(tasks_data)

fig, ax = plt.subplots(figsize=(19.3, 9.5))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

table_right = 0
table_mid = -3.8
table_left = -7.3
header_top = n_tasks + 0.8
header_y = n_tasks + 0.15

# 添加大标题
fig.suptitle("基于GNN的关键用户识别项目 — 年度实施甘特图", fontsize=26, fontweight='bold', y=0.95)

# 绘制交替且分阶段的行背景 (仅在任务和甘特图区域)
for i, task in enumerate(tasks_data):
    phase = task[3]
    color = colors[phase]
    row_alpha = 0.25 if i % 2 == 0 else 0.10
    ax.add_patch(patches.Rectangle((table_mid, i - 0.5), 12 - table_mid, 1.0, 
                                   facecolor=color, alpha=row_alpha, zorder=0, lw=0, clip_on=False))

# 绘制表头背景色
ax.add_patch(patches.Rectangle((table_left, n_tasks - 0.5), 12 - table_left, header_top - (n_tasks - 0.5), 
                               facecolor='#F4F6F9', zorder=0, lw=0, clip_on=False))

# 绘制甘特图条块
bar_height = 0.5
for i, (name, start, dur, phase, is_milestone) in enumerate(tasks_data):
    color = colors[phase]
    
    # 绘制无边框的矩形
    rect = patches.Rectangle((start, i - bar_height/2), dur, bar_height, 
                             facecolor=color, linewidth=0, zorder=3,
                             alpha=0.95)
    ax.add_patch(rect)

# ================== 左侧总分结构表格 ==================
phase_groups = {1:[], 2:[], 3:[], 4:[]}
for i, task in enumerate(tasks_data):
    phase_groups[task[3]].append(i)

# 关闭默认Y轴标签
ax.set_yticks([])
ax.set_yticklabels([])

dark_colors = {
    1: '#6289B8', 
    2: '#47A293', 
    3: '#D18844', 
    4: '#8C77B8'
}
header_line_color = '#A0A0A0'

# 最顶部分隔线 (加粗)
ax.plot([table_left, 12], [header_top, header_top], color=header_line_color, lw=2.0, clip_on=False)
# 表头下方分隔线
ax.plot([table_left, 12], [n_tasks - 0.5, n_tasks - 0.5], color=dark_colors[1], lw=2.0, clip_on=False)
# 底部分隔线 (加粗)
ax.plot([table_left, 12], [-0.5, -0.5], color=dark_colors[4], lw=2.0, clip_on=False)

# 绘制表头文本
ax.text((table_left + table_mid)/2, header_y, "研究阶段", ha='center', va='center', 
        fontsize=16, fontweight='bold', color='#222222', clip_on=False)
ax.text(table_mid + 0.3, header_y, "具体行动方案与任务", ha='left', va='center', 
        fontsize=16, fontweight='bold', color='#222222', clip_on=False)

# 手动绘制甘特图时间轴表头
months = ['26年4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月', '27年1月', '2月', '3月']
for m_idx, m_str in enumerate(months):
    ax.text(m_idx + 0.5, header_y, m_str, ha='center', va='center', fontsize=14, fontweight='bold', color='#222222', clip_on=False)

# 绘制表头内的月份分隔线
for m_idx in range(1, 12):
    ax.plot([m_idx, m_idx], [n_tasks - 0.5, header_top], color='#CCCCCC', lw=1.0, clip_on=False)

for i, task in enumerate(tasks_data):
    # 所有任务名字体样式统一（不区分是否为里程碑）
    fw = 'normal'
    color = '#333333'
    ax.text(table_mid + 0.3, i, task[0], ha='left', va='center', fontsize=14, fontweight=fw, color=color, clip_on=False)
    
    # 每行任务下方的水平线
    if i > 0:  # 避开底部线
        is_phase_boundary = False
        for p in [1, 2, 3, 4]:
            if i - 1 == max(phase_groups[p]):
                is_phase_boundary = True
                break
        
        if is_phase_boundary:
            p_above = next(p for p in [1, 2, 3, 4] if i - 1 == max(phase_groups[p]))
            ax.plot([table_left, 12], [i - 0.5, i - 0.5], color=dark_colors[p_above], lw=2.0, clip_on=False)
        else:
            ax.plot([table_left, 12], [i - 0.5, i - 0.5], color='#E0E0E0', lw=1.0, linestyle='-', clip_on=False)

# 画阶段的文字和背景
for p in [1, 2, 3, 4]:
    idx_list = phase_groups[p]
    min_idx, max_idx = min(idx_list), max(idx_list)
    mid_idx = (min_idx + max_idx) / 2
    
    # 绘制当前阶段的背景色
    ax.add_patch(patches.Rectangle((table_left, min_idx - 0.5), table_mid - table_left, max_idx - min_idx + 1.0, 
                                   facecolor=colors[p], alpha=0.35, zorder=0, lw=0, clip_on=False))
    
    phase_short = [
        "第一阶段：\n需求分析与数据准备\n（第1-2个月）", 
        "第二阶段：\n核心算法设计与模型调优\n（第3-6个月）", 
        "第三阶段：\n系统原型开发与集成测试\n（第7-9个月）", 
        "第四阶段：\n成果凝练与\n结题答辩准备\n（第10-12个月）"
    ][p-1]
    ax.text((table_left + table_mid)/2, mid_idx, phase_short, ha='center', va='center', 
            fontsize=15, fontweight='bold', color='#222222', clip_on=False)

# 画表头区域的垂直线
ax.plot([table_left, table_left], [n_tasks - 0.5, header_top], color=header_line_color, lw=2.0, clip_on=False)
ax.plot([table_mid, table_mid], [n_tasks - 0.5, header_top], color=header_line_color, lw=2.0, clip_on=False)
ax.plot([table_right, table_right], [n_tasks - 0.5, header_top], color=header_line_color, lw=2.0, clip_on=False)
ax.plot([12, 12], [n_tasks - 0.5, header_top], color=header_line_color, lw=2.0, clip_on=False)

# 画各个阶段区域的垂直线
for p in [1, 2, 3, 4]:
    idx_list = phase_groups[p]
    min_idx, max_idx = min(idx_list), max(idx_list)
    
    ax.plot([table_left, table_left], [min_idx - 0.5, max_idx + 0.5], color=dark_colors[p], lw=2.0, clip_on=False)
    ax.plot([table_mid, table_mid], [min_idx - 0.5, max_idx + 0.5], color=dark_colors[p], lw=2.0, clip_on=False)
    ax.plot([table_right, table_right], [min_idx - 0.5, max_idx + 0.5], color=dark_colors[p], lw=2.0, clip_on=False)
    ax.plot([12, 12], [min_idx - 0.5, max_idx + 0.5], color=dark_colors[p], lw=2.0, clip_on=False)

# 调整左侧边距，为表格留出空间，顶部增加边距以容纳表头
plt.subplots_adjust(left=0.38, top=0.82, bottom=0.1, right=0.98)

# ================== 调整X轴到上方并隐藏不需要的边框 ==================
# X轴设置 (仅保留主网格逻辑)
ax.set_xticks(np.arange(13), minor=True)

# 隐藏X轴/Y轴的短刻度线与标签
ax.tick_params(axis='y', which='both', left=False)
ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False, labeltop=False)
ax.set_xticks([]) # 完全关闭x轴刻度标签

# 绘制网格辅助线（垂直线，对应月份分割）
ax.grid(which='minor', axis='x', linestyle=':', color='#999999', zorder=1, linewidth=1.5)

# 隐藏全部边框 (黑框)
for spine in ax.spines.values():
    spine.set_visible(False)

ax.set_xlim(table_left, 12)
ax.set_ylim(-0.5, n_tasks - 0.5)

# 图例已删除

plt.subplots_adjust(left=0.02, top=0.82, bottom=0.05, right=0.98)
plt.savefig('assets/project_gantt_chart_academic.png', dpi=500, bbox_inches='tight')
print("科研级学术风甘特图已生成并保存为 assets/project_gantt_chart_academic.png！")
