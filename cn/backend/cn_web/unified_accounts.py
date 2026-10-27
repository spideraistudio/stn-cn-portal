"""Transactional unified provisioning; pending signup identities stay disabled."""
import hashlib
import json
from .security import AuthError, verify_password

class UnifiedAccounts:
    def provision(self, token, body, member=None):
        allowed={'username','temporary_password','permissions','quota_bytes','max_users','user_quota_bytes','cn','stn','plan','starts_at','ends_at','member_id','parent_admin'}
        if set(body)-allowed:raise AuthError('Unsupported account field',400)
        for k in ('cn','stn'):
            if type(body.get(k)) is not bool:raise AuthError('Choose CN/STN access',400)
        with self._tx() as db:
            actor=self._session(db,token,admin=True)
            if member:
                if actor['role']!='superadmin':raise AuthError('Platform superadmin required',403)
                mid=str(body.get('member_id',''))
                digest=hashlib.sha256(json.dumps({k:v for k,v in body.items() if k!='temporary_password'},sort_keys=True).encode()).hexdigest()
                previous=db.execute('SELECT user_id,config_digest FROM portal_provisioning WHERE member_id=?',(mid,)).fetchone()
                if previous:
                    user=self._user(db,previous[0])
                    if previous['config_digest']!=digest or user['username']!=self.username(body['username']) or not verify_password(body['temporary_password'],user['password_hash']):raise AuthError('This request already has an account. Use its original submitted credentials to retry, or Edit access.',409)
                    return {'user_id':user['id'],'prepared':True}
                if member.get('status') not in ('pending','approved','cn_only'):raise AuthError('Membership is not eligible for approval',409)
                if db.execute('SELECT 1 FROM portal_memberships WHERE stn_member_id=?',(mid,)).fetchone():raise AuthError('Membership already linked. Use Edit access.',409)
                company=self.company(token,{'name':member['company_name'],'cn':body['cn'],'stn':body['stn'],'plan':body.get('plan','Both' if body['cn'] and body['stn'] else 'CN-only' if body['cn'] else 'STN-only'),'starts_at':body.get('starts_at'),'ends_at':body.get('ends_at')})
                user=self.create_user(token,username=body['username'],temporary_password=body['temporary_password'],permissions=body['permissions'],role='admin',quota_bytes=body.get('quota_bytes',1024**3),max_users=body.get('max_users',5),user_quota_bytes=body.get('user_quota_bytes',250*1024**2))
                self.access(token,{'user_id':user['id'],'company_id':company['id'],'cn':body['cn'],'stn':body['stn'],'stn_member_id':mid})
                db.execute('UPDATE workspaces SET enabled=0 WHERE user_id=?',(user['id'],))
                db.execute('INSERT INTO portal_provisioning VALUES(?,?,0,?)',(mid,user['id'],digest))
            else:
                parent=body.get('parent_admin') if actor['role']=='superadmin' else actor['id']
                if not parent:raise AuthError('Choose the company admin for this staff user',400)
                parent_row=self._user(db,parent)
                if not parent_row:raise AuthError('Company admin not found',404)
                from . import account_roles as roles
                policy=self._policy(db,roles.public(db,self._public_user(parent_row)))
                user=self.create_user(token,username=body['username'],temporary_password=body['temporary_password'],permissions=body['permissions'],parent_admin=parent,quota_bytes=body.get('quota_bytes'))
                changes={'user_id':user['id'],'cn':body['cn'],'stn':body['stn']}
                if body['stn']:
                    if not policy['stn'] or not policy['stn_member_id']:raise AuthError('Company admin needs an approved linked STN membership first',409)
                    changes['stn_member_id']=policy['stn_member_id']
                self.access(token,changes)
            db.execute('UPDATE users SET must_change=1 WHERE id=?',(user['id'],))
            self.audit(db,actor['id'],'unified_account_prepared',user['id'],signup=bool(member))
            return {'user_id':user['id'],'prepared':bool(member)}

    def activate_provision(self,token,member):
        with self._tx() as db:
            actor=self._session(db,token,admin=True)
            if actor['role']!='superadmin':raise AuthError('Platform superadmin required',403)
            if member.get('status') not in ('approved','cn_only'):raise AuthError('STN approval is not complete. Retry approval.',409)
            row=db.execute('SELECT * FROM portal_provisioning WHERE member_id=?',(member['member_id'],)).fetchone()
            if not row:raise AuthError('Prepared account not found',404)
            if not row['completed']:
                db.execute('UPDATE workspaces SET enabled=1 WHERE user_id=?',(row['user_id'],))
                db.execute('UPDATE portal_provisioning SET completed=1 WHERE member_id=?',(member['member_id'],))
                self.audit(db,actor['id'],'unified_signup_completed',row['user_id'])
            return {'created':True,'user_id':row['user_id']}
