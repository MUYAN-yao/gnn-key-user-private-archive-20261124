$ErrorActionPreference = 'Stop'
$target = 'D:\竞赛\兵乓球\deliverables\work_brief_20261030\output\乒乓球实验工作简报_20261026-1030.pptx'
$qaDir = 'D:\校创\基于GNN的关键用户识别\deliverables\weekly-brief-20261030'
$backup = Join-Path $qaDir 'original_5slides.pptx'
if (!(Test-Path -LiteralPath $backup)) { Copy-Item -LiteralPath $target -Destination $backup }
$work = Join-Path $qaDir 'combined_8slides.pptx'
Copy-Item -LiteralPath $backup -Destination $work -Force
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($work, $false, $false, $false)
$pages = @(
    @{
        Title='关键用户识别｜实验复现核验'
        Rows=@(
            @('结果核验','54 个条件、468 个实验臂完成核对','核对源码、数据与结果记录，补齐复现说明'),
            @('复现重跑','12 个代表性条件重跑，64 个实验臂一致','选中节点、整数得分及传播评估数组均一致'),
            @('图表复核','重新生成并核对 30 份统计与图像文件','数值表一致，图像解码像素一致')
        )
        Footer='2026.10.26—10.30｜同机复现检查，不增加独立实验样本量'
        Notes='来源：reproducible-revision-20261026/revision_report_zh.md；.planning/computing-reproducibility-20261026/progress.md。12条件64臂包括主实验6条件52臂及严格容差6条件12臂。本周执行的是代表性复现重跑，并非全部实验重新运行。'
    },
    @{
        Title='关键用户识别｜整理历史证据'
        Rows=@(
            @('历史复核','复核 4680 份已保存传播评估向量','补齐参数、采样方式与候选池覆盖率说明'),
            @('补充材料','新增 5 张表、2 幅图','整合历史结果，明确证据来源与适用范围'),
            @('核心认识','预算效应需结合排名精度解释','集合改变不等于传播收益同步提高')
        )
        Footer='本周基于已有数据整理；相关结论限于已测试网络与设置'
        Notes='来源：historical-evidence-revision-20261027/revision_report_zh.md、qa/final_checks.json；structural-language-revision-20261027/revision_report_zh.md。新增补充表S9—S13、图S5—S6。历史结果整合未新增传播模拟；ca-GrQc默认预算下的反转在事后精度控制中消失，不能将现象仅归因于预算变化。'
    },
    @{
        Title='关键用户识别｜论文修订与下周重点'
        Rows=@(
            @('论文修订','围绕参照预算与排名精度重写研究主线','明确贡献，区分集合变化与传播收益'),
            @('稿件交付','完成中英文正文及英文补充材料','同步题名与投稿附信，完成编译和版面核查'),
            @('下周重点','统一投稿版本，整理投稿材料','评估传播参数与固定边采样对照的补充范围')
        )
        Footer='论文题目：候选受限影响力最大化的评价：参照预算与排名精度的影响'
        Notes='来源：contribution-action-revision-20261028/README.md、revision_report_zh.md、qa/title-amendment-20261029/verification.json。10月29日统一题名。英文正文17页、中文正文20页、补充材料26页。下周内容为拟开展工作，尚未执行。'
    }
)
function Set-Text($slide, $name, $value) {
    $shape = $slide.Shapes.Item($name)
    $shape.TextFrame.TextRange.Text = $value
    $shape.TextFrame.AutoSize = 0
    $shape.TextFrame.WordWrap = -1
}
foreach ($page in $pages) {
    $range = $pres.Slides.Item(2).Duplicate()
    $slide = $range.Item(1)
    $slide.MoveTo($pres.Slides.Count)
    Set-Text $slide 'Rectangle 12' $page.Title
    $names=@(@('Rectangle 2','Rectangle 3','Rectangle 4'),@('Rectangle 5','Rectangle 6','Rectangle 7'),@('Rectangle 8','Rectangle 9','Rectangle 10'))
    for ($r=0; $r -lt 3; $r++) {
        for ($c=0; $c -lt 3; $c++) { Set-Text $slide $names[$r][$c] $page.Rows[$r][$c] }
    }
    Set-Text $slide 'Rectangle 11' $page.Footer
    $slide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text=$page.Notes
}
foreach ($slide in $pres.Slides) { Set-Text $slide 'Rectangle 1' ($slide.SlideIndex.ToString() + ' / ' + $pres.Slides.Count) }
$pres.Save()
$checks=@()
foreach ($slide in $pres.Slides) {
    if ($slide.SlideIndex -ge 6) {
        $slide.Export((Join-Path $qaDir ('slide-' + $slide.SlideIndex + '.png')), 'PNG', 1600, 900)
        foreach ($shape in $slide.Shapes) {
            if ($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1) {
                $checks += [PSCustomObject]@{Slide=$slide.SlideIndex;Name=$shape.Name;Text=$shape.TextFrame.TextRange.Text;Width=$shape.Width;Height=$shape.Height;TextWidth=$shape.TextFrame.TextRange.BoundWidth;TextHeight=$shape.TextFrame.TextRange.BoundHeight;FontSize=$shape.TextFrame.TextRange.Font.Size}
            }
        }
    }
}
$checks | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $qaDir 'layout_checks.json') -Encoding utf8
$count=$pres.Slides.Count
$pres.Close()
Copy-Item -LiteralPath $work -Destination $target -Force
[PSCustomObject]@{SlideCount=$count;AddedSlides='6–8';Output=$target;Backup=$backup} | ConvertTo-Json
