import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# ================= 画布调整：减少高度，紧凑算法层 =================
# 减少层间留白：算法层下移25，数据层下移50
fig, ax = plt.subplots(figsize=(26, 12.8)) 
ax.set_xlim(0, 2000) 
ax.set_ylim(0, 1000)  
ax.axis('off')
fig.patch.set_facecolor('white')

def darken_color(hex_color, factor=0.65):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f'#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}'

DATA_LINE = '#5C7B96'
ALGO_LINE = '#4A7A6A'
APP_LINE  = '#8C5A31'

def draw_box(x, y, w, h, text, bg_color, font_size=18, title='', title_size=20, rx=10, text_color='#222222', title_color='#111111', offset_y=0, title_offset_y=0, edge_color=None, font_weight='normal'):
    if edge_color is None:
        edge_color = darken_color(bg_color)
        
    shadow = patches.FancyBboxPatch((x+5, y-5), w, h, boxstyle=f'round,pad=0,rounding_size={rx}',
                                    linewidth=0, facecolor='#000000', alpha=0.15)
    ax.add_patch(shadow)
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle=f'round,pad=0,rounding_size={rx}',
                                  linewidth=2.0, edgecolor=edge_color, facecolor=bg_color)
    ax.add_patch(rect)
    cy = y + h/2 + offset_y
    if title:
        ax.text(x + w/2, y + h - 35 + offset_y + title_offset_y, title, ha='center', va='center', fontsize=title_size, fontweight='bold', color=title_color)
        cy -= 18
    if text:
        ax.text(x + w/2, cy, text, ha='center', va='center', fontsize=font_size, fontweight=font_weight, color=text_color, wrap=True)

def draw_line(x1, y1, x2, y2, color='#333333', arrow=True):
    if arrow:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='-|>', lw=2.8, color=color, mutation_scale=25))
    else:
        ax.plot([x1, x2], [y1, y2], color=color, lw=2.8)

def draw_line_path(points, color='#333333'):
    for i in range(len(points)-2):
        ax.plot([points[i][0], points[i+1][0]], [points[i][1], points[i+1][1]], color=color, lw=2.8)
    ax.annotate('', xy=points[-1], xytext=points[-2], arrowprops=dict(arrowstyle='-|>', lw=2.8, color=color, mutation_scale=25))

def draw_thick_arrow(x1, y1, x2, y2, color, edge_color=None):
    if edge_color is None:
        edge_color = darken_color(color, 0.7)
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(facecolor=color, edgecolor=edge_color, width=16, headwidth=32, headlength=32, shrink=0.05, linewidth=1.8))

def draw_community_clusters(cx, cy, scale=1.0):
    # Background blobs 
    blob_b = patches.Circle((cx-30*scale, cy), 35*scale, facecolor='#E3EFF8', edgecolor='none', alpha=0.9)
    blob_y = patches.Circle((cx+35*scale, cy+30*scale), 28*scale, facecolor='#FDF3E1', edgecolor='none', alpha=0.9)
    blob_o = patches.Circle((cx+35*scale, cy-30*scale), 28*scale, facecolor='#FBE7E1', edgecolor='none', alpha=0.9)
    ax.add_patch(blob_b)
    ax.add_patch(blob_y)
    ax.add_patch(blob_o)
    
    # Nodes
    b_nodes = [(cx-30*scale, cy+18*scale), (cx-50*scale, cy+8*scale), (cx-45*scale, cy-15*scale), 
               (cx-25*scale, cy-10*scale), (cx-10*scale, cy+8*scale), (cx-15*scale, cy-25*scale)]
    y_nodes = [(cx+35*scale, cy+45*scale), (cx+20*scale, cy+30*scale), (cx+50*scale, cy+30*scale), (cx+35*scale, cy+15*scale)]
    o_nodes = [(cx+35*scale, cy-15*scale), (cx+20*scale, cy-30*scale), (cx+50*scale, cy-30*scale), (cx+35*scale, cy-45*scale)]
    
    # Edges
    edges = [
        # Blue
        (b_nodes[0], b_nodes[1]), (b_nodes[1], b_nodes[2]), (b_nodes[2], b_nodes[3]), 
        (b_nodes[3], b_nodes[4]), (b_nodes[4], b_nodes[0]), (b_nodes[0], b_nodes[3]),
        (b_nodes[3], b_nodes[5]), (b_nodes[2], b_nodes[5]),
        # Yellow
        (y_nodes[0], y_nodes[1]), (y_nodes[0], y_nodes[2]), (y_nodes[1], y_nodes[3]), (y_nodes[2], y_nodes[3]), (y_nodes[1], y_nodes[2]),
        # Orange
        (o_nodes[0], o_nodes[1]), (o_nodes[0], o_nodes[2]), (o_nodes[1], o_nodes[3]), (o_nodes[2], o_nodes[3]), (o_nodes[1], o_nodes[2]),
        # Inter-cluster
        (b_nodes[4], y_nodes[1]), (b_nodes[3], o_nodes[1])
    ]
    
    for e in edges:
        ax.plot([e[0][0], e[1][0]], [e[0][1], e[1][1]], color=ALGO_LINE, lw=2.0*scale)
        
    for n in b_nodes:
        ax.add_patch(patches.Circle(n, radius=5.5*scale, facecolor='#7CB0E2', edgecolor=darken_color('#7CB0E2'), lw=1.8*scale, zorder=3))
    for n in y_nodes:
        ax.add_patch(patches.Circle(n, radius=5.5*scale, facecolor='#F5B341', edgecolor=darken_color('#F5B341'), lw=1.8*scale, zorder=3))
    for n in o_nodes:
        ax.add_patch(patches.Circle(n, radius=5.5*scale, facecolor='#ED7853', edgecolor=darken_color('#ED7853'), lw=1.8*scale, zorder=3))

