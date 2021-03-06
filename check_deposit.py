
####################################################################### 
# 
# # Author: romeo abulencia <romeo.abulencia@gmail.com> 
# Maintainer: romeo abulencia <romeo.abulencia@gmail.com> 
# # This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. 
# # This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details. 
# # You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>. 
#######################################################################
    


from openerp.osv import fields, osv
import time
from openerp.tools.translate import _
from openerp import netsvc



class glimsol_check_deposit(osv.osv):
    _name="glimsol.check.deposit"
    
    def check_deposit_save(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}

        
    def _get_check_number(self, cr, user, ids, name, attr, context=None):
        res = {}
        for obj in self.browse(cr, user, ids, context=context):
            res[obj.id]=len(obj.line_ids)
        return res    

    def _get_check_amount(self, cr, user, ids, name, attr, context=None):
        res = {}
        for obj in self.browse(cr, user, ids, context=context):
            res[obj.id]=sum([x.amount for x in obj.line_ids])
            if context and 'line_ids' in context:
                list_sum = []
                for x in context['line_ids']:
                    if x[0] == 4:
                        temp=self.pool.get('glimsol.check.deposit.line').read(cr,user,x[1],['amount'])
                        list_sum.append(temp['amount'])
                    elif x[2]:
                        if 'amount' in x[2]:
                            list_sum.append(x[2]['amount'])
                res[obj.id]=sum(list_sum)
#                 res[obj.id]=sum([x[2]['amount'] for x in context['line_ids'] if x[2]])
        return res        
    
    def _get_cleared_checks(self,cr,user,ids,name,attr,context=None):
        res={}
        
        for obj in self.browse(cr, user, ids, context=context):
            amount_list=[]
            for x in obj.line_ids:
                if x.state == 'paid':
                    amount_list.append(x.amount)
            res[obj.id]=sum(amount_list)
            if context and 'line_ids' in context:
                for x in context['line_ids']:
                    if x[0] == 4:
                        temp=self.pool.get('glimsol.check.deposit.line').read(cr,user,x[1],['amount','state'])
                        x[2]=temp                    
                    if x[2] and 'state' in x[2] and x[2]['state'] == 'paid':
                        if 'amount' in x[2] and x[2]['amount']:
                            amount_list.append(x[2]['amount'])
                res[obj.id]=sum(amount_list)            
        return res
    
    
    def _get_return_checks(self,cr,user,ids,name,attr,context=None):
        res={}
        
        for obj in self.browse(cr, user, ids, context=context):
            amount_list=[]
            for x in obj.line_ids:
                if x.state == 'returned':
                    amount_list.append(x.amount)
            res[obj.id]=sum(amount_list)
            if context and 'line_ids' in context:
                for x in context['line_ids']:
                    if x[0] == 4:
                        temp=self.pool.get('glimsol.check.deposit.line').read(cr,user,x[1],['amount','state'])
                        x[2]=temp                    
                    if x[2] and 'state' in x[2] and x[2]['state'] == 'returned':
                        amount_list.append(x[2]['amount'])
                res[obj.id]=sum(amount_list)                
            
        return res
    
    def onchange_line_ids(self,cr,uid,ids,line_ids,context=None):
        res={}
        if ids:
            res={'value':{
                          'cheque_number':len(line_ids),
                          'cheque_amount':self._get_check_amount(cr, uid, ids, '','',{'line_ids':line_ids})[ids[0]],
                          'cleared_checks':self._get_cleared_checks(cr, uid, ids, '','',{'line_ids':line_ids})[ids[0]],
                          'return_checks':self._get_return_checks(cr, uid, ids, '','',{'line_ids':line_ids})[ids[0]]
                          }}
        return res
    
    
    _columns={
              'partner_id':fields.many2one('res.partner', 'Customer', required=True),
              'invoice_id':fields.many2one('account.invoice', 'Invoice No.',required=True),
              'date': fields.date('Date'), 
              'line_ids':fields.one2many('glimsol.check.deposit.line', 'cd_id', 'Check Deposit', required=False),
              'cheque_number': fields.function(_get_check_number, method=True, type='integer', string='Total number of checks', store=False), 
              'cheque_amount':fields.function(_get_check_amount, method=True, type='float', string='Total amount of checks', store=False),
              'cleared_checks':fields.function(_get_cleared_checks,method=True,type='float', string="Total amount of checks cleared",store=False),
              'return_checks':fields.function(_get_return_checks,method=True,type='float',string="Total amount of return checks",store=False),
              'payment_ref':fields.char('Payment Ref',size=64, required=False, readonly=False),
              'memo':fields.char('Memo',size=64, required=False,redonly=False),              
              }
    _defaults={
        'date':time.strftime('%Y-%m-%d %H:%M:%S'),
                }    

