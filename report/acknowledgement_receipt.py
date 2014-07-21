# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp import netsvc
from openerp.netsvc import Service

try:
    del Service._services['report.acknowledgement.receipt']
except:
    pass


from openerp.report import report_sxw

class order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        print "called!".upper()
        super(order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time, 
            'show_discount':self._show_discount,
            'line_number':self._get_product_line_number,
            'get_down_payment':self._get_down_payment,
            'get_balance':self._get_balance,
            'get_monthly_payment':self._get_monthly_payment,
            'get_designation':self._get_designation,
            'get_product_bundle_items':self._get_product_bundle_items,
        })
        
    def _get_product_bundle_items(self,product_id,context=None):
        cr=self.cr
        uid = self.uid
        #fetch connected product item entries

        cr.execute('select id from product_item where product_id = %s' % product_id)
        product_item_ids = [x[0] for x in cr.fetchall()]
        res = self.pool.get('product.item').read(cr,uid,product_item_ids,['item_id','qty_uom','uom_id'])
#         bundle_product_item_ids = [x[0] for x in cr.fetchall()]
#         product_dicts=self.pool.get('product.product').read(cr,uid,bundle_product_item_ids,['name'])
#         bundle_product_names = [product_dict['name'] for product_dict in product_dicts]
#         res = bundle_product_names
#         if context and 'mode' in context and context['mode'] == 'all':
#             res = [product_dict['id'] for product_dict in product_dicts]
        return res
            

    def _get_product_line_number(self,data,context=None):
        cr = self.cr
        #intigrate fetching of bundle items
        for datum in data:
            datum.bundle_items=self._get_product_bundle_items(datum.product_id.id)
            print "datum.bundle_items".upper(),datum.bundle_items            
        res = [(x+1,obj) for x,obj in enumerate(data)]
        return res        

        return data
    def _get_down_payment(self,data,context=None):
        cr = self.cr
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
    
        
    def _get_balance(self,data,context=None):
        cr = self.cr
        dp = float(self._get_down_payment(data, context))
        res = 0.0
        if dp:
            res = data.amount_total - dp
#         if res:
#             res  = "%.2f" % round(res,2)
        return res
        
    def _get_monthly_payment(self,data,context=None):
        cr = self.cr
        res=0.0
        if data.billing_months:
            balance=float(self._get_balance(data, context))
            res = balance / data.billing_months
#         if res:
#             res  = "%.2f" % round(res,2)            
        return res
        
    def _get_designation(self,data,context=None):
        cr = self.cr
        uid = self.uid
        pool = self.pool.get
        employee_id = pool('hr.employee').search(cr,uid,[('user_id','=',data)],limit=1)
        res = ''
        if employee_id:
            employee_dict = pool('hr.employee').read(cr,uid,employee_id[0],['job_id'])
            if employee_dict['job_id']:
                res = employee_dict['job_id'][1]
        return res
        

    def _show_discount(self, uid, context=None):
        cr = self.cr
        try: 
            group_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'group_discount_per_so_line')[1]
        except:
            return False
        return group_id in [x.id for x in self.pool.get('res.users').browse(cr, uid, uid, context=context).groups_id]

report_sxw.report_sxw('report.acknowledgement.receipt', 'glimsol.acknowledgement.receipt', 'addons/glimsol_report/report/sale_order.rml', parser=order)