def draw_cylinder(x, y, w, h, bg_color, edge_color=None):
    if edge_color is None:
        edge_color = darken_color(bg_color)
    shadow = patches.Rectangle((x+5, y-5), w, h, linewidth=0, facecolor='#000000', alpha=0.15)
    ax.add_patch(shadow)
    
    rect = patches.Rectangle((x, y), w, h, linewidth=2.0, edgecolor=edge_color, facecolor=bg_color)
    ax.add_patch(rect)
    
    bottom_oval = patches.Ellipse((x+w/2, y), w, h*0.2, linewidth=2.0, edgecolor=edge_color, facecolor=bg_color)
    top_oval = patches.Ellipse((x+w/2, y+h), w, h*0.2, linewidth=2.0, edgecolor=edge_color, facecolor=bg_color)
    ax.add_patch(bottom_oval)
    ax.add_patch(top_oval)

def draw_ranking_icon(cx, cy, scale=1.0):
    # 排行榜底座
    # 左边底座(青色)
    ax.add_patch(patches.FancyBboxPatch((cx-21*scale, cy-15*scale), 14*scale, 18*scale, boxstyle='round,pad=0,rounding_size=2', facecolor='#84D2C5', edgecolor='#333', lw=1.8*scale))
    # 右边底座(紫色)
    ax.add_patch(patches.FancyBboxPatch((cx+7*scale, cy-15*scale), 14*scale, 15*scale, boxstyle='round,pad=0,rounding_size=2', facecolor='#B59CD9', edgecolor='#333', lw=1.8*scale))
    # 中间最高底座(橙色)
    ax.add_patch(patches.FancyBboxPatch((cx-7*scale, cy-15*scale), 14*scale, 25*scale, boxstyle='round,pad=0,rounding_size=2', facecolor='#F6B676', edgecolor='#333', lw=1.8*scale))
    
    # 绘制星星的函数
    def _draw_star(sx, sy, r, c='#F9D371'):
        star_points = [(sx, sy+r), (sx+r*0.3, sy+r*0.3), (sx+r*0.95, sy+r*0.3), 
                       (sx+r*0.45, sy-r*0.1), (sx+r*0.6, sy-r*0.8), 
                       (sx, sy-r*0.4), (sx-r*0.6, sy-r*0.8), (sx-r*0.45, sy-r*0.1), 
                       (sx-r*0.95, sy+r*0.3), (sx-r*0.3, sy+r*0.3)]
        star = patches.Polygon(star_points, closed=True, facecolor=c, edgecolor='#333', lw=1.8*scale)
        ax.add_patch(star)

    # 三颗星星
    _draw_star(cx, cy+22*scale, 9*scale)      # 中间大星
    _draw_star(cx-14*scale, cy+8*scale, 5.5*scale)  # 左边小星
    _draw_star(cx+14*scale, cy+8*scale, 5.5*scale)  # 右边小星

