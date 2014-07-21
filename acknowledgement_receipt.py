
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
from num2words import num2words

class glimsol_acknowledgment_receipt(osv.osv):
    _name="glimsol.acknowledgment.receipt"
    
    def print_report(self, cr, uid, ids, context=None):
        datas = {
             'ids': [],
             'active_ids': context['active_ids'],
             'model': 'glimsol.acknowledgment.receipt',
             'form': self.read(cr, uid, ids)[0]
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hr.attendance.bymonth',
            'datas': datas,
        }    
    
    def _get_total_cash_amount(self, cr, user, ids, name, attr, context=None):
        print "_get_total_cash_amount".upper()
        res = {}
        for statement in self.browse(cr, user, ids, context=context):
            print "statement.invoice_id".upper(),statement.invoice_id
            pass
        return res
    def _get_check_amount(self, cr, user, ids, name, attr, context=None):
        res = {}
        for statement in self.browse(cr, user, ids, context=context):
            pass
        return res    
    
    def _get_check_number(self, cr, user, ids, name, attr, context=None):
        res = {}
        for statement in self.browse(cr, user, ids, context=context):
            pass
        return res
    
    def _get_check_number(self, cr, user, ids, name, attr, context=None):
        res = {}
        for statement in self.browse(cr, user, ids, context=context):
            pass
        return res
    
    def _get_amount_in_words(self, cr, user, ids, name, attr, context=None):
        res = {}
        for statement in self.browse(cr, user, ids, context=context):
            pass
        return res    
    
    _columns={
              'total_cash_amount':fields.function(_get_total_cash_amount, method=True, type="float", string='Total Cash Amount', store=False), 
              'total_check_amount':fields.function(_get_check_amount, method=True, type='float', string='Total Check Amount', store=False),
              'total_check_number':fields.function(_get_check_number, method=True, type='float', string='Total Check Number', store=False),
              'journal_id':fields.many2one('account.journal', 'Payment Method', required=True ,domain=[('type','in',['bank','cash'])]),
              'total_amount_in_words': fields.function(_get_amount_in_words, method=True, type='char', string='Total Amount in Words', store=False),
              'payment_description':fields.char('Payment Description',size=64),
              'notes':fields.text('Notes/Remarks'),
              
              'date': fields.date('Check Date'),
              'cdos_reference':fields.char('CDOS Reference',size=64),
              'invoice_id':fields.many2one('account.invoice','Invoice Reference',required=True),
              'recieve_user_id':fields.many2one('res.partner','Received By',required=True),
              }
    
class invoice(osv.osv):
    _inherit = 'account.invoice'
    _name="account.invoice"
    
    def _glimsol_get_val(self,cr,uid,trigger,inv_obj):
        res = False
        if trigger == 'total_cash_amount':
#             for payment in inv_obj.payment_ids:
            target_cash_journal_ids=self.pool.get('account.journal').search(cr,uid,[('type','=','cash')])
            target_payment_ids=self.pool.get('account.move.line').search(cr,uid,[('journal_id','in',target_cash_journal_ids),('id','in',[x.id for x in inv_obj.payment_ids])])
            target_payment_objs=self.pool.get('account.move.line').browse(cr,uid,target_payment_ids)
            res = sum([x.credit for x in target_payment_objs])
            
        elif trigger in ['total_check_amount','total_check_number']:
            print "total_check_amount".upper()
            check_deposit_ids = self.pool.get('glimsol.check.deposit').search(cr,uid,[('invoice_id','=',inv_obj.id)])
            if check_deposit_ids:
                if trigger == 'total_check_amount':
                    res = self.pool.get('glimsol.check.deposit').read(cr,uid,check_deposit_ids[0],['cheque_amount'])['cheque_amount']
                elif trigger == 'total_check_number':
                    res = self.pool.get('glimsol.check.deposit').read(cr,uid,check_deposit_ids[0],['cheque_number'])['cheque_number']
        elif trigger == 'total_amount_in_words':
            temp_amount = self._glimsol_get_val(cr, uid, 'total_cash_amount', inv_obj)+self._glimsol_get_val(cr, uid, 'total_check_amount', inv_obj)
            res = num2words(temp_amount)
        return res

    def invoice_acknowledgment_receipt(self, cr, uid, ids, context=None):
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'glimsol_check', 'glimsol_acknowledgment_receipt_form_view')

        inv = self.browse(cr, uid, ids[0], context=context)
        #check for existing check deposit entry
        target = self.pool.get('glimsol.acknowledgment.receipt').search(cr,uid,[('invoice_id','=',inv.id)])
        
        res = {
            'name':_("Acknowledgment Receipt"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'glimsol.acknowledgment.receipt',
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
            
        if inv.check_deposit_ids:
            check_deposit_obj= inv.check_deposit_ids[0]
            temp_dict={'default_total_cash_amount':self._glimsol_get_val(cr,uid,'total_cash_amount',inv),
                       'default_total_check_amount':self._glimsol_get_val(cr,uid,'total_check_amount',inv),
                       'default_total_check_number':self._glimsol_get_val(cr,uid,'total_check_number',inv),
                       'default_total_amount_in_words':self._glimsol_get_val(cr,uid,'total_amount_in_words',inv),}
            res['context'].update(temp_dict)
        return res

invoice()        