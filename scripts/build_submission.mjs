import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { constants as fsConstants } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { money } from '../web/format.js';

const project = 'D:/projects/vultre';
const out = path.join(project, 'submission', 'agent-rush');
const build = path.join(out, '.build');
const revision = new Date().toISOString().replaceAll(':','-').replaceAll('.','-');
const validatedPath = path.join(out,'.validated',`prooflane-deck-${revision}.pptx`);
const validationPath = path.join(build,`validation-${revision}.json`);
const skill = 'C:/Users/nural/.codex/plugins/cache/openai-primary-runtime/presentations/26.1105.12137/skills/presentations';
const runtimeModules = 'C:/Users/nural/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const runtimePython = 'C:/Users/nural/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
process.env.RUNTIME_NODE_MODULES = runtimeModules;
const { importRuntimeModule } = await import(pathToFileURL(path.join(skill, 'container_tools/runtime_helpers.mjs')).href);
const { Presentation, PresentationFile, FileBlob } = await importRuntimeModule('@oai/artifact-tool');
const { finalizePresentation, resolvePresentationFont } = await import(pathToFileURL(path.join(skill, 'container_tools/artifact_tool_utils.mjs')).href);
const bodyFont = resolvePresentationFont({ fontFamily: 'Segoe UI' });
const titleFont = resolvePresentationFont({ fontFamily: 'Georgia' });
const C = { paper:'#EDF2F3',white:'#FAFCFC',ink:'#162633',navy:'#173238',olive:'#346C68',teal:'#215B58',soft:'#DBEBE9',muted:'#465B65',line:'#BDCDD1',orange:'#9D4A29' };
await fs.mkdir(build, { recursive: true });
await fs.mkdir(path.join(out,'.validated'), { recursive: true });
const nativeLink=fs.link.bind(fs);
fs.link=async(source,destination)=>{
 try { return await nativeLink(source,destination); }
 catch(error){
  const validated=path.resolve(out,'.validated');
  if(error.code!=='EPERM'||path.dirname(path.resolve(source))!==validated||path.dirname(path.resolve(destination))!==validated)throw error;
  await fs.copyFile(source,destination,fsConstants.COPYFILE_EXCL);
 }
};
const deck = Presentation.create({slideSize:{width:1600,height:900}});
const evidence=path.join(project,'artifacts/vultr-release');
const packetPath=path.join(evidence,'sandbox-multi-range-case.json');
const packet=JSON.parse(await fs.readFile(packetPath,'utf8'));
const verifyPacket=spawnSync(path.join(project,'.venv/Scripts/python.exe'),[path.join(project,'scripts/verify_receipt.py'),packetPath],{cwd:project,encoding:'utf8'});
if(verifyPacket.status!==0||!JSON.parse(verifyPacket.stdout).passed)throw new Error(verifyPacket.stderr||verifyPacket.stdout||'Case packet failed verification');
const cloud=JSON.parse(await fs.readFile(path.join(evidence,'case-http-smoke.json'),'utf8'));
if(!cloud.passed||!cloud.containment?.passed||cloud.model_calls!==0)throw new Error('Missing actual Vultr Docker evidence');
const sample=cloud.cases.find(item=>item.mode==='sandbox');
let live=null;
try { live=JSON.parse(await fs.readFile(path.join(evidence,'live-evidence.json'),'utf8')); }
catch(error) { if(error.code!=='ENOENT')throw error; }
const liveVerified=live?.passed===true&&live?.model_calls>0;
const liveLabel=liveVerified ? 'Live Inference verified' : 'Live Inference awaiting validation';
let serial=0;
function txt(slide,value,x,y,w,h,size=28,color=C.ink,bold=false,font=bodyFont){
  const s=slide.shapes.add({geometry:'textbox',name:`text-${++serial}`,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  s.text=value;s.text.style={typeface:font,fontSize:size,color,bold,verticalAlignment:'top',alignment:'left',insets:0};
  return s;
}
function line(slide,x,y,w,color=C.line){return slide.shapes.add({geometry:'line',position:{left:x,top:y,width:w,height:0},line:{fill:color,width:1.2}});}
function base(title,number,dark=false){const s=deck.slides.add();s.background.fill=dark?C.navy:C.paper;txt(s,'Prooflane',76,40,300,45,28,dark?C.soft:C.teal,true);txt(s,String(number).padStart(2,'0'),1465,44,60,35,18,dark?'#B5C5AC':C.muted);if(title)txt(s,title,76,130,1440,90,52,dark?C.white:C.ink,false,titleFont);line(s,76,823,1448,dark?'#40584B':C.line);txt(s,'VULTR AGENT RUSH   ·   BLAST RADIUS ZERO   ·   NOVEMBER 2026',76,843,1100,26,15,dark?'#B5C5AC':C.muted);return s;}
async function img(slide,file,x,y,w,h){const b=await fs.readFile(file);slide.images.add({blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:file.endsWith('.png')?'image/png':'image/jpeg',alt:'Actual Prooflane screenshot from the public Vultr deployment',fit:'contain',position:{left:x,top:y,width:w,height:h}});}
function table(slide,values,x,y,w,h,widths){const t=slide.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,columnWidths:widths,values});t.borders.assign({fill:C.line,width:1,style:'solid'});for(let r=0;r<values.length;r++){t.rows[r].height=h/values.length;for(let c=0;c<values[0].length;c++){const cell=t.getCell(r,c);cell.fill=r===0?C.navy:r===values.length-1&&values[r][0]==='Total'?C.soft:C.white;cell.text.style={typeface:bodyFont,fontSize:r===0?22:25,color:r===0?C.white:C.ink,bold:r===0||values[r][0]==='Total'};}}return t;}
function diagramBox(slide,title,subtitle,x,y,w,h){const b=slide.shapes.add({geometry:'rect',name:`architecture-${++serial}`,position:{left:x,top:y,width:w,height:h},fill:C.white,line:{fill:C.line,width:1.5}});txt(slide,title,x+22,y+24,w-44,38,26,C.teal,true);txt(slide,subtitle,x+22,y+75,w-44,h-88,22,C.muted);return b;}
function arrow(slide,x,y,w){slide.shapes.add({geometry:'rightArrow',position:{left:x,top:y,width:w,height:21},fill:C.olive,line:{fill:'none',width:0}});}
const shot=path.join(project,'artifacts/vultr-prooflane-ledger.jpg');
const containmentShot=path.join(evidence,'containment.jpg');