def draw_clapperboard_icon(cx, cy, scale=1.0):
    # 场记板主板
    ax.add_patch(patches.FancyBboxPatch((cx-20*scale, cy-15*scale), 40*scale, 26*scale, boxstyle='round,pad=0,rounding_size=3', facecolor='#A9BFE4', edgecolor='#333', lw=2.0*scale))
    
    # 场记板上方条纹板 (底部黑白相间条纹)
    # 利用旋转来画倾斜的条纹板
    import matplotlib.transforms as transforms
    ts = ax.transData
    tr = transforms.Affine2D().rotate_deg_around(cx-20*scale, cy+13*scale, 15)
    t = tr + ts
    
    # 画上方条纹板底板
    ax.add_patch(patches.FancyBboxPatch((cx-20*scale, cy+11*scale), 40*scale, 8*scale, boxstyle='round,pad=0,rounding_size=2', facecolor='#fff', edgecolor='#333', lw=2.0*scale, transform=t))
    
    # 画上方条纹板的黑色条纹
    ax.add_patch(patches.Polygon([(cx-16*scale, cy+11*scale), (cx-8*scale, cy+11*scale), (cx-4*scale, cy+19*scale), (cx-12*scale, cy+19*scale)], closed=True, facecolor='#333', edgecolor='#333', transform=t))
    ax.add_patch(patches.Polygon([(cx-2*scale, cy+11*scale), (cx+6*scale, cy+11*scale), (cx+10*scale, cy+19*scale), (cx+2*scale, cy+19*scale)], closed=True, facecolor='#333', edgecolor='#333', transform=t))
    ax.add_patch(patches.Polygon([(cx+12*scale, cy+11*scale), (cx+20*scale, cy+11*scale), (cx+24*scale, cy+19*scale), (cx+16*scale, cy+19*scale)], closed=True, facecolor='#333', edgecolor='#333', transform=t))
    
    # 底部固定条纹板
    ax.add_patch(patches.FancyBboxPatch((cx-20*scale, cy+3*scale), 40*scale, 8*scale, boxstyle='round,pad=0,rounding_size=1', facecolor='#fff', edgecolor='#333', lw=2.0*scale))
    ax.add_patch(patches.Polygon([(cx-16*scale, cy+3*scale), (cx-8*scale, cy+3*scale), (cx-4*scale, cy+11*scale), (cx-12*scale, cy+11*scale)], closed=True, facecolor='#333', edgecolor='#333'))
    ax.add_patch(patches.Polygon([(cx-2*scale, cy+3*scale), (cx+6*scale, cy+3*scale), (cx+10*scale, cy+11*scale), (cx+2*scale, cy+11*scale)], closed=True, facecolor='#333', edgecolor='#333'))
    ax.add_patch(patches.Polygon([(cx+12*scale, cy+3*scale), (cx+20*scale, cy+3*scale), (cx+24*scale, cy+11*scale), (cx+16*scale, cy+11*scale)], closed=True, facecolor='#333', edgecolor='#333'))

    # 中心播放按钮
    play_points = [(cx-5*scale, cy-8*scale), (cx-5*scale, cy+1*scale), (cx+6*scale, cy-3.5*scale)]
    play = patches.Polygon(play_points, closed=True, facecolor='#F6CBA3', edgecolor='#333', lw=1.5*scale)
    ax.add_patch(play)

def draw_weibo_icon(cx, cy, scale=1.0):
    # 微博底色圆和波纹
    ax.add_patch(patches.Circle((cx-4*scale, cy-4*scale), 15*scale, facecolor='#E6162D', edgecolor='none', zorder=3))
    ax.add_patch(patches.Arc((cx-4*scale, cy-4*scale), 40*scale, 40*scale, angle=0, theta1=0, theta2=85, color='#E6162D', lw=4*scale, capstyle='round', zorder=3))
    ax.add_patch(patches.Arc((cx-4*scale, cy-4*scale), 58*scale, 58*scale, angle=0, theta1=0, theta2=80, color='#E6162D', lw=4*scale, capstyle='round', zorder=3))
    # 眼睛
    ax.add_patch(patches.Ellipse((cx-4*scale, cy-4*scale), 18*scale, 11*scale, facecolor='white', edgecolor='none', zorder=4))
    ax.add_patch(patches.Circle((cx-4*scale, cy-4*scale), 4*scale, facecolor='black', edgecolor='none', zorder=5))
    ax.add_patch(patches.Circle((cx-5.5*scale, cy-2.5*scale), 1.5*scale, facecolor='white', edgecolor='none', zorder=6))

