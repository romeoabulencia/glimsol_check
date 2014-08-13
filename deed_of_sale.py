
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

class cdos(osv.osv):
    _name="glimsol.conditional.deed.of.sale"
    def print_report(self, cr, uid, ids, context=None):
        datas = {
             'ids': ids,
             'active_ids': context['active_ids'],
             'model': 'glimsol.conditional.deed.of.sale',
             'form': self.read(cr, uid, ids)[0]
        }
        res = {

            'type': 'ir.actions.report.xml',
            'report_name': 'conditional.deed.of.sale',
            'report_type':'pdf',
            'datas': datas,
        }    
        return res    
    
    def get_down_payment(self,cr,user,data):

        res=0.0

        target_data={'type':data.billing_type,
                     'amount':data.billing_extra_amount,
                     'months':data.billing_months,
                     'total':data.amount_total}
        temp_bank=[#('whole amount'),
         (['monthly by percentage','by percentage'],"res = target_data['total']*target_data['amount']/100"),
         (['fixed amount'],"res = target_data['amount']"),
         ]
        for target_types,str_result in temp_bank:
            if target_data['type'] in target_types:
                exec str_result
                
#         if res:
#             res  = "%.2f" % round(res,2)
        return res 
    def _get_down_payment(self, cr, user, ids, name,attr,context=None):
        res = {}
        for obj in self.browse(cr,user,ids,):
            res[obj.id]=0.0
            #check for connected sale_order
            cr.execute('select order_id from sale_order_invoice_rel where invoice_id = %s' % obj.invoice_id.id)
            sale_order_ids = [x[0] for x in cr.fetchall()]
            for data in self.pool.get('sale.order').browse(cr,user,sale_order_ids):
                res[obj.id]=self.get_down_payment(cr, user, data)
        return res 
    def get_balance(self,cr,user,data,context=None):
        dp = float(self.get_down_payment(cr,user,data))
        res = 0.0
        if dp:
            res = data.amount_total - dp
        return res    
    def _get_balance(self,cr,user,ids,name,attr,context=None):
        res={}
        for obj in self.browse(cr,user,ids,):
            res[obj.id]=0.0
            #check for connected sale_order
            cr.execute('select order_id from sale_order_invoice_rel where invoice_id = %s' % obj.invoice_id.id)
            sale_order_ids = [x[0] for x in cr.fetchall()]
            for data in self.pool.get('sale.order').browse(cr,user,sale_order_ids):
                res[obj.id]=self.get_balance(cr, user, data)
        return res 

    
    _columns={
              'invoice_id':fields.many2one('account.invoice','Invoice',required=False),
              'company_id':fields.many2one('res.partner', 'Company', domain=[('is_company','=',True)]), 
              'company_user_id':fields.many2one('res.partner','Company Owner',domain=[('is_company','=',False)]),
              'customer_id':fields.many2one('res.partner','Customer',domain=[('is_company','=',True)]),
              'customer_user_id': fields.many2one('res.partner','Customer Owner',domain=[('is_company','=',False)]),
             'cdos_date': fields.date('Date'), 
             'down_payment': fields.function(_get_down_payment, method=True, type='float', string='Down Payment', store=False), 
             'balance':fields.function(_get_balance, method=True, type='float', string='Balance', store=False), 

              }
    
class dos(osv.osv):
    _inherit="glimsol.conditional.deed.of.sale"
    _name="glimsol.deed.of.sale"
    
    def print_report(self, cr, uid, ids, context=None):
        datas = {
             'ids': ids,
             'active_ids': context['active_ids'],
             'model': 'glimsol.deed.of.sale',
             'form': self.read(cr, uid, ids)[0]
        }
        res = {

            'type': 'ir.actions.report.xml',
            'report_name': 'deed.of.sale',
            'report_type':'pdf',
            'datas': datas,
        }    
        return res
    
class invoice(osv.osv):
    _inherit = 'account.invoice'
    _name="account.invoice"
    
    _columns={
              'cdos_ids':fields.one2many('glimsol.conditional.deed.of.sale', 'invoice_id', 'Conditional Deed of Sale', required=False),
              'dos_ids':fields.one2many('glimsol.conditional.deed.of.sale', 'invoice_id', 'Conditional Deed of Sale', required=False),
              
              }
    def invoice_deed_of_sale(self, cr, uid, ids, context=None):
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'glimsol_check', 'glimsol_deed_of_sale_form_view')

        inv = self.browse(cr, uid, ids[0], context=context)
        #check for existing check deposit entry
        target = self.pool.get('glimsol.deed.of.sale').search(cr,uid,[('invoice_id','=',inv.id)])
        res = {
            'name':_("Deed of Sale"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'glimsol.deed.of.sale',
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
            
        #check for connected sale_order
        cr.execute('select order_id from sale_order_invoice_rel where invoice_id = %s' % inv.id)
        sale_order_ids = [x[0] for x in cr.fetchall()]
        if sale_order_ids:
            so_pool = self.pool.get('glimsol.deed.of.sale')
        for data in self.pool.get('sale.order').browse(cr,uid,sale_order_ids):
            temp_dict={'default_balance':so_pool.get_balance(cr,uid,data),
                       'default_down_payment':so_pool.get_down_payment(cr,uid,data)
                       }
            res['context'].update(temp_dict)

        return res    

    def invoice_conditional_deed_of_sale(self, cr, uid, ids, context=None):
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'glimsol_check', 'glimsol_conditional_deed_of_sale_form_view')

        inv = self.browse(cr, uid, ids[0], context=context)
        #check for existing check deposit entry
        target = self.pool.get('glimsol.conditional.deed.of.sale').search(cr,uid,[('invoice_id','=',inv.id)])
        res = {
            'name':_("Conditional Deed of Sale"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'glimsol.conditional.deed.of.sale',
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
            
        #check for connected sale_order
        cr.execute('select order_id from sale_order_invoice_rel where invoice_id = %s' % inv.id)
        sale_order_ids = [x[0] for x in cr.fetchall()]
        if sale_order_ids:
            so_pool = self.pool.get('glimsol.conditional.deed.of.sale')
        for data in self.pool.get('sale.order').browse(cr,uid,sale_order_ids):
            temp_dict={'default_balance':so_pool.get_balance(cr,uid,data),
                       'default_down_payment':so_pool.get_down_payment(cr,uid,data)
                       }
            res['context'].update(temp_dict)

        return res

invoice()        