import {NextResponse} from 'next/server';
import {ObjectId} from 'mongodb';
import {portalIdentity} from '@/lib/portal-session';
import {mongoDb} from '@/lib/sql-mongo';
import {parseMemberId} from '@/lib/member-data';
export async function GET(request:Request){
 const identity=await portalIdentity();if(!identity||identity.role!=='superadmin'&&!(identity.role==='admin'&&identity.modules.stn&&identity.stn_member_id===new URL(request.url).searchParams.get('id')))return NextResponse.json({error:'Platform superadmin required'},{status:403});
 const id=parseMemberId(new URL(request.url).searchParams.get('id'));
 if(id==null)return NextResponse.json({exists:false},{status:400});
 const row=await(await mongoDb()).collection('members').findOne({_id:typeof id==='string'?new ObjectId(id):id} as never,{projection:{company_name:1,status:1}});
 return NextResponse.json({exists:!!row,member_id:String(id),company_name:row?.company_name,status:row?.status},{headers:{'Cache-Control':'no-store'}});
}
