import {test} from 'node:test';
import assert from 'node:assert/strict';
import {renderToStaticMarkup} from 'react-dom/server';
import {updatedCaseNumbers, caseNumberHistory} from '../lib/case-numbers';
import {CaseNumberInfo} from '../components/case-number-info';

test('temporary to permanent keeps history; unchanged saves do not add duplicates', () => {
  const temp=updatedCaseNumbers({legal:true,caseNumber:'TMP-12/2026',caseNumberType:'temporary'},undefined,10);
  const source={case_number:temp.number,case_number_type:temp.type,case_number_history:temp.history};
  const next=updatedCaseNumbers({legal:true,caseNumber:'REG-90/2026',caseNumberType:'permanent'},source,20);
  assert.deepEqual(caseNumberHistory(next.history),[{number:'TMP-12/2026',type:'temporary',replaced_at:20}]);
  assert.equal(updatedCaseNumbers({legal:true,caseNumber:'REG-90/2026',caseNumberType:'permanent'}, {case_number:next.number,case_number_type:next.type,case_number_history:next.history},30).history,next.history);
  assert.equal(source.case_number,'TMP-12/2026');
});
test('legacy type stays unspecified until explicitly reviewed', () => {
  const source={case_number:'OLD-12'};
  assert.equal(updatedCaseNumbers({legal:true,caseNumber:'OLD-12',caseNumberType:'unspecified'},source).type,'unspecified');
  assert.throws(()=>updatedCaseNumbers({legal:true,caseNumber:'NEW-12',caseNumberType:'unspecified'},source),/Choose Temporary/);
  assert.throws(()=>updatedCaseNumbers({legal:true,caseNumber:'NEW-12',caseNumberType:'unspecified'}),/Choose Temporary/);
  const next=updatedCaseNumbers({legal:true,caseNumber:'OLD-12',caseNumberType:'permanent'},source,30);
  assert.equal(caseNumberHistory(next.history)[0].type,'unspecified');
});
test('pending corrections and removal preserve earlier case references', () => {
  const first={case_number:'TMP-1',case_number_type:'temporary'};
  const corrected=updatedCaseNumbers({legal:true,caseNumber:'TMP-2',caseNumberType:'temporary'},first,20);
  const removed=updatedCaseNumbers({legal:false,caseNumber:'',caseNumberType:'unspecified'}, {case_number:corrected.number,case_number_type:corrected.type,case_number_history:corrected.history},30);
  assert.equal(removed.number,null);
  assert.deepEqual(caseNumberHistory(removed.history).map(x=>x.number),['TMP-1','TMP-2']);
});
test('number type and escaped history render consistently', () => {
  const html=renderToStaticMarkup(<CaseNumberInfo report={{case_number:'P<1>',case_number_type:'permanent',case_number_history:JSON.stringify([{number:'T<script>',type:'temporary',replaced_at:10}])}}/>);
  assert.match(html,/Permanent \/ registered case number/); assert.match(html,/Temporary \/ filing number/);
  assert.match(html,/P&lt;1&gt;/); assert.doesNotMatch(html,/<script>/);
  assert.match(renderToStaticMarkup(<CaseNumberInfo report={{case_number:'OLD'}}/>),/type not specified/);
});
