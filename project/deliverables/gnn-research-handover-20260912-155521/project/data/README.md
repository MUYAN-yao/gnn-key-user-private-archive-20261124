# 真实数据目录

`raw/` 存放从原始发布方下载的文件，不应提交至公开代码仓库；`processed/` 存放可由脚本再生成的平台数据包。

## Higgs Twitter

- 发布方：SNAP / Stanford；页面：<https://snap.stanford.edu/data/higgs-twitter.html>
- 使用文件：`higgs-activity_time.txt.gz`
- 原始字段：行为发起用户、目标用户、Unix 时间、互动类型（RT/MT/RE）
- 转换命令：`python scripts/prepare_higgs_twitter.py`

转换脚本将目标用户视为潜在信息源，得到 `target -> actor` 的时序边。由于原始发布不提供原始帖子或话题级级联 ID，`cascades.csv` 的小时分组仅服务于界面追踪，不能作为完整级联真值。论文实验必须在数据卡中披露这一限制。
