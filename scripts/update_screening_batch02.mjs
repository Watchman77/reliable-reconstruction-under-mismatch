// One-time v0.5 -> v0.6 migration. Run with @oai/artifact-tool available.
// Arguments: repository root, output directory. Existing workbook objects are preserved.
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {FileBlob, SpreadsheetFile, Workbook} from '@oai/artifact-tool';
const [repo,out]=process.argv.slice(2);
if(!repo||!out)throw new Error('Usage: node update_screening_batch02.mjs REPO OUTPUT_DIR');
await fs.mkdir(out,{recursive:true});
const batch=JSON.parse(await fs.readFile(path.join(repo,'literature/screening/pilot_02.json'),'utf8'));
const input=path.join(repo,'literature/evidence_matrix_2020_2026.xlsx');
const bytes=await fs.readFile(input);
const sha=createHash('sha1').update(`blob ${bytes.length}\0`).update(bytes).digest('hex');
assert.equal(sha,'8a8353b6bcccc63a82bb5dfff0b580a17b815a2c','Requires the v0.5 workbook; must not overwrite a later checkpoint.');
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(input));
const matrix=wb.worksheets.getItem('Evidence Matrix'),log=wb.worksheets.getItem('Screening Log');
const summary=wb.worksheets.getItem('Summary'),protocol=wb.worksheets.getItem('Review Protocol');
const dictionary=wb.worksheets.getItem('Coding Dictionary');
const csvWb=await Workbook.fromCSV(await fs.readFile(path.join(repo,'literature/references/forward_model_mismatch_90_references.csv'),'utf8'),{sheetName:'References'});
const csvValues=csvWb.worksheets.getItem('References').getUsedRange().values;
const headers=csvValues[0],refs=csvValues.slice(1).filter(r=>r[0]).map(r=>Object.fromEntries(headers.map((h,i)=>[h,r[i]??''])));
assert.equal(refs.length,90);assert.equal(batch.records.length,20);
const snapshots=[];
for(let i=0;i<5;i++){
 const s=wb.worksheets.getItemAt(i);
 snapshots.push({name:s.name,values:s.getRange('A1:AF101').values,formulas:s.getRange('A1:AF101').formulas});
}
const changes=[],allowed=new Set(['Summary!E11','Summary!E12','Summary!E13','Summary!E14']);
function set(sheet,address,value,reason='Batch 02 preliminary screening'){
 const old=sheet.getRange(address).values[0][0];
 if(old===value)return;
 sheet.getRange(address).values=[[value]];
 allowed.add(`${sheet.name}!${address}`);
 changes.push({sheet:sheet.name,cell:address,old:old??null,new:value,reason});
}
const columns={'Year':'B','Authors':'C','Title':'D','Venue':'E','Publication type':'F','Peer reviewed':'G','Primary source URL':'AE'};
for(const r of batch.records){
 const index=refs.findIndex(x=>x['Study ID']===r.study_id),row=index+2;
 assert(index>=20&&index<40);
 const ref=refs[index];
 assert.equal(matrix.getRange(`A${row}`).values[0][0],r.study_id);
 assert.equal(log.getRange(`A${row}`).values[0][0],`S${String(index+1).padStart(3,'0')}`);
 assert.equal(log.getRange(`I${row}`).values[0][0],'Pending');
 for(const [field,value] of Object.entries(r.metadata??{})){
  changes.push({record:r.study_id,field,old:ref[field]??null,new:value,source:r.metadata_source_url??r.source_url,reason:'Source-backed correction or lineage reconciliation'});
  ref[field]=value;
  if(columns[field])set(matrix,`${columns[field]}${row}`,value,'Verified metadata or existing lineage audit');
 }
 ref['Evidence status']=r.status;
 // Keep historical notes; add an explicit evidence limit rather than validate old feature codes.
 ref['Review notes']+=` | AI pilot ${batch.checked_on}: advance to full-text review; human pending. Basis: ${r.basis}. Feature codes remain provisional. ${r.full_text_question} Evidence: ${r.source_url}`;
 set(matrix,`Z${row}`,r.status,'State the evidence actually inspected');
 set(matrix,`AF${row}`,ref['Review notes']);
 set(log,`E${row}`,ref.Title,'Mirror corrected title');
 set(log,`F${row}`,Number(ref.Year),'Mirror canonical publication year');
 set(log,`G${row}`,ref['Primary source URL'],'Mirror corrected locator');
 set(log,`I${row}`,r.decision,'AI recommendation only; human and formal eligibility pending');
 set(log,`L${row}`,`${batch.checked_on} | AI only; human pending. ${r.criterion_3}. Basis: ${r.basis}. Sources and full-text question: screening/pilot_02.json (${r.study_id}).`);
 log.getRange(`I${row}`).format.fill='#E2F0D9';
}
for(const r of batch.revisits){
 const index=refs.findIndex(x=>x['Study ID']===r.study_id),row=index+2,ref=refs[index];
 assert.equal(log.getRange(`I${row}`).values[0][0],r.decision);
 ref['Review notes']+=` | Batch 02 revisit ${batch.checked_on}: ${r.note} Source: ${r.source_url}`;
 set(matrix,`AF${row}`,ref['Review notes'],'Preserve unresolved decision and document new evidence/access limits');
 set(log,`L${row}`,`${log.getRange(`L${row}`).values[0][0]} Revisit: ${r.basis}; unchanged unclear. See screening/pilot_02.json.`);
 if(r.study_id==='P006'){
  ref['Evidence status']='Targeted full-text sections inspected';
  set(matrix,`Z${row}`,ref['Evidence status'],'Experiments section inspected; complete eligibility still pending');
 }
}
set(summary,'A16','Nearest-method overlap');
set(summary,'A17','AverNet already tests compound/time-varying video degradation; PRISM evaluates joint image/kernel uncertainty; VDPS documents dynamic blind reconstruction. Specific inspected passages and limitations are recorded in screening/pilot_02_report.md.');
set(summary,'A22','40/90 seed records have AI pilot recommendations: 38 advance, 2 unclear; 50 remain. All human adjudication is pending. No formal inclusion or methodological novelty is established. Feature codes still require full-text verification.');
set(summary,'A26','Candidate question — novelty unestablished');
set(summary,'A27','Can accounting for uncertainty in an estimated forward operator improve the reliability of selectively released image detail when the true acquisition process leaves the assumed model family? Test against the nearest methods; a longer feature checklist does not establish novelty.');
set(protocol,'B22','40 AI pilot recommendations (38 advance, 2 unclear); 50 seed records remain. All human adjudication is pending. Formal database searches and two-stage eligibility are incomplete; formal inclusion/exclusion counts remain zero.');
set(protocol,'B23','90 seed candidates, not 90 included studies. AI recommendations and targeted passage inspections are preliminary. See screening/pilot_01.json, screening/pilot_02.json and docs/systematic_review_protocol.md.');
set(dictionary,'B17','Abstract inspected; full-text pending / Targeted full-text sections inspected / Abstract and repository inspected / Title/project checked; abstract pending / Incomplete evidence; retrieval pending / legacy labels');
set(dictionary,'C17','Evidence accessed, not study quality or final eligibility. Selected passages validate only the cited findings. All other feature codes remain provisional; positive legacy codes do not establish calibrated uncertainty.');
log.getRange('A22:N41').format.verticalAlignment='top';
log.getRange('I22:N41').format.wrapText=true;
log.getRange('A22:N41').format.rowHeight=112;
log.getRange('A7:N7').format.rowHeight=112;
log.getRange('A17:N17').format.rowHeight=112;
dictionary.getRange('A17:C17').format.rowHeight=128;
// Newly added source/evidence notes must be readable without opening the formula bar.
matrix.getRange('AF1:AF91').format.columnWidth=96;
matrix.getRange('A22:AF41').format.wrapText=true;
matrix.getRange('A22:AF41').format.verticalAlignment='top';
matrix.getRange('A22:AF41').format.rowHeight=112;
for(const row of [7,17]){
 matrix.getRange(`AF${row}`).format.wrapText=true;
 matrix.getRange(`AF${row}`).format.verticalAlignment='top';
 matrix.getRange(`A${row}:AF${row}`).format.rowHeight=128;
}
// Existing dropdowns, tables, charts, frozen panes and unrelated feature codes stay intact.
assert.deepEqual(summary.getRange('E11:E14').values.flat(),[40,38,2,50]);
const decision=log.getRange('I22').values[0][0];
log.getRange('I22').values=[['Pending']];
assert.deepEqual(summary.getRange('E11:E14').values.flat(),[39,37,2,51]);
log.getRange('I22').values=[[decision]];
wb.recalculate();
assert.deepEqual(summary.getRange('E11:E14').values.flat(),[40,38,2,50]);
assert.deepEqual(summary.getRange('B7:B12').values.flat(),[0,0,0,0,0,0]);
assert.equal(log.getRange('I42:I91').values.filter(r=>r[0]==='Pending').length,50);
assert.equal(log.getRange('J2:J91').values.filter(r=>r[0]==='Pending').length,90);
assert.equal(matrix.getRange('AA2:AA91').values.filter(r=>r[0]==='Pending formal eligibility').length,90);
const errors=[],unintended=[];
function address(row,col){let s='';for(let n=col+1;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s+(row+1);}
for(const before of snapshots){
 const s=wb.worksheets.getItem(before.name),values=s.getRange('A1:AF101').values,formulas=s.getRange('A1:AF101').formulas;
 for(let r=0;r<101;r++)for(let c=0;c<32;c++){
  const a=`${before.name}!${address(r,c)}`;
  if(!allowed.has(a)&&((before.values[r]?.[c]??null)!==(values[r]?.[c]??null)||(before.formulas[r]?.[c]??'')!==(formulas[r]?.[c]??'')))unintended.push(a);
  if(typeof values[r]?.[c]==='string'&&/^#(REF!|DIV\/0!|VALUE!|NAME\?|N\/A|NUM!|SPILL!|CALC!)/.test(values[r][c]))errors.push(a);
 }
}
assert.deepEqual(unintended,[]);assert.deepEqual(errors,[]);
const output=await SpreadsheetFile.exportXlsx(wb);
await output.save(path.join(out,'evidence_matrix_2020_2026.xlsx'));
for(const [name,range] of [['Summary','A5:E14'],['Summary','A16:H29'],['Screening Log','I22:L24'],['Screening Log','I32:L33'],['Coding Dictionary','A17:C17'],['Evidence Matrix','AE32:AF33'],['Evidence Matrix','AE7:AF7']]){
 const img=await wb.render({sheetName:name,range,scale:1,format:'png'});
 await fs.writeFile(path.join(out,`after_${name.replaceAll(' ','_')}_${range.replace(':','-')}.png`),new Uint8Array(await img.arrayBuffer()));
}
const csvEscape=s=>'"'+String(s??'').replaceAll('"','""')+'"';
const csv=[headers,...refs.map(r=>headers.map(h=>r[h]))].map(r=>r.map(csvEscape).join(',')).join('\n')+'\n';
const check=await Workbook.fromCSV(csv,{sheetName:'Check'});
assert.equal(check.worksheets.getItem('Check').getUsedRange().values.length,91);
await fs.writeFile(path.join(out,'forward_model_mismatch_90_references.csv'),csv);
const tex=s=>String(s).replaceAll('&','\\&').replaceAll('%','\\%').replaceAll('_','\\_');
const authors=r=>r.Authors.includes(';')?r.Authors.split(';').map(s=>s.trim()):[r.Authors];
const bib=refs.map(r=>{
 const type=r['Publication type']==='Journal'?'article':r['Publication type']==='Conference'?'inproceedings':'misc';
 const venue=type==='article'?'journal':type==='inproceedings'?'booktitle':'howpublished';
 return `@${type}{${r['Study ID']}_${r.Year},\n  author = {${authors(r).map(tex).join(' and ')}},\n  title = {{${tex(r.Title)}}},\n  year = {${r.Year}},\n  ${venue} = {${tex(r.Venue)}},\n  url = {${r['Primary source URL']}},\n${r.DOI?`  doi = {${r.DOI}},\n`:''}  note = {Seed candidate ${r['Study ID']}; evidence status: ${tex(r['Evidence status'])}; pending formal eligibility and human adjudication}\n}`;
}).join('\n\n')+'\n';
await fs.writeFile(path.join(out,'forward_model_mismatch_90_references.bib'),bib);
const ris=refs.map(r=>[
 `TY  - ${r['Publication type']==='Journal'?'JOUR':r['Publication type']==='Conference'?'CPAPER':'GEN'}`,
 `ID  - ${r['Study ID']}`,...authors(r).map(a=>`AU  - ${a}`),`PY  - ${r.Year}`,`TI  - ${r.Title}`,`T2  - ${r.Venue}`,`UR  - ${r['Primary source URL']}`,
 ...(r.DOI?[`DO  - ${r.DOI}`]:[]),`N1  - Evidence status: ${r['Evidence status']}; formal eligibility pending. AI pilot recommendations, where present, require human adjudication.`,`ER  -`
].join('\n')).join('\n\n')+'\n';
await fs.writeFile(path.join(out,'forward_model_mismatch_90_references.ris'),ris);
const md='# Forward-Model Mismatch Review: 90 Seed Publications\n\n> Draft seed references, not a PRISMA-included corpus or submission-ready bibliography. The first 40 received preliminary AI triage; all require human adjudication and full-text verification. Author lists outside verified corrections may remain abbreviated. See ../screening/pilot_02_report.md for evidence limits and corrected links.\n\n'+refs.map((r,i)=>`${i+1}. **${r['Study ID']}** — ${r.Authors} (${r.Year}). “${r.Title}.” *${r.Venue}*. [Primary source](${r['Primary source URL']})  \n   Evidence: ${r['Evidence status']}; formal eligibility: pending; closest competitor (provisional): ${r['Closest competitor']}.`).join('\n')+'\n';
await fs.writeFile(path.join(out,'forward_model_mismatch_90_bibliography.md'),md);
const audit={checked_on:batch.checked_on,baseline_local_commit:'8388877cdd36ce8672129b0a67ba995f71b9ca98',baseline_remote_commit:'00f33a9120b6ef8f4a59ec575f7cfd35ff93350b',baseline_workbook_blob:sha,note:'20 new AI recommendations and two unresolved revisits. No formal decisions or feature ratings changed. Source-backed targeted findings are separate from complete full-text eligibility.',changes,validation:{cumulative_triaged:40,advance:38,unclear:2,untriaged:50,formal_included:0,formal_excluded:0,formula_input_change_test:'passed',unintended_cell_changes:unintended,formula_errors:errors}};
await fs.writeFile(path.join(out,'pilot_02_changes.json'),JSON.stringify(audit,null,2)+'\n');
console.log(JSON.stringify(audit.validation,null,2));
