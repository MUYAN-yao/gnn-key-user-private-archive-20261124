# 候选截断评估：数据准入台账

日期：2026-09-20；版本 0.1。候选状态仅基于可见的第一方页面核对；准入记录
另须具备已保存的原始归档、哈希和字段核验。

**修订记录（2026-09-20）：** 以下 SocioPatterns 记录已完成第一方条款、
下载、SHA-256 和字段核验，因此其状态与早期候选不同：它们可用于本项目的
模拟 IC 确认层，但不能被表述为已观察到的信息级联。

## 准入规则

每个确认层网络必须同时具备：

1. 第一方或原始作者可访问来源；
2. 明确显示的可用于本研究及发表的条款/许可，或可保存的作者授权；
3. 节点、边、方向、时间字段的明确语义；
4. 下载后可记录原始文件 SHA-256、下载日期和完整处理脚本；
5. 规模经不读取方法效用的 full-baseline 资源预检确认可行。

页面展示的**软件**许可证不自动适用于页面上提供的**数据**。缺少第 2 项时，
状态保持 `terms_unverified_not_admitted`。

## 候选记录

| ID | 第一方页面 | 字段/语义核验 | 可见数据条款 | 当前状态 | 允许用途 |
| --- | --- | --- | --- | --- | --- |
| CollegeMsg | [SNAP](https://snap.stanford.edu/data/CollegeMsg.html) | `SRC DST UNIXTS`；UC Irvine 在线社交网络中的有向私信事件；1,899 节点、59,835 temporal edges。 | 数据页未显示独立数据许可证；SNAP 软件 BSD 许可证不适用作数据许可依据。 | `terms_unverified_not_admitted` | 可作候选，不下载、不运行。 |
| email-Eu-core-temporal | [SNAP](https://snap.stanford.edu/data/email-Eu-core-temporal.html) | `SRC DST TS`；匿名机构成员间有向邮件事件；986 节点、332,334 temporal edges。 | 数据页未显示独立数据许可证；同上。 | `terms_unverified_not_admitted` | 可作候选，不下载、不运行。 |
| sx-mathoverflow | [SNAP temporal catalogue](https://snap.stanford.edu/data/) | catalogue 说明为有向时间评论/提问/回答网络；需要在单独数据页核验具体格式、来源和条款。 | 未核验。 | `source_terms_fields_unverified` | 不下载、不运行。 |
| soc-sign-bitcoin-otc | [SNAP temporal catalogue](https://snap.stanford.edu/data/) | catalogue 说明为有向、加权、带符号、时间的 web-of-trust 网络；其边不是通信或传播事件。 | 未核验。 | `source_terms_fields_unverified` | 仅可作为拓扑敏感性候选；不作为传播行为验证。 |
| SocialBursts Cannes2013 | [原始作者公开仓库](https://github.com/manlius/SocialBursts) | README 声明每条临时活动记录为 `nodeFrom nodeTo timestamp interaction`，方向明确，用户匿名；RT/MT/RE 字段需按研究目的解释。 | 仓库页面称每个数据集附带许可证，但许可证在压缩包内；完整下载和包内条款尚未核验。 | `archive_license_unverified_not_admitted` | 可作高价值候选；在完整下载、SHA-256 和包内许可证核验前不运行。 |

## 已准入的模拟确认层实例

| ID | 第一方页面和条款 | 原始归档 SHA-256 | 字段/变换 | 当前状态 |
| --- | --- | --- | --- | --- |
| invs2013 | [SocioPatterns workplace](https://sociopatterns.org/datasets/contacts-in-a-workplace/)；页面明确 CC0。 | `bf818f7e819864e134c90ed82f2cda6ca9d9548d43fe4d05002ac068c91258c0` | 原始 `t i j` 无向接触；在同一时刻写为双向边。 | `admitted_simulated_ic_confirmation` |
| invs2015 | [SocioPatterns workplace 2015](https://sociopatterns.org/datasets/test/)；页面明确 CC0。 | `339eb090d506d750f38a2c1ac6aca76c00c55b462f9dea325933d8b7bc260871` | 原始 `t i j` 无向接触；在同一时刻写为双向边。 | `admitted_simulated_ic_confirmation` |
| sfhh2009 | [SocioPatterns SFHH](https://sociopatterns.org/datasets/sfhh-conference-data-set/)；页面明确 CC0。 | `77de2e3d490e0d2426f55c19bbd8d4255f1d3b39a20820474a88dd15d1aa1556` | 原始 `t i j` 无向接触；在同一时刻写为双向边。 | `admitted_simulated_ic_confirmation` |
| kenya2012 | [SocioPatterns Kenya](https://sociopatterns.org/datasets/kenyan-households-contact-network/)；页面明确 CC0。 | `1d6211ac1ddfeda4feb2285b1882cac5a7bde4ce96fdd04488d5abd2de1abadb` | 原始家庭成员接触记录；以家庭-成员复合 ID 和小时级时间写为双向边。 | `admitted_simulated_ic_confirmation` |

## 已确认的语义边界

- 即使 CollegeMsg/email 将来准入，消息/邮件边仍不是级联传播的观察父子边。
  本研究只能报告“给定拓扑上的模拟 IC 选择”，不能称真实消息传播预测。
- email-Eu-core-temporal 的节点是匿名机构成员且只覆盖机构内部通信；不能外推为
  普通邮件网络。
- 多个来自同一 SNAP 目录的数据不自动构成独立的统计总体；论文应逐网络展示，
  不对少量网络作总体显著性宣称。
- SocioPatterns 接触数据是匿名的无向接近事件。双向化只定义了模拟 IC 的拓扑；
  不能把模拟 spread 解释为真实信息扩散、线上转发或因果干预效果。

## 数据准入后的操作顺序

1. 保存条款页面或授权记录的访问日期和文本哈希；
2. 下载至隔离原始目录，记录 URL、日期、字节数、SHA-256；
3. 仅将 `SRC DST TS` 转成标准化事件表；保存解析、去重和时间排序日志；
4. 先运行不可见选择结果的图规模/全搜索资源预检；
5. 只有预检通过才生成冻结的数据卡和确认层运行矩阵。

在前述步骤完成前，任何候选的实验行都不得从 `planned_not_run` 变为运行状态。
