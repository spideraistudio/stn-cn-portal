"""Confirmed starting references. Activation requires explicit production confirmation."""
from copy import deepcopy

def bands(bounds, rates):
    return [{'above': str(0 if i == 0 else bounds[i-1]), 'upto': str(b), 'rate': str(r), 'name': ''} for i,(b,r) in enumerate(zip(bounds,rates))]
def periods(crop):
    ends, rates = {'Cotton':(['06-15','07-15','07-30','12-31'],[8,4,2,0]),'Maize':(['06-15','06-30','07-15','07-30','12-31'],[12,8,5,2,0]),'Bajra':(['06-30','07-15','07-31','12-31'],[7,5,3,0])}[crop]
    import datetime
    start='2026-04-01'; out=[]
    for end,rate in zip(ends,rates):
        end='2026-'+end; out.append({'start':start,'end':end,'percent':str(rate)})
        start=(datetime.date.fromisoformat(end)+datetime.timedelta(days=1)).isoformat()
    return out

def initial_settings():
    catalog=[('Cotton','Premium',['25D51','Advance','Agniveer'],'0.475','packet'),('Cotton','Deluxe',['D551','Dhanvarsha'],'0.475','packet'),('Bajra','Bajra',['14D88','14D99','14D14','14D14 Gold','14D41'],'1.5','kg'),('Maize','SingleCross',['32D12','Legend','Ranbanka'],'4','kg'),('Maize','DoubleCross',['32D55'],'4','kg'),('Maize','Threeway Cross',['Purnima'],'4','kg'),('Paddy','DAWAT 1 kg',['DAWAT'],'1','kg'),('Paddy','DAWAT 3 kg',['DAWAT'],'3','kg'),('Paddy','Research Paddy',['Janki Gold','Karina','Karishma'],'10','kg')]
    schemes=[]; products=[]
    for i,(crop,seg,names,pack,unit) in enumerate(catalog):
        sid='scheme-'+str(i+1)
        s={'id':sid,'segment_id':'segment-'+str(i+1),'version':1,'name':seg+' reference','crop':crop,'segment':seg,'states':['Gujarat'] if crop=='Cotton' else [],'season':'2026 season 1','confirmed':False,'unit':unit,'packing_kg':pack,'billing':'0','billing_unit':unit,'benefits':['ABS','Quantity','CD'],'quantity_mode':'whole','quantity':[], 'extra':[],'extra_unit':'fixed','token':None,'abs_rate':None,'abs_unit':unit,'abs_start':None,'abs_end':None,'extended_end':None,'cd':periods(crop if crop in ('Cotton','Maize','Bajra') else 'Cotton'),'return_threshold':'0','return_rate':'0','return_unit':unit,'net':[], 'cash':None,'narration':'{party} | {crop} | {segment} | {season} | {benefit}','remark':'Confirmed numerical reference. Enter and confirm production dates/state/season before use.'}
        if crop=='Cotton':
            s.update(billing='901',token='250',abs_rate='25')
            if seg=='Premium': s.update(benefits=['Net'],net=bands([300,500,1000,2500],[700,675,650,625]))
            else:s.update(benefits=['ABS','Quantity','CD','Extra','Return'],quantity=bands([300,500,1000,2500],[150,175,200,225]),extra=bands([300,500,1000,2500],[3950,15000,17500,50000]),return_threshold='10',return_rate='10')
        elif crop=='Bajra':
            s.update(billing='400',billing_unit='packet',token='50',abs_rate='10',benefits=['ABS','Quantity','CD','Extra'],quantity=bands([330,630,1050,1650,9999],[16,20,25,27,32]),extra=bands([330,630,1050,1650,9999],[15000,25000,35000,55000,65000]))
            for row,name in zip(s['extra'],['Ranthambore','Ujjain','Kashmir Single','Thailand Couple','Foreign Couple']):row['name']=name
        elif crop=='Maize':
            s.update(billing='350' if seg=='SingleCross' else '160' if seg=='Threeway Cross' else '140',token='50' if seg=='SingleCross' else '40',abs_rate='10',quantity=bands([200,500,1200,2500,5000],[2.5,5,7,10,15]) if seg=='SingleCross' else bands([500,1500,2500],[10,15,20]))
            if seg=='SingleCross':s.update(benefits=['ABS','Quantity','CD','Extra','Return'],extra=[{'above':'1500','inclusive':True,'upto':'2999','rate':'25000','name':'Extra 25,000'},{'above':'3000','inclusive':True,'upto':None,'rate':'50000','name':'Extra 50,000'}],return_rate='10',return_unit='packet')
            if seg=='DoubleCross':s['cash']={'start':'2026-03-12','end':'2026-03-31','advance':'100','cn_rate':'40','unit':'kg','products':['32D55']}
        elif seg.startswith('DAWAT'):
            s.update(billing='300',token='100',abs_rate='25',quantity=bands([330,630,1050,1650,9999],[16,20,25,27,32]))
        else:s.update(billing='70',token='25',abs_rate='2.5',benefits=['ABS','CD'])
        s['products']=[]
        for name in names:
            pid=f'p{len(products)+1}';s['products'].append(pid)
            products.append({'id':pid,'segment_id':'segment-'+str(i+1),'name':name,'crop':crop,'segment':seg,'packing_kg':pack,'scheme':sid,'aliases':[]})
        schemes.append(s)
    return {'version':1,'seasons':[{'name':'2026 season 1','start':None,'end':None,'cutoff':None,'confirmed':False}], 'products':products,'schemes':schemes,'rounding':'Separate nearest rupee, half up'}
