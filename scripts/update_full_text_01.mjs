// One-time v0.7 -> v0.8 migration; preserves seed IDs, historic triage and formal decisions.
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {FileBlob, SpreadsheetFile, Workbook} from '@oai/artifact-tool';
const [repo,out]=process.argv.slice(2);
if(!repo||!out)throw new Error('Usage: node update_full_text_01.mjs REPO OUTPUT_DIR');
await fs.mkdir(out,{recursive:true});
const batch=JSON.parse(await fs.readFile(path.join(repo,'literature/screening/full_text_01.json'),'utf8'));
const input=path.join(repo,'literature/evidence_matrix_2020_2026.xlsx');
const bytes=await fs.readFile(input);
const sha=createHash('sha1').update(`blob ${bytes.length}\0`).update(bytes).digest('hex');
assert.equal(sha,'7a7dddfa82faeeaf243a4850005a75e76d91701b','Requires v0.7; must not overwrite a later checkpoint.');
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(input));
const matrix=wb.worksheets.getItem('Evidence Matrix'),log=wb.worksheets.getItem('Screening Log');
const summary=wb.worksheets.getItem('Summary'),protocol=wb.worksheets.getItem('Review Protocol'),dictionary=wb.worksheets.getItem('Coding Dictionary');
const csvWb=await Workbook.fromCSV(await fs.readFile(path.join(repo,'literature/references/forward_model_mismatch_90_references.csv'),'utf8'),{sheetName:'References'});
const csvValues=csvWb.worksheets.getItem('References').getUsedRange().values;
const headers=csvValues[0],refs=csvValues.slice(1).filter(r=>r[0]).map(r=>Object.fromEntries(headers.map((h,i)=>[h,r[i]??''])));
assert.equal(refs.length,90); assert.equal(batch.records.length,12);
const snapshots=[];
for(let i=0;i<5;i++){const s=wb.worksheets.getItemAt(i);snapshots.push({name:s.name,values:s.getRange('A1:AF101').values,formulas:s.getRange('A1:AF101').formulas});}
const changes=[],allowed=new Set(['Summary!E15','Summary!A22']);
function set(sheet,address,value,reason='AI full-text checkpoint'){
 const old=sheet.getRange(address).values[0][0];if(old===value)return;
 sheet.getRange(address).values=[[value]];allowed.add(`${sheet.name}!${address}`);
 changes.push({sheet:sheet.name,cell:address,old:old??null,new:value,reason});
}
// Mutate the existing rule, avoiding duplicate validations.
log.getRange('I2:J101').dataValidation.rule={type:'list',values:['Pending','Include','Exclude','Unclear','AI pilot: advance','AI pilot: unclear','AI full-text: include','AI full-text: exclude']};
for(const r of batch.records){
 const i=refs.findIndex(x=>x['Study ID']===r.study_id),row=i+2,ref=refs[i];
 assert(i>=0);assert.equal(matrix.getRange(`A${row}`).values[0][0],r.study_id);
 assert.equal(log.getRange(`J${row}`).values[0][0],'Pending');
 const status='AI full-text eligibility assessed; selected features verified';
 ref['Evidence status']=status;
 ref['Review notes']+=` | AI full-text ${batch.checked_on}: ${r.decision}; human pending. Verified fields: ${Object.keys(r.feature_codes).join(', ')}. Evidence/version/read extent: screening/full_text_01.json (${r.study_id}). Unlisted feature codes remain provisional.`;
 set(matrix,`Z${row}`,status);
 set(matrix,`AF${row}`,ref['Review notes']);
 for(const [col,value] of Object.entries(r.feature_codes)){
  assert(/^[O-X]$/.test(col));assert(['Yes','No','Partial'].includes(value));
  set(matrix,`${col}${row}`,value,`${r.study_id}: ${r.feature_locator}; ${r.source_url}`);
 }
 set(log,`J${row}`,`AI full-text: ${r.decision}`);
 set(log,`K${row}`,r.exclusion_reason??'');
 set(log,`L${row}`,`${batch.checked_on} | AI full-text ${r.decision}; human pending. ${r.decision==='exclude'?r.exclusion_detail:r.criteria['3'].evidence} Online text inspected; no local PDF saved. Version, read extent and technical extraction: screening/full_text_01.json (${r.study_id}).`);
 log.getRange(`J${row}`).format.fill=r.decision==='include'?'#E2F0D9':'#FCE4D6';
 log.getRange(`A${row}:N${row}`).format.rowHeight=144;
 log.getRange(`J${row}:N${row}`).format.wrapText=true;
 log.getRange(`A${row}:N${row}`).format.verticalAlignment='top';
 matrix.getRange(`A${row}:AF${row}`).format.rowHeight=176;
 matrix.getRange(`A${row}:AF${row}`).format.wrapText=true;
 matrix.getRange(`A${row}:AF${row}`).format.verticalAlignment='top';
}
set(log,'L17',`${log.getRange('L17').values[0][0]} Full-text 01: author PDF still fails to open; eligibility pending, not excluded. See full_text_01.json.`,'Record P016 retrieval failure without a false eligibility decision');
set(summary,'A10','Formal full-text assessments');
set(summary,'D15','AI full-text assessed');
summary.getRange('E15').formulas=[[`=COUNTIF('Screening Log'!J2:J101,"AI full-text: include")+COUNTIF('Screening Log'!J2:J101,"AI full-text: exclude")`]];
summary.getRange('D15:E15').format.fill='#E2F0D9';
summary.getRange('D15:E15').format.font.bold=true;
summary.getRange('D15:E15').format.rowHeight=30;
set(summary,'A17','PRISM: joint image/kernel uncertainty. No-Harm: conditional certificates and fallback. PnP: posterior mismatch bounds. nanoCT: operator error plus image variance. SURE: self-supervised calibration under stated assumptions. Details: screening/full_text_01_report.md.');
summary.getRange('A22').formulas=[[`="Initial triage: 90/90. AI full-text assessed: "&E15&"/90 ("&COUNTIF('Screening Log'!J2:J101,"AI full-text: include")&" include, "&COUNTIF('Screening Log'!J2:J101,"AI full-text: exclude")&" exclude); "&(B6-E15)&" remain. Human adjudication and formal inclusion pending. Novelty unestablished. Only explicitly logged features are verified."`]];
set(protocol,'B21','0.4 — operational AI full-text convention, 16 September 2026; not registered. Eligibility and search window unchanged.');
set(protocol,'B22','Initial triage 90/90 (82 advance, 8 unclear). AI full-text assessed: 12 (11 include, 1 exclude), 78 remain. All human adjudication and formal searches/inclusion pending. Formal inclusion/exclusion counts remain zero.');
set(protocol,'B23','90 seed records retained. Full-text progress: screening/full_text_01.json and full_text_01_report.md. AI decisions are recommendations. Evidence/version/read extent and verified feature fields are recorded per study; other codes remain provisional.');
set(dictionary,'B17',`${dictionary.getRange('B17').values[0][0]} / AI full-text eligibility assessed; selected features verified`);
set(dictionary,'C17','Full-text eligibility assessment means sufficient evidence for criteria, not a proof/code audit. Only explicitly logged feature fields are verified; other codes remain provisional. AI include/exclude in Screening Log J requires human adjudication; Evidence Matrix AA remains the formal decision.');
dictionary.getRange('A17:C17').format.rowHeight=160;
wb.recalculate();
assert.deepEqual(summary.getRange('E11:E14').values.flat(),[90,82,8,0]);
assert.equal(summary.getRange('E15').values[0][0],12);
const decision=log.getRange('J7').values[0][0];log.getRange('J7').values=[['Pending']];
assert.equal(summary.getRange('E15').values[0][0],11);
log.getRange('J7').values=[[decision]];wb.recalculate();
assert.equal(summary.getRange('E15').values[0][0],12);
assert.deepEqual(summary.getRange('B7:B12').values.flat(),[0,0,0,0,0,0]);
assert.equal(log.getRange('J2:J91').values.filter(r=>r[0]==='Pending').length,78);
assert.equal(log.getRange('J2:J91').values.filter(r=>r[0]==='AI full-text: include').length,11);
assert.equal(log.getRange('J2:J91').values.filter(r=>r[0]==='AI full-text: exclude').length,1);
assert.equal(matrix.getRange('AA2:AA91').values.filter(r=>r[0]==='Pending formal eligibility').length,90);
// Remaining validation and export routines are appended below.

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
for(const [name,range] of [['Summary','A5:E15'],['Summary','A16:H29'],['Screening Log','I61:N61'],['Screening Log','I85:L85'],['Evidence Matrix','O39:X39'],['Review Protocol','A21:B23'],['Coding Dictionary','A17:C17']]){
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
 ...(r.DOI?[`DO  - ${r.DOI}`]:[]),`N1  - Evidence status: ${r['Evidence status']}; formal eligibility pending. AI recommendations, where present, require human adjudication.`,`ER  -`
].join('\n')).join('\n\n')+'\n';
await fs.writeFile(path.join(out,'forward_model_mismatch_90_references.ris'),ris);
const md='# Forward-Model Mismatch Review: 90 Seed Publications\n\n> Draft seed references, not a PRISMA-included corpus or submission-ready bibliography. All 90 received preliminary AI triage: 82 advance, 8 unclear, 0 untriaged. 12 AI full-text assessments are complete (11 include recommendations, 1 exclude); 78 remain. Human adjudication and formal inclusion remain pending. Author lists outside verified corrections may remain abbreviated. See ../screening/full_text_01_report.md for evidence limits and corrected links.\n\n'+refs.map((r,i)=>`${i+1}. **${r['Study ID']}** — ${r.Authors} (${r.Year}). “${r.Title}.” *${r.Venue}*. [Primary source](${r['Primary source URL']})  \n   Evidence: ${r['Evidence status']}; formal eligibility: pending; closest competitor (provisional): ${r['Closest competitor']}.`).join('\n')+'\n';
await fs.writeFile(path.join(out,'forward_model_mismatch_90_bibliography.md'),md);
const audit={checked_on:batch.checked_on,baseline_workbook_blob:sha,note:'12 AI full-text decisions and source-backed feature corrections; historical triage and formal decisions preserved.',changes,validation:{...batch.counts,initial_triage:[90,82,8,0],formula_input_change_test:'passed',unintended_cell_changes:unintended,formula_errors:errors}};
await fs.writeFile(path.join(out,'full_text_01_changes.json'),JSON.stringify(audit,null,2)+'\n');
console.log(JSON.stringify(audit.validation,null,2));
