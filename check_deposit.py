
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


class glimsol_check_deposit(osv.osv):
    _name="glimsol.check.deposit"
    
    _columns={
              'partner_id':fields.many2one('res.partner', 'Customer', required=True),
              'invoice_id':fields.many2one('account.invoice', 'Invoice No.',required=True),
              'date': fields.date('Date'), 
              'line_ids':fields.one2many('glimsol.check.deposit.line', 'cd_id', 'Check Deposit', required=False),
              
               
              }
    _defaults={
        'date':time.strftime('%Y-%m-%d %H:%M:%S'),
                }    

class glimsol_check_deposit_line(osv.osv):
    _name="glimsol.check.deposit.line"
    
    _columns={
              'cd_id':fields.many2one('glimsol.check.deposit','Check Deposit',required=False),
              'bank_id':fields.many2one('res.bank', 'Bank', required=True), 
              'check_number':fields.char('Check Number', size=64, required=True),
              'date': fields.date('Check Date'),
              'amount': fields.float('Amount', digits=(16, 2)),
              'journal_id':fields.many2one('account.journal', 'Payment Method', required=True ,domain=[('type','in',['bank','cash'])]),
              'period_id':fields.many2one('account.period', 'Period', required=True),  
              'state':fields.selection([
                  ('pending','Pending'),
                  ('paid','Paid'),
                  ('returned','Returned'),
                   ],    'State', select=True, readonly=False),
              }
    _defaults = {  
        'state': 'pending',  
        'date':time.strftime('%Y-%m-%d %H:%M:%S'),
                }
    
class invoice(osv.osv):
    _inherit = 'account.invoice'

    def invoice_check_deposit(self, cr, uid, ids, context=None):
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'glimsol_check', 'glimsol_check_deposit_form_view')

        inv = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':_("Check Deposit"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'glimsol.check.deposit',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                        
        #        'payment_expected_currency': inv.currency_id.id,
                'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
              #  'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
            #    'default_reference': inv.name,
            #    'close_after_process': True,
            #    'invoice_type': inv.type,
                'default_invoice_id': inv.id,
                #'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                #'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            }
        }

invoice()    