def draw_twitter_icon(cx, cy, scale=1.0):
    c = '#1DA1F2'
    # 简易 Twitter 鸟
    ax.add_patch(patches.Circle((cx-2*scale, cy-4*scale), 12*scale, facecolor=c, edgecolor='none', zorder=3)) # 身体
    ax.add_patch(patches.Circle((cx+10*scale, cy+6*scale), 8*scale, facecolor=c, edgecolor='none', zorder=3))  # 头部
    ax.add_patch(patches.Polygon([(cx+14*scale, cy+6*scale), (cx+24*scale, cy+8*scale), (cx+16*scale, cy+2*scale)], facecolor=c, edgecolor='none', zorder=3)) # 喙
    # 尾巴
    ax.add_patch(patches.Polygon([(cx-10*scale, cy-6*scale), (cx-24*scale, cy-10*scale), (cx-10*scale, cy-16*scale)], facecolor=c, edgecolor='none', zorder=3))
    # 翅膀 (用白色椭圆切掉一部分，再叠加一个蓝色多边形或椭圆)
    ax.add_patch(patches.Ellipse((cx-6*scale, cy+8*scale), 18*scale, 8*scale, angle=30, facecolor=c, edgecolor='none', zorder=4))
    
def draw_api_cloud(cx, cy, scale=1.0):
    color = '#357ABD'
    # 云朵圆圈
    ax.add_patch(patches.Circle((cx, cy+3*scale), 12*scale, facecolor=color, edgecolor='none', zorder=3))
    ax.add_patch(patches.Circle((cx-10*scale, cy-3*scale), 9*scale, facecolor=color, edgecolor='none', zorder=3))
    ax.add_patch(patches.Circle((cx+10*scale, cy-3*scale), 9*scale, facecolor=color, edgecolor='none', zorder=3))
    # 云朵底部
    ax.add_patch(patches.Rectangle((cx-10*scale, cy-12*scale), 20*scale, 12*scale, facecolor=color, edgecolor='none', zorder=3))
    # API文字
    ax.text(cx, cy-3*scale, 'API', ha='center', va='center', fontsize=18*scale, fontweight='bold', color='white', zorder=4)

# ================= 背景分层 =================
# 应用层 (y 保持不变)
rect = patches.FancyBboxPatch((50, 40), 1900, 230, boxstyle='round,pad=0,rounding_size=12',
                              linewidth=2.0, edgecolor='#A67B5B', facecolor='#FEF6EE', linestyle='--')
ax.add_patch(rect)
ax.plot([250, 250], [40, 270], color='#A67B5B', lw=2.0, linestyle=':')
ax.text(150, 175, '应用层', ha='center', va='center', fontsize=34, fontweight='bold', color='#5C3A21')
ax.text(150, 115, '系统开发\n与成果展示', ha='center', va='center', fontsize=20, fontweight='bold', color='#8C5A31')

# 算法层 (y 从 310 降到 285)
rect = patches.FancyBboxPatch((50, 285), 1900, 410, boxstyle='round,pad=0,rounding_size=12',
                              linewidth=2.0, edgecolor='#6D9E8F', facecolor='#F0FAF6', linestyle='--')
ax.add_patch(rect)
ax.plot([250, 250], [285, 695], color='#6D9E8F', lw=2.0, linestyle=':')
ax.text(150, 520, '算法层', ha='center', va='center', fontsize=34, fontweight='bold', color='#2C4035')
ax.text(150, 460, '算法模型\n与核心研究', ha='center', va='center', fontsize=20, fontweight='bold', color='#2C4035')

# 数据层 (y 从 760 降到 710)
rect = patches.FancyBboxPatch((50, 710), 1900, 250, boxstyle='round,pad=0,rounding_size=12',
                              linewidth=2.0, edgecolor='#7F9EB5', facecolor='#F0F6FA', linestyle='--')
ax.add_patch(rect)
ax.plot([250, 250], [710, 960], color='#7F9EB5', lw=2.0, linestyle=':')
ax.text(150, 865, '数据层', ha='center', va='center', fontsize=34, fontweight='bold', color='#2C3E50')
ax.text(150, 805, '数据采集\n与预处理', ha='center', va='center', fontsize=20, fontweight='bold', color='#2C3E50')


