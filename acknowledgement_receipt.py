
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
    def _get_total_cash_amount(self, cr, user, ids, name, attr, context=None):
        res = {}
        for statement in self.browse(cr, user, ids, context=context):
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
              'total_amount_in_words': fields.function(_get_amount_in_words, method=True, type='float', string='Total Amount in Words', store=False),
              'payment_description':fields.char('Payment Description',size=64),
              'notes':fields.char('Notes/Remarks',size=64),
              
              'date': fields.date('Check Date'),
              'cdos_reference':fields.char('CDOS Reference',size=64),
              'invoice_id':fields.many2one('account.invoice','Invoice Reference',required=True),
              'recieve_user_id':fields.many2one('res.partner','Received By',required=True),
              }