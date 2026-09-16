// Run with @oai/artifact-tool available. Arguments: repository root, output directory.
// Imports the existing workbook; never rebuilds its sheets or native objects.
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { FileBlob, SpreadsheetFile, Workbook } from '@oai/artifact-tool';

const [repo, out] = process.argv.slice(2);
if (!repo || !out) throw new Error('Usage: node update_screening_pilot.mjs REPO OUTPUT_DIR');
await fs.mkdir(out, {recursive: true});
const pilot = JSON.parse(await fs.readFile(path.join(repo, 'literature/screening/pilot_01.json'), 'utf8'));
const inputBytes=await fs.readFile(path.join(repo,'literature/evidence_matrix_2020_2026.xlsx'));
const inputBlobSha=createHash('sha1').update(`blob ${inputBytes.length}\0`).update(inputBytes).digest('hex');
assert.equal(inputBlobSha,'4b203c2ad0b58f5e07b6c84211acefca43ba832d','This one-time migration requires the v0.4 workbook baseline (local commit 589e766 / remote 9191c3a). It must not overwrite later screening work.');
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(repo, 'literature/evidence_matrix_2020_2026.xlsx')));
const matrix = wb.worksheets.getItem('Evidence Matrix');
const log = wb.worksheets.getItem('Screening Log');
const summary = wb.worksheets.getItem('Summary');
const protocol = wb.worksheets.getItem('Review Protocol');
const dictionary = wb.worksheets.getItem('Coding Dictionary');
const csvBook = await Workbook.fromCSV(await fs.readFile(path.join(repo, 'literature/references/forward_model_mismatch_90_references.csv'), 'utf8'), {sheetName:'References'});
const csvSheet = csvBook.worksheets.getItem('References');
const csvValues = csvSheet.getUsedRange().values;
const headers = csvValues[0];
const refs = csvValues.slice(1).filter(r=>r[0]).map(r=>Object.fromEntries(headers.map((h,i)=>[h,r[i]??''])));
assert.equal(refs.length, 90);
const changes = [];
const allowed = new Map();
const snapshots = [];
for (let i=0;i<5;i++) {
  const sheet=wb.worksheets.getItemAt(i);
  snapshots.push({name:sheet.name, values:sheet.getRange('A1:AF101').values, formulas:sheet.getRange('A1:AF101').formulas});
}
function set(sheet, address, value, reason='Pilot update') {
  const old=sheet.getRange(address).values[0][0];
  sheet.getRange(address).values=[[value]];
  allowed.set(`${sheet.name}!${address}`, true);
  if(old!==value) changes.push({sheet:sheet.name, cell:address, old:old??null, new:value, reason});
}
function formula(address, value) {
  summary.getRange(address).formulas=[[value]];
  allowed.set(`Summary!${address}`,true);
}
const colNames = {'Authors':'C','Title':'D','Venue':'E','Primary source URL':'AE'};
const evidenceStatus = r => r.basis.includes('abstract not retrieved') ? 'Title/project checked; abstract pending'
  : r.basis.includes('snippet only') ? 'Incomplete evidence; retrieval pending' : 'Abstract inspected; full-text pending';
