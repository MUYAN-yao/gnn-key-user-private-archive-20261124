"""Build the r46 review copy and verify source/evidence preservation."""
from pathlib import Path
import hashlib
import json
import math
import re
import sys
from zipfile import ZipFile

from docx import Document

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'manuscript'))
import build_internal_word_draft as builder


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = ROOT / 'manuscript/temporal_key_user_identification_snam_r46_contribution_revision.docx'
    zh = (ROOT / 'manuscript/draft_zh_v0_1.md').read_text(encoding='utf-8')
    en = (ROOT / 'manuscript/abstract_en_v0_1.md').read_text(encoding='utf-8')
    before = (HERE / 'before/draft_zh_v0_1.md').read_text(encoding='utf-8')
    assert zh.split('## 参考文献')[1] == before.split('## 参考文献')[1]
    old_tables = [line for line in before.splitlines() if line.startswith('|')]
    new_tables = [line for line in zh.splitlines() if line.startswith('|')]
    assert old_tables == new_tables
    old_images = re.findall(r'!\[.*?\]\((.*?)\)', before)
    new_images = re.findall(r'!\[.*?\]\((.*?)\)', zh)
    assert old_images == new_images and len(new_images) == 10
    abstract = en.split('## Abstract')[1].split('**Keywords:**')[0].strip()
    assert 150 <= len(abstract.split()) <= 250
    assert len(en.split('**Keywords:**')[1].split('\n')[0].split(';')) == 6
    source_dir = ROOT / 'results/higgs-50000-v4-screening-diagnostic-070-48'
    manifest = json.loads((source_dir / 'manifest.json').read_text(encoding='utf-8'))
    name, digest = next(iter(manifest['artifact'].items()))
    assert sha(source_dir / name) == digest
    evidence = json.loads((source_dir / name).read_text(encoding='utf-8'))
    g, d = (evidence['arms'][key] for key in ('gnn_prior', 'weighted_out_degree'))
    assert g['reporting_evaluation'] == d['reporting_evaluation']
    assert g['selection']['top_k'] == d['selection']['top_k'] == ['88', '1988']
    assert len(set(g['membership_rank_order']) & set(d['membership_rank_order'])) == 91
    assert g['reporting_evaluation']['mean_spread'] == 3193.45
    assert g['reporting_evaluation']['robust_objective'] == 3096.981208
    assert not (set(evidence['reproducibility']['selection_worlds']) &
                set(evidence['reproducibility']['evaluation_worlds']))
    for arm in evidence['arms'].values():
        assert len(set(arm['canonical_candidate_order'])) == 120
        assert [len(r['candidate_scores']) for r in arm['rounds']] == [120, 119]
        assert len(arm['reporting_evaluation']['world_spreads']) == 20
    source_hash_checks = {}
    for name, expected in manifest['sources'].items():
        folder = 'protocols' if name.endswith('.md') else ('experiments' if name.startswith('run_') else 'backend/app')
        source_hash_checks[name] = sha(ROOT / folder / name) == expected
    assert all(source_hash_checks.values())

    builder.build(output)
    doc = Document(output)
    # The shared builder retains an editorial note in its English appendix.
    # Remove only that internal tail from the new review copy.
    remove = False
    for p in list(doc.paragraphs):
        if p.text.startswith('Editorial note'):
            remove = True
        if remove:
            p._element.getparent().remove(p._element)
    # Keep the short algorithm block and each small table with its caption.
    for p in doc.paragraphs:
        if p.text.startswith('ROBUST-GREEDY('):
            p.paragraph_format.keep_together = True
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.keep_with_next = True
        sibling = table._tbl.getnext()
        from docx.text.paragraph import Paragraph
        while sibling is not None and sibling.tag.endswith('}p'):
            p = Paragraph(sibling, doc._body)
            if not p.text.strip():
                p.paragraph_format.keep_with_next = True
                sibling = sibling.getnext()
                continue
            if p.text.startswith('表 '):
                p.paragraph_format.keep_together = True
                p.paragraph_format.keep_with_next = False
            break
    comments = {
        '时序社交网络中的关键用户识别：传播概率建模':
            '本轮将主线调整为概率建模与候选缩减的实证评估；标题不预设学习组件的独立收益。',
        '建立传播概率建模与种子集合选择的分层证据链':
            '贡献点对应 C2、C5、C11、C12。概率预测门槛与选种增益分开表述。',
        '上述隔离仅说明记录的时间窗口':
            '新增 C11 信息边界：全期边集合参与校准负样本资格判定，不能称整个流程严格在线。',
        '6.7 同预算筛选的单次机制诊断':
            '新增 C10 诊断证据，n=1，不合并进 v3 或既有显著性检验。',
        'v3 三十次运行表明':
            '结论保留阶段成本观察，同时说明 GNN 独特筛选价值和学习概率的独立贡献尚未确立。',
    }
    for anchor, note in comments.items():
        p = next(p for p in doc.paragraphs if p.text.startswith(anchor))
        doc.add_comment(p.runs, text=note, author='修订说明', initials='R46')
    assert len(doc.inline_shapes) == 10
    assert '[Missing figure' not in '\n'.join(p.text for p in doc.paragraphs)
    doc.save(output)
    old_doc = ROOT / 'manuscript/temporal_key_user_identification_snam_r45_figure_revision.docx'
    def image_hashes(path):
        with ZipFile(path) as z:
            return sorted(hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/'))
    assert image_hashes(old_doc) == image_hashes(output), 'Figure binary changed'
    report = {
        'reference_section_unchanged': True,
        'all_existing_table_rows_unchanged': True,
        'image_paths_unchanged': True,
        'r45_embedded_images_identical': True,
        'abstract_word_count': len(abstract.split()),
        'diagnostic_sha256': digest,
        'diagnostic_numbers_verified': True,
        'archived_source_hash_checks': source_hash_checks,
        'word_sha256': sha(output),
        'word_inline_figures': 10,
        'word_revision_comments': len(comments),
        'source_hashes': {p.name: sha(p) for p in [ROOT / 'manuscript' / n for n in
            ('draft_zh_v0_1.md', 'abstract_en_v0_1.md', 'snam_introduction_en_v1.md',
             'claim_ledger.md', 'innovation_evidence_matrix.md')]},
        'visual_qa': 'pending',
    }
    (HERE / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