// The six slides follow one fictional case and use the deployed build's evidence.
{
 const s=base('',1);
 txt(s,'Which contract price\nsupports this invoice?',76,176,700,194,60,C.ink,false,titleFont);
 txt(s,'Prooflane gives accounts payable reviewers a way to trace a price dispute and hand it over with the evidence intact.',80,420,600,172,32,C.muted);
 txt(s,'Live demo  ·  https://45.76.92.198/',80,680,620,46,24,C.teal,true);
 await img(s,shot,715,174,809,550);
 s.speakerNotes.text='The screenshot shows the public HTTPS application on the Vultr VM with the fictional case and a fixed Docker recipe. Source: artifacts/vultr-prooflane-ledger.jpg and TESTING.md.';
}
{
 const s=base('The review records which invoices count',2);
 txt(s,'Eight invoices arrive with two unresolved contract matches.',80,236,1400,49,28,C.muted);
 txt(s,'INV504',80,336,220,55,34,C.teal,true);
 txt(s,'Two effective contract versions overlap. The reviewer selects C2R.',320,336,1150,64,30,C.ink);
 line(s,80,421,1440);
 txt(s,'INV506',80,455,220,55,34,C.teal,true);
 txt(s,'No supplied contract covers the invoice date. The reviewer records the reason for exclusion.',320,455,1100,101,30,C.ink);
 line(s,80,578,1440);
 txt(s,'7 of 8 included',80,625,600,92,57,C.teal,false,titleFont);
 txt(s,'The exported packet keeps both decisions and their sources.',741,646,725,110,28,C.muted);
 s.speakerNotes.text='Fictional data. The source match uses exact vendor and item keys and inclusive contract dates. On INV504 choose C2R; on INV506 enter a reason for exclusion. Prooflane retains the excluded record without a calculated amount. Source: artifacts/vultr-release/sandbox-multi-range-case.json.';
}
{
 const s=base('A disputed price changes three invoices',3);
 table(s,[['Case','Inputs','Positive variance'],['Original','Supplied contract prices',money(sample.baseline)],['Shared price','C1 at $80',money(sample.alternatives[0])],['Price and volume','C1 at $80, INV501 at 80 units',money(sample.alternatives[1])]],80,248,1440,330,[340,720,380]);
 const range=sample.multi_range;
 txt(s,`Declared bounds put the total between ${money(range.low)} and ${money(range.high)}.`,82,622,1410,54,33,C.teal,true);
 txt(s,'Confirming C1 removes at least $645 of that range, given these bounds.',82,708,1410,64,27,C.muted);
 s.speakerNotes.text='The signed scope is seven included invoices. C1 is used by normalized records 2, 3 and 8. To reproduce the range, set C1 to 65–85 and INV501 quantity to 20–80. The $645 guaranteed reduction follows only under these declared bounds. Amounts are fictional and express positive price variance. Source: artifacts/vultr-release/case-http-smoke.json and sandbox-multi-range-case.json.';
}
{
 const s=base('The Vultr VM controls each execution',4);
 txt(s,`Public HTTPS and Docker verified. ${liveLabel}.`,80,234,1440,64,28,C.muted);
 diagramBox(s,'Browser','Reconcile source rows\nReview results',80,345,325,195);
 arrow(s,425,427,54);
 diagramBox(s,'Vultr VM','FastAPI and SQLite\nIndependent Decimal checks',499,345,490,195);
 arrow(s,1009,427,54);
 diagramBox(s,'Disposable Docker','Executes bounded Python\nReturns output, then is removed',1083,345,437,195);
 txt(s,'Vultr Serverless Inference',500,597,950,53,30,C.teal,true);
 txt(s,'The server requests a Python plan. Invoice rows go to the offline container.',500,661,960,106,27,C.ink);
 s.speakerNotes.text='Caddy terminates public HTTPS. The application and data store run on a dedicated Vultr VM. Agent mode sends a fixed task and row count to Vultr Inference for Python. The server validates returned JSON and can request one bounded repair. Sandbox mode executes the fixed recipe. Source: prooflane/provider.py, prooflane/sandbox.py, deploy/prooflane.service, TESTING.md. '+liveLabel+'.';
}
{
 const s=base('The evidence survives the demo',5);
 table(s,[['Evidence','What the independent verifier reconstructs'],['Sources','Dated contract matches, selections and exclusions'],['Calculations','Original and alternative results, exact ranges and priorities'],['Integrity','Receipt links and packet hashes']],80,239,1440,326,[370,1070]);
 txt(s,'A false priority value was rejected even after its hash was recomputed.',80,616,1420,62,32,C.teal,true);
 txt(s,'python scripts/verify_receipt.py prooflane-case.json',80,716,1410,54,24,C.muted);
 s.speakerNotes.text='Public smoke reproduced the negative control by changing the stated information value to 99999.00 and recomputing the top-level hash. The verifier independently reconstructed the evidence and rejected it. Verification covers content integrity and supported arithmetic. It does not authenticate the issuer, establish contract truth or attest to the host. Source: scripts/smoke_case.py and artifacts/vultr-release/case-http-smoke.json.';
}
{
 const s=base('Prooflane fits disputed supplier prices',6);
 txt(s,'Start with AP teams that already export invoice and contract tables.',80,228,1390,62,32,C.ink);
 txt(s,'Reviewers can prioritize which contract to confirm and send the case to procurement.',80,342,635,165,32,C.ink);
 txt(s,'Next validation: time how long a second reviewer takes to reproduce an exception using a spreadsheet or a Prooflane packet.',80,557,610,181,28,C.muted);
 await img(s,containmentShot,730,330,794,417);
 txt(s,`Vultr containment check: ${cloud.containment.checks.length} observed checks passed`,748,753,775,44,22,C.teal,true);
 s.speakerNotes.text='Business value is a hypothesis for existing accounts payable and procurement workflows. No customer adoption, time saved or recovered cash was measured. A team subscription for repeat exception review is a pricing hypothesis. During the recorded demo run Proof → Run containment check and read the observed filesystem and cleanup results. Source: docs/AGENT_RUSH_READINESS.md and artifacts/vultr-release/containment.jpg.';
}
const requirements={explicitTotalSlideCount:6,requiredNativeTableOwnerSlides:[3,5],requiredNativeChartOwnerSlides:[]};
const fontPolicy={basis:'design',families:[bodyFont,titleFont]};
const candidate=path.join(build,'candidate.pptx');
await (await PresentationFile.exportPptx(deck)).save(candidate);
console.log(JSON.stringify({stage:'candidate',path:candidate}));
await fs.writeFile(path.join(build,'deck.proto.json'),JSON.stringify(deck.toProto()));
const result=await finalizePresentation({...requirements,workspaceDir:project,candidatePath:candidate,finalPath:validatedPath,pythonExecutable:runtimePython,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','15240000,8572500','--validate-bullet-geometry','--validate-heading-fit','--require-native-table-slide','3','--require-native-table-slide','5'],fontPolicy,verifyArtifactToolImport:true,receiptPath:validationPath});
console.log(JSON.stringify({stage:'finalizer',result}));
await fs.copyFile(validationPath,path.join(build,'validation.json'));
await fs.copyFile(validatedPath,path.join(out,'prooflane-deck.pptx'));
const finalDeck=await PresentationFile.importPptx(await FileBlob.load(path.join(out,'prooflane-deck.pptx')));
for(const [index,slide] of finalDeck.slides.items.entries()){
 const png=await finalDeck.export({slide,format:'png',scale:1});
 await fs.writeFile(path.join(build,`slide-${index+1}.png`),new Uint8Array(await png.arrayBuffer()));
}
const cover=await finalDeck.export({slide:finalDeck.slides.items[0],format:'png',scale:1});
await fs.writeFile(path.join(out,'cover.png'),new Uint8Array(await cover.arrayBuffer()));
try {
 const pdf=await finalDeck.export({format:'pdf'});
 await fs.writeFile(path.join(out,'prooflane-deck.pdf'),new Uint8Array(await pdf.arrayBuffer()));
} catch(error) {
 if(!String(error.message).includes('#standard-fonts/'))throw error;
 await fs.writeFile(path.join(build,'pdf-export-fallback.json'),JSON.stringify({reason:error.message,fallback:'Bundled ReportLab assembles validated PNGs; editable objects remain in PPTX.'},null,2));
 const pdfBuild=spawnSync(runtimePython,[path.join(project,'scripts/build_submission_pdf.py'),'--output-dir',out],{cwd:project,encoding:'utf8'});
 if(pdfBuild.status!==0)throw new Error(pdfBuild.stderr||'PDF fallback failed');
 console.log(pdfBuild.stdout.trim());
}
console.log(JSON.stringify({stage:'complete',slides:finalDeck.slides.items.length,files:['prooflane-deck.pptx','prooflane-deck.pdf','cover.png'],screenshot:shot}));