for (const r of pilot.records) {
  const index=refs.findIndex(x=>x['Study ID']===r.study_id);
  assert(index>=0);
  const row=index+2, ref=refs[index];
  assert.equal(matrix.getRange(`A${row}`).values[0][0], r.study_id);
  assert.equal(log.getRange(`A${row}`).values[0][0], `S${String(index+1).padStart(3,'0')}`);
  for(const [field,value] of Object.entries(r.metadata??{})) {
    changes.push({record:r.study_id, field, old:ref[field]??null, new:value, source:r.source_url, reason:'Primary-source metadata correction'});
    ref[field]=value;
    if(colNames[field]) set(matrix, `${colNames[field]}${row}`,value,'Source-backed metadata correction');
  }
  ref['Evidence status']=evidenceStatus(r);
  const notes=`AI pilot ${pilot.checked_on}; ${r.decision.endsWith('advance')?'advance to full text':'unclear'}. ${r.criterion_3}. Human adjudication and full-text coding pending. Evidence: ${r.source_url}`;
  ref['Review notes']=`${ref['Review notes'].split(' | AI pilot ')[0]} | ${notes}`;
  set(matrix, `Z${row}`,ref['Evidence status'],'Record actual evidence inspected in this pilot');
  set(matrix, `AF${row}`,ref['Review notes']);
  set(log, `E${row}`,ref.Title,'Mirror corrected title');
  set(log, `G${row}`,ref['Primary source URL'],'Mirror corrected source');
  set(log, `I${row}`,r.decision,'AI recommendation; not a human or final eligibility decision');
  set(log, `L${row}`,`${pilot.checked_on} | AI only; human pending. ${r.criterion_3}. Basis: ${r.basis}. Full-text question and source: screening/pilot_01.json (${r.study_id}).`);
  // No changes to full-text decision, exclusion reason, discovery date or acquisition status.
}
for(let i=0;i<refs.length;i++) {
  refs[i]['Inclusion decision']='Pending formal eligibility';
  set(matrix, `AA${i+2}`, 'Pending formal eligibility', 'Legacy Include meant seed-map membership, not completed formal inclusion');
}

summary.getRange('D10:E10').copyFrom(summary.getRange('D5:E5'),'all');
allowed.set('Summary!D10',true); allowed.set('Summary!E10',true);
set(summary,'D10','AI pilot — not formal'); set(summary,'E10','Records');
set(summary,'D11','Pilot records triaged');
set(summary,'D12','Advance to full text');
set(summary,'D13','Unclear / retrieve');
set(summary,'D14','Not pilot-triaged');
formula('E11','=COUNTIF(\'Screening Log\'!$I$2:$I$101,"AI pilot: advance")+COUNTIF(\'Screening Log\'!$I$2:$I$101,"AI pilot: unclear")');
formula('E12','=COUNTIF(\'Screening Log\'!$I$2:$I$101,"AI pilot: advance")');
formula('E13','=COUNTIF(\'Screening Log\'!$I$2:$I$101,"AI pilot: unclear")');
formula('E14','=B6-E11');
summary.getRange('D11:E14').format.fill='#EAF2F8';
summary.getRange('D10:E10').format.fill='#1F4E78';
summary.getRange('D10:E10').format.font.color='#FFFFFF';
summary.getRange('D10:E10').format.font.bold=true;
summary.getRange('D10:E14').format.wrapText=true;
summary.getRange('D10:E14').format.rowHeight=32;
summary.getRange('E11:E14').setNumberFormat('0');
set(summary,'A9','Formal title/abstract screened');
set(summary,'A22','Proceed with reproducible database searches and human adjudication. The first 20 seed records received AI pilot recommendations only; no formal inclusion or methodological novelty is established. Feature codes require full-text verification.');

const protocolText=await fs.readFile(path.join(repo,'docs/systematic_review_protocol.md'),'utf8');
const queries=[...protocolText.matchAll(/```text\n([\s\S]*?)\n```/g)].map(m=>m[1].replace(/\s+/g,' ').trim());
assert.equal(queries.length,3);
for(let i=0;i<3;i++)set(protocol,`B${13+i}`,queries[i],'Align summary with authoritative protocol; no new database execution');
set(protocol,'B7','To what extent do learning-based image or video reconstruction methods remain accurate, calibrated and evidentially faithful when the true acquisition operator differs from the assumed forward model?','Mirror authoritative review question');
set(protocol,'B19','Planning estimate only: 60–100 full-text papers; not an eligibility quota. Include all studies meeting the protocol.');
set(protocol,'B21','0.3 — working draft amended 16 September 2026; not registered. Corrects inconsistent workbook 1.1 label.');
set(protocol,'B22','20 AI pilot recommendations (18 advance, 2 unclear); all human adjudication pending. Formal database searches and two-stage eligibility are not completed; formal inclusion/exclusion counts remain zero.');
set(protocol,'B23','90 seed candidates, not 90 included studies. AI pilot decisions are preliminary; missing abstracts are flagged, not excluded. See screening/pilot_01.json and docs/systematic_review_protocol.md.');
set(dictionary,'B17','Abstract inspected; full-text pending / Title/project checked; abstract pending / Incomplete evidence; retrieval pending / legacy labels');
set(dictionary,'C17','Describes evidence actually accessed, not study quality. Legacy labels outside the pilot remain unverified here. All feature codes require full-text verification.');