class glimsol_check_deposit_line(osv.osv):
    _name="glimsol.check.deposit.line"
    
    def process_check_payment(self,cr,uid,cdl_id,context=None):
        if not isinstance(cdl_id,list):
            cdl_id = [cdl_id]
        for temp_id in cdl_id:
            obj=self.browse(cr,uid,temp_id)
            av_default_data=self.pool.get('account.voucher').default_get(cr,uid,['date','payment_rate','payment_rate_currency_id','company_id'])
            inv = obj.cd_id.invoice_id
            temp_context={
                    'payment_expected_currency': inv.currency_id.id,
                    'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                    'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                    'default_reference': inv.name,
                    'close_after_process': True,
                    'invoice_type': inv.type,
                    'invoice_id': inv.id,
                    'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                    'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
                }
            temp_av_data={
                     'partner_id':obj.cd_id.partner_id.id,
                     'journal_id':obj.journal_id.id,
                     'amount':obj.amount,
                     'currency_id':obj.cd_id.invoice_id.currency_id.id or [],
                     'type':inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
    #                 'date':
                     'context':temp_context,
    #                  'payment_rate'
    #                  'payment_rate_currency_id'
    #                  'company_id'
                     'line_cr_ids':[],
                     }
            av_data=av_default_data
            av_data.update(temp_av_data)
            #call onchange partner_id
            onchange_partner_id_result = self.pool.get('account.voucher').onchange_partner_id(cr,uid,[],av_data['partner_id'], av_data['journal_id'], av_data['amount'], av_data['currency_id'], av_data['type'], av_data['date'], av_data['context'])
            av_data.update(onchange_partner_id_result['value'])
            
            
            #call onchange_amount
            onchange_amount_result = self.pool.get('account.voucher').onchange_amount(cr,uid,[],av_data['amount'], av_data['payment_rate'], av_data['partner_id'], av_data['journal_id'], av_data['currency_id'], av_data['type'], av_data['date'], av_data['payment_rate_currency_id'], av_data['company_id'], av_data['context'])
            av_data.update(onchange_amount_result['value'])
    
            #call onchange_journal
            onchange_journal_result = self.pool.get('account.voucher').onchange_journal(cr,uid,[],av_data['journal_id'], av_data['line_cr_ids'], False, av_data['partner_id'], av_data['date'], av_data['amount'], av_data['type'], av_data['company_id'], av_data['context'])
            av_data.update(onchange_journal_result['value'])
            
            #reformat lines ids
            for x in ['line_cr_ids','line_dr_ids']:
                temp_list=[(0,0,elem) for elem in av_data[x]]
                av_data[x]=temp_list
                    
            vid=self.pool.get('account.voucher').create(cr,uid,av_data,context=context)
            temp =self.pool.get('account.voucher').proforma_voucher(cr,uid,[vid],context=context)
            #update connected cd_id.voucher_id 
            self.pool.get('glimsol.check.deposit.line').write(cr,uid,temp_id,{'voucher_id':vid})
        return True
        

    def write(self, cr, uid, ids, vals, context=None):
        result = super(glimsol_check_deposit_line, self).write(cr, uid, ids, vals, context=context)
        if vals and 'state' in vals and vals['state'] == 'paid':
            self.process_check_payment(cr,uid,ids)
        return result    
    
    def create(self, cr, uid, vals, context=None):
        result = super(glimsol_check_deposit_line, self).create(cr, uid, vals, context) 
        if vals and 'state' in vals and vals['state']=='paid':
            self.process_check_payment(cr,uid,[result])
        return result
    
    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        for deposit_line in self.browse(cr, uid, ids, context=context):
            if deposit_line.state == 'paid':
                raise osv.except_osv(_('User Error!'), _('You cannot delete paid checks.'))
        return super(glimsol_check_deposit_line, self).unlink(
            cr, uid, ids, context=ctx)

    def _get_period(self, cr, uid, context=None):
        if context is None: context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        ctx = dict(context, account_period_prefer_normal=True)
        periods = self.pool.get('account.period').find(cr, uid, context=ctx)
        return periods and periods[0] or False        
    
    def _get_journal(self,cr,uid,context=None):
        pool = self.pool.get
        
        #search for journals having a 'check' in their name
        cr.execute("select id from account_journal where type in ('bank','cash') and lower(name) like '%check%'")
        check_journals = [x[0] for x in cr.fetchall()]
        
        if not check_journals:
            cr.execute("select id from account_journal where type in ('bank') limit 1")
            check_journals=[x[0] for x in cr.fetchall()]

        res = []            
        if check_journals:
            res=check_journals[0]
        return res

    _columns={
              'cd_id':fields.many2one('glimsol.check.deposit','Check Deposit',required=False),
              'bank_id':fields.many2one('res.bank', 'Bank', required=True), 
              'check_number':fields.char('Check Number', size=64, required=True),
              'date': fields.date('Check Date'),
              'amount': fields.float('Amount', digits=(16, 2)),
              'journal_id':fields.many2one('account.journal', 'Payment Method', required=True ,domain=[('type','in',['bank'])]),
              'period_id':fields.many2one('account.period', 'Period', required=True),  
              'state':fields.selection([
                  ('pending','Pending'),
                  ('paid','Paid'),
                  ('returned','Returned'),
                   ],    'State', select=True, readonly=False),
              'voucher_id':fields.many2one('account.voucher','Voucher',),
              }
    
    _defaults = {  
        'state': 'pending',  
        'date':time.strftime('%Y-%m-%d %H:%M:%S'),
        'period_id':_get_period,
        'journal_id':_get_journal,
        }
    
class invoice(osv.osv):
    _inherit = 'account.invoice'
    _name="account.invoice"


    
    _columns={
              'check_deposit_ids':fields.one2many('glimsol.check.deposit', 'invoice_id', 'Check Deposit', required=False),
              }

    def invoice_check_deposit(self, cr, uid, ids, context=None):
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'glimsol_check', 'glimsol_check_deposit_form_view')

        inv = self.browse(cr, uid, ids[0], context=context)
        #check for existing check deposit entry
        target = self.pool.get('glimsol.check.deposit').search(cr,uid,[('invoice_id','=',inv.id)])
        res = {
            'name':_("Check Deposit"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'glimsol.check.deposit',
#            'res_id':target[0],
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                'default_invoice_id': inv.id,
            }
        }
        if target:
            res['res_id']=target[0]
        return res

invoice()    