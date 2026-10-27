"""Case-number lifecycle against the real local gateway/Next/Mongo stack."""
import csv
import io
import json
import uuid


def exercise_case_numbers(buyer, supplier, other, admin, original):
    def send(browser, path, report, source=None):
        values={'report':json.dumps(report)}
        if source: values.update(sourceId=source,keepDocuments='[]')
        boundary='SYNTHETIC_CASE_FORM'
        raw=''.join('--'+boundary+'\r\nContent-Disposition: form-data; name="'+k+'"\r\n\r\n'+v+'\r\n' for k,v in values.items())+'--'+boundary+'--\r\n'
        return browser.request(path,raw=raw.encode(),headers={'Content-Type':'multipart/form-data; boundary='+boundary})
    def approve(rid):
        code,out,_=admin.request('/api/report-review',{'id':rid,'status':'approved','notes':'Synthetic case-number review','identityChecked':True,'reportReviewed':True,'evidenceReviewed':False,'approvedForDisplay':True})
        assert code==200,(code,out)
    def searched():
        code,out,_=supplier.request('/api/seller-search',{'query':original['gstin']})
        assert code==200 and len(out['reports'])==1,(code,out)
        return out['reports'][0]
    report={**original,'legal':True,'caseNumber':'TMP-1/2026'}
    code,out,_=send(buyer,'/api/reports',report)
    assert code==400 and 'Choose Temporary' in out['error'],out
    code,out,_=send(buyer,'/api/reports',{**report,'caseNumberType':'invalid'})
    assert code==400,out
    report['caseNumberType']='temporary'
    code,out,_=send(buyer,'/api/reports',report)
    assert code==201,(code,out)
    rid=out['id']
    correction={**report,'requestId':str(uuid.uuid4()),'caseNumber':'TMP-2/2026'}
    code,out,_=send(buyer,'/api/report-edit',correction,rid)
    assert code==200 and out['id']==rid,(code,out)
    code,out,_=send(buyer,'/api/report-edit',correction,rid)
    assert code==200,(code,out)
    approve(rid)
    saved=searched()
    assert saved['case_number_type']=='temporary' and saved['case_number']=='TMP-2/2026',saved
    assert [x['number'] for x in json.loads(saved['case_number_history'])]==['TMP-1/2026'],saved
    permanent={**report,'requestId':str(uuid.uuid4()),'caseNumber':'REG-90/2026','caseNumberType':'permanent','case_number_history':'forged client history'}
    code,out,_=send(other,'/api/report-edit',permanent,rid)
    assert code in (403,409),(code,out)
    code,out,_=send(buyer,'/api/report-edit',permanent,rid)
    assert code==200 and out['revision'],(code,out)
    next_id=out['id']
    assert searched()['case_number']=='TMP-2/2026','Unapproved revision replaced approved result'
    code,html,_=buyer.request('/member/reports/'+next_id+'/edit')
    assert code==200 and 'REG-90/2026' in html and 'TMP-1/2026' in html and 'TMP-2/2026' in html,(code,str(html)[:200])
    code,out,_=buyer.request('/api/report-review',{'id':next_id,'status':'approved','notes':'not authorised'})
    assert code==403,(code,out)
    approve(next_id)
    saved=searched()
    assert saved['case_number_type']=='permanent' and saved['case_number']=='REG-90/2026',saved
    assert [x['number'] for x in json.loads(saved['case_number_history'])]==['TMP-1/2026','TMP-2/2026'],saved
    assert 'forged' not in saved['case_number_history']
    code,body,_=admin.request('/api/admin/export?type=reports')
    assert code==200,(code,body)
    row=next(row for row in csv.DictReader(io.StringIO(body.lstrip('\ufeff'))) if row['Case number']=='REG-90/2026')
    assert row['Case number type']=='Permanent / registered case number',row
    assert len(json.loads(row['Previous case numbers (JSON)']))==2,row
    assert buyer.request('/api/admin/export?type=reports')[0]==403
    print('PASS real case-number submission validation, pending correction/no duplicate history, ownership denial, permanent revision/admin approval, unchanged published version before approval, server-owned history and saved edit form',flush=True)
    return next_id