log.getRange('I1:J21').format.columnWidth=24;
// Preserve the existing shared decision dropdown and extend its explicit labels.
// Only column I receives pilot values; column J stays Pending for every record.
log.getRange('I2:J101').dataValidation.rule={type:'list',values:['Pending','Include','Exclude','Unclear','AI pilot: advance','AI pilot: unclear']};
log.getRange('L1:L101').format.columnWidth=64;
log.getRange('I1:N21').format.wrapText=true;
log.getRange('A2:N21').format.verticalAlignment='top';
log.getRange('A2:N21').format.rowHeight=84;
log.getRange('I1:N1').format.rowHeight=42;
for(const r of pilot.records) {
  const row=Number(r.study_id.slice(1))+1;
  log.getRange(`I${row}`).format.fill=r.decision.endsWith('unclear')?'#FFF2CC':'#E2F0D9';
}
protocol.getRange('B13:B15').format.wrapText=true;
protocol.getRange('B13:B15').format.rowHeight=78;
protocol.getRange('B19:B23').format.wrapText=true;
protocol.getRange('B19:B23').format.rowHeight=62;
dictionary.getRange('A17:C17').format.wrapText=true;
dictionary.getRange('A17:C17').format.rowHeight=96;

// Behavioural check: changing one input must change dependent pilot counters, then restore it.
assert.deepEqual(summary.getRange('E11:E14').values.flat(),[20,18,2,70]);
const decision=log.getRange('I2').values[0][0];
log.getRange('I2').values=[['Pending']];
assert.deepEqual(summary.getRange('E11:E14').values.flat(),[19,17,2,71]);
log.getRange('I2').values=[[decision]];
wb.recalculate();
assert.deepEqual(summary.getRange('E11:E14').values.flat(),[20,18,2,70]);
assert.deepEqual(summary.getRange('B7:B12').values.flat(),[0,0,0,0,0,0]);
assert.equal(log.getRange('I22:I91').values.filter(r=>r[0]==='Pending').length,70);
assert.equal(log.getRange('J2:J91').values.filter(r=>r[0]==='Pending').length,90);
assert.equal(log.getRange('K2:K91').values.filter(r=>r[0]!=null && r[0]!=='').length,0);
const errors=[]; const unintended=[];
function address(row,col) {let s=''; for(let n=col+1;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s+(row+1);}
for(const before of snapshots) {
  const sheet=wb.worksheets.getItem(before.name);
  const after=sheet.getRange('A1:AF101').values, afterF=sheet.getRange('A1:AF101').formulas;
  for(let r=0;r<101;r++)for(let c=0;c<32;c++) {
    const addr=`${before.name}!${address(r,c)}`;
    if(!allowed.has(addr) && ((before.values[r]?.[c]??null)!==(after[r]?.[c]??null) || (before.formulas[r]?.[c]??'')!==(afterF[r]?.[c]??'')))unintended.push(addr);
    if(typeof after[r]?.[c]==='string' && /^#(REF!|DIV\/0!|VALUE!|NAME\?|N\/A|NUM!|SPILL!|CALC!)/.test(after[r][c]))errors.push(addr);
  }
}
assert.deepEqual(unintended,[]); assert.deepEqual(errors,[]);
const output=await SpreadsheetFile.exportXlsx(wb);
await output.save(path.join(out,'evidence_matrix_2020_2026.xlsx'));
for(const [name,range] of [['Summary','A5:E14'],['Screening Log','I1:L4'],['Review Protocol','A19:B23'],['Coding Dictionary','A17:C17']]) {
  const img=await wb.render({sheetName:name,range,scale:1,format:'png'});
  await fs.writeFile(path.join(out,`after_${name.replaceAll(' ','_')}.png`),new Uint8Array(await img.arrayBuffer()));
}

// Synchronize derived reference formats with the corrected matrix metadata.
const csvEscape=s=>'"'+String(s??'').replaceAll('"','""')+'"';
const csv=[headers,...refs.map(r=>headers.map(h=>r[h]))].map(r=>r.map(csvEscape).join(',')).join('\n')+'\n';
// Reimport the generated CSV to verify row/column integrity rather than relying on a custom parser.
const checkCsv=await Workbook.fromCSV(csv,{sheetName:'Check'});
assert.equal(checkCsv.worksheets.getItem('Check').getUsedRange().values.length,91);
await fs.writeFile(path.join(out,'forward_model_mismatch_90_references.csv'),csv);
const tex=s=>String(s).replaceAll('&','\\&').replaceAll('%','\\%').replaceAll('_','\\_');
const authorList=r=>r.Authors.includes(';')?r.Authors.split(';').map(s=>s.trim()):[r.Authors];
const bib=refs.map(r=>{
  const type=r['Publication type']==='Journal'?'article':r['Publication type']==='Conference'?'inproceedings':'misc';
  const venueField=type==='article'?'journal':type==='inproceedings'?'booktitle':'howpublished';
  return `@${type}{${r['Study ID']}_${r.Year},\n  author = {${authorList(r).map(tex).join(' and ')}},\n  title = {{${tex(r.Title)}}},\n  year = {${r.Year}},\n  ${venueField} = {${tex(r.Venue)}},\n  url = {${r['Primary source URL']}},\n${r.DOI?`  doi = {${r.DOI}},\n`:''}  note = {Seed candidate ${r['Study ID']}; evidence status: ${tex(r['Evidence status'])}; pending formal eligibility and human adjudication}\n}`;
}).join('\n\n')+'\n';
await fs.writeFile(path.join(out,'forward_model_mismatch_90_references.bib'),bib);
const ris=refs.map(r=>[
  `TY  - ${r['Publication type']==='Journal'?'JOUR':r['Publication type']==='Conference'?'CPAPER':'GEN'}`,
  `ID  - ${r['Study ID']}`,...authorList(r).map(a=>`AU  - ${a}`),`PY  - ${r.Year}`,`TI  - ${r.Title}`,`T2  - ${r.Venue}`,`UR  - ${r['Primary source URL']}`,
  ...(r.DOI?[`DO  - ${r.DOI}`]:[]),`N1  - Evidence status: ${r['Evidence status']}; formal eligibility pending. AI pilot recommendations, where present, require human adjudication.`,`ER  -`
].join('\n')).join('\n\n')+'\n';
await fs.writeFile(path.join(out,'forward_model_mismatch_90_references.ris'),ris);
const bibMD='# Forward-Model Mismatch Review: 90 Seed Publications\n\n> Draft seed references, not a PRISMA-included corpus or submission-ready bibliography. The first 20 received preliminary AI triage; all require human adjudication and full-text verification. Author lists outside verified corrections may remain abbreviated. See ../screening/pilot_01_report.md for evidence limits.\n\n'+refs.map((r,i)=>`${i+1}. **${r['Study ID']}** — ${r.Authors} (${r.Year}). “${r.Title}.” *${r.Venue}*. [Primary source](${r['Primary source URL']})  \n   Evidence: ${r['Evidence status']}; formal eligibility: pending; closest competitor (provisional): ${r['Closest competitor']}.`).join('\n')+'\n';
await fs.writeFile(path.join(out,'forward_model_mismatch_90_bibliography.md'),bibMD);
await fs.writeFile(path.join(out,'pilot_01_changes.json'),JSON.stringify({checked_on:pilot.checked_on,baseline_local_commit:'589e7668e8afc124933a94307d0f52256ac27fc5',baseline_remote_commit:'9191c3a78e640ce7ff6a99275e1cf465177cb225',note:'Legacy Include labels expressed seed-map membership. No completed inclusion decisions were reversed. Unrelated feature codes were preserved.',changes},null,2)+'\n');
const report=`# Pilot 01: preliminary screening of 20 seed records\n\nChecked: ${pilot.checked_on}. Protocol: v${pilot.protocol_version}, working draft, not registered. Reviewer: Codex AI assistance; all human adjudication pending.\n\n## Outcome\n\n| Stage | Records |\n|---|---:|\n| Seed candidates | 90 |\n| AI pilot triaged | 20 |\n| Recommend full-text review | 18 |\n| Unclear: resolve scope/retrieval | 2 |\n| Not yet pilot-triaged | 70 |\n| Formally included / excluded | 0 / 0 |\n\nThese are the first 20 stable seed IDs, not a random sample or formal database search. Seventeen complete abstracts were inspected. P001 and P013 were conservatively advanced using their titles and official author repositories; their abstracts remain to be retrieved. P016 has only partial search-result evidence. Reading P005's PDF abstract/opening page is not a full-text eligibility assessment. No human agreement statistic, full-text appraisal or definitive novelty claim can be computed from this pilot.\n\nThe initial seed matrix's feature ratings remain provisional. This checkpoint corrects metadata and evidence labels; it does not validate every pre-existing Yes/No code.\n\n## Decisions and evidence\n\n${pilot.records.map(r=>{
  const ref=refs.find(x=>x['Study ID']===r.study_id);
  return `### ${r.study_id} — ${ref.Title}\n\n**Recommendation:** ${r.decision}. Human adjudication: pending.\n\n**Evidence basis:** ${r.basis}. [Inspected source](${r.source_url}).\n\n${r.evidence}\n\n**Scope signal:** ${r.criterion_3}.\n\n**Full-text question:** ${r.full_text_question}\n`;
}).join('\n')}\n## Metadata and status repairs\n\n- P001: replaced incorrect Dong authorship with Yuesong Nan and Hui Ji.\n- P004: corrected CVPR to ECCV 2020 and replaced the erroneous CVF link with the publisher DOI; added the verified author list.\n- P007: replaced the unrelated AAAI page ending 16430 with 16366; added the complete title, authors and DOI.\n- P017/P019: replaced abbreviated DDNM and GibbsDDRM labels with complete titles.\n- P020: corrected the NeurIPS proceedings hash and used its proceedings title; the differently worded preprint title belongs to the same lineage.\n- All 90: changed seed-map Include labels to Pending formal eligibility. The original values and exact changes are in pilot_01_changes.json and git history.\n- Protocol: reconciled the workbook's inconsistent 1.1 label with the authoritative v0.3 working-draft amendment; matched its query summary to the protocol without executing new database searches.\n\n## Next actions\n\n1. A human reviewer adjudicates all 20 recommendations, prioritizing unclear P006 and P016 and the abstract-access gaps P001/P013. Recheck borderline NETT P002 against criterion 3.\n2. Retrieve and fully extract the nearest-method set P001, P005, P008, P011, P018 and P019, retaining page/section evidence for each capability and limitation.\n3. Execute database-adapted queries, retaining raw exports, exact query syntax, dates, filters and counts. Reconcile seed IDs and preprint/proceedings/journal lineages against those exports.\n4. Continue triage of P021–P090, without imposing a target number of inclusions. The earlier lineage-verification audit remains separate and must be reconciled during report-level deduplication.\n5. Test a precise contribution against the nearest competitors. Failure to find one paper containing every desired feature is not evidence of novelty.\n`;
await fs.writeFile(path.join(out,'pilot_01_report.md'),report);
console.log(JSON.stringify({pilot:20,advance:18,unclear:2,untriaged:70,formal_included:0,unintended_cell_changes:unintended,formula_errors:errors,behavioural_test:'passed',output:out},null,2));