# ================= 第一层：数据层 =================
draw_box(300, 737.5, 400, 195, '', '#ffffff', title='多源公开数据合规采集', title_size=24, offset_y=15, title_offset_y=-10, edge_color='#7F9EB5')
draw_weibo_icon(380, 825, scale=1.4)
ax.text(380, 785, 'Weibo', ha='center', va='center', fontsize=22, color='#111')

draw_twitter_icon(500, 825, scale=1.4)
ax.text(500, 785, 'Twitter', ha='center', va='center', fontsize=22, color='#111')

draw_api_cloud(620, 825, scale=1.4)
ax.text(620, 785, 'API', ha='center', va='center', fontsize=22, color='#111')


# Neo4j Cylinder
draw_cylinder(830, 767.5, 180, 135, '#B1CDEB') 
ax.text(920, 845, 'Neo4j', ha='center', va='center', fontsize=34, fontweight='bold', color='#111')
ax.text(920, 790, '图数据库', ha='center', va='center', fontsize=22, fontweight='bold', color='#333')

# Data Cleaning
draw_box(1140, 737.5, 760, 195, '', '#ffffff', title='数据清洗与多维特征工程', title_size=24, offset_y=15, title_offset_y=-10, edge_color='#7F9EB5')
ax.text(1310, 855, 'pandas', ha='center', va='center', fontsize=32, fontweight='bold', color='#150458')
ax.text(1310, 780, 'NetworkX', ha='center', va='center', fontsize=30, fontweight='bold', color='#428B36')
draw_box(1470, 825, 410, 50, 'BERT 深度语义特征提取', '#F0F5FA', rx=6, font_size=20)
draw_box(1470, 760, 410, 50, '时序交互频次计算图谱边权重', '#F0F5FA', rx=6, font_size=20)

# Data internal connections 
draw_line(700, 835, 830, 835, color=DATA_LINE)
draw_line(1140, 835, 1010, 835, color=DATA_LINE)

# ================= 第二层：算法层 =================
draw_box(330, 570, 150, 65, 'DeepInf', '#96BBE0', font_size=20, font_weight='bold')
draw_box(330, 457.5, 150, 65, 'BiGCN', '#FCE198', font_size=20, font_weight='bold')
draw_box(330, 345, 150, 65, 'GLIE', '#94D3C5', font_size=20, font_weight='bold')

# GAT框
draw_box(580, 370, 260, 240, '', '#74CDAE', title='引入注意力机制的', title_size=26, offset_y=-5, title_offset_y=-25)
ax.text(710, 505, '改进 GAT 模型', ha='center', va='center', fontsize=26, fontweight='bold', color='#111')
ax.text(710, 440, '(自适应学习交互权重)\n精准锁定传播通道', ha='center', va='center', fontsize=18, fontweight='bold', color='#222')

# Scores框
draw_box(920, 430, 160, 120, '关键影响力\n得分', '#CCDFF1', font_size=26, rx=10, font_weight='bold')

# 分支文字
# 放到线条的上方居中 (线条是从 1100 到 1280，中心在 1190)
ax.text(1190, 580, '动态传播验证', ha='center', va='center', fontsize=21, fontweight='bold', color='#333')
ax.text(1190, 430, '网络启发寻优', ha='center', va='center', fontsize=21, fontweight='bold', color='#333')

# SIR模块
draw_box(1280, 495, 340, 140, '', '#96BBE0', title='SIR/SIS 传染病动力学', title_size=24)
draw_box(1305, 515, 135, 55, 'MCMC模拟', '#EBF3FA', rx=6, font_size=20)
draw_box(1460, 515, 135, 55, '传播覆盖率', '#EBF3FA', rx=6, font_size=20)

# ACO模块
draw_box(1280, 345, 340, 140, '', '#8ED1C1', title='蚁群优化算法 (ACO)', title_size=24)
draw_box(1305, 365, 290, 55, 'GNN 表征先验辅助全局寻优', '#E6F5F0', rx=6, font_size=20)

# Community 模块
draw_box(1670, 310, 190, 360, '', '#F1F8F5', title='网络社区发现', title_size=24)

# 网络社区图标
draw_community_clusters(1765, 555, scale=0.95)

# 底部文字块
draw_box(1690, 435, 150, 40, 'Louvain / InfoMap', '#E0F0E9', rx=5, font_size=15)
draw_box(1690, 385, 150, 40, '极化 / 回音室效应', '#E0F0E9', rx=5, font_size=15)
draw_box(1690, 335, 150, 40, '结构洞 / 跨圈层桥接', '#E0F0E9', rx=5, font_size=15)

# ================= Algo internal lines =================
# Neo4j to GAT 折线连接
# 垂直跨越: 767.5 - 610 = 157.5
# 中间折返点在 (767.5+610)/2 = 688.75
draw_line(920, 767.5, 920, 688.75, color=DATA_LINE, arrow=False)
draw_line(920, 688.75, 710, 688.75, color=DATA_LINE, arrow=False)
draw_line(710, 688.75, 710, 610, color=DATA_LINE, arrow=True)

# Scores to App 交互式系统折线连接
# 垂直跨越: 430 - 245 = 185
# 中间折返点在 (430+245)/2 = 337.5
draw_line(1000, 430, 1000, 337.5, color=ALGO_LINE, arrow=False)
draw_line(1000, 337.5, 880, 337.5, color=ALGO_LINE, arrow=False)
draw_line(880, 337.5, 880, 245, color=ALGO_LINE, arrow=True)

# 左侧三个模型汇聚成一条线进入 GAT
draw_line(480, 602.5, 520, 602.5, color=ALGO_LINE, arrow=False) 
draw_line(480, 490, 520, 490, color=ALGO_LINE, arrow=False) 
draw_line(480, 377.5, 520, 377.5, color=ALGO_LINE, arrow=False) 
draw_line(520, 377.5, 520, 602.5, color=ALGO_LINE, arrow=False) # 竖线
draw_line(520, 490, 580, 490, color=ALGO_LINE, arrow=True)    # 汇聚后的单箭头

draw_line(840, 490, 920, 490, color=ALGO_LINE) 

# 拐角线 
# 改为先竖线再横线并带箭头指向模块
draw_line(1080, 490, 1100, 490, color=ALGO_LINE, arrow=False)
draw_line(1100, 490, 1100, 565, color=ALGO_LINE, arrow=False)
draw_line(1100, 565, 1280, 565, color=ALGO_LINE, arrow=True)

draw_line(1100, 490, 1100, 415, color=ALGO_LINE, arrow=False)
draw_line(1100, 415, 1280, 415, color=ALGO_LINE, arrow=True)

# 直线连接到 Community 
draw_line(1620, 565, 1670, 565, color=ALGO_LINE) 
draw_line(1620, 415, 1670, 415, color=ALGO_LINE) 

# ================= 第三层：应用层 =================
# 交互式可视化与舆情分析系统 背景框
shadow = patches.FancyBboxPatch((460+5, 65-5), 840, 180, boxstyle='round,pad=0,rounding_size=10', linewidth=0, facecolor='#000000', alpha=0.15)
ax.add_patch(shadow)
rect = patches.FancyBboxPatch((460, 65), 840, 180, boxstyle='round,pad=0,rounding_size=10', linewidth=2.0, edgecolor=darken_color('#F8B677'), facecolor='#F8B677')
ax.add_patch(rect)
ax.text(460 + 840/2, 65 + 180 - 35, '交互式可视化与舆情分析系统', ha='center', va='center', fontsize=32, fontweight='bold', color='#111')

draw_box(520, 85, 320, 85, '(D3.js / ECharts / AntV)', '#FDE198', title='前端渲染大屏', title_size=24, rx=8, font_size=18, offset_y=-8, title_offset_y=5)
draw_box(920, 85, 320, 85, '(预训练 GNN API 服务)', '#FDE198', title='后端在线推理', title_size=24, rx=8, font_size=18, offset_y=-8, title_offset_y=5)

draw_box(1340, 155, 400, 70, '    关键用户实时排行榜', '#FDECDA', font_size=26, rx=10)
draw_box(1340, 70, 400, 70, '    信息传播路径时序回放', '#FDECDA', font_size=26, rx=10)

# 排行榜图标 (替换了原来的星号图标)
draw_ranking_icon(1375, 185, scale=0.85)

# 播放图标 (替换为场记板)
draw_clapperboard_icon(1375, 105, scale=0.85)

# App internal lines 
draw_line(1300, 190, 1340, 190, color=APP_LINE)
draw_line(1300, 105, 1340, 105, color=APP_LINE)

plt.tight_layout()
plt.savefig('assets/technical_route_final_masterpiece.png', dpi=600, bbox_inches='tight')
print('Chart meticulously updated: reduced white spaces between layers.')