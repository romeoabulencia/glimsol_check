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
from num2words import num2words
import datetime

try:
    del Service._services['report.conditional.deed.of.sale']
except:
    pass


from openerp.report import report_sxw

class cdos(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(cdos, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time, 
            'num2words':num2words,
            'ordinal':self._get_ordinal,
            'check_lines':self._get_check_lines,
    #        'product_lines':self._get_product_lines,
            'get_cdos_month':self._get_cdos_month,
            
            
                    })
        
    def _get_cdos_month(self,cdos_obj,context=None):
        target_date=cdos_obj.cdos_date
        temp=datetime.datetime.strptime(target_date,'%Y-%m-%d')
        return temp.strftime('%B')
    
    def _get_product_lines(self,invoice_obj,context=None):
         
        #fetch connected sale order
        self.cr.execute('select order_id from sale_order_invoice_rel where invoice_id = %s' % invoice_id)
        target_sale_order_ids=[x[0] for x in self.cr.fetchall()]
        #fetch connected delivery order move lines
        self.cr.execute('select move.id from stock_picking_out do inner join stock_move move on (move.picking_id = do.id) where do.sale_id in (%s)' % str(target_sale_order_ids)[1:-1])
        target_stock_move_ids=[x[0] for x in self.cr.fetchall()]
        
        res = self.pool.get('stock.move').browse(self.cr,self.uid,target_stock_move_ids)
         
        return res        
    
    def _get_check_lines(self,invoice_id,context=None):
        
        res = []
        
        return res
    
    
    def _get_ordinal(self,n,context=None):
        if 10 < n < 14: return u'%sth' % n
        if n % 10 == 1: return u'%sst' % n
        if n % 10 == 2: return u'%snd' % n
        if n % 10 == 3: return u'%srd' % n
        return u'%sth' % n
    
report_sxw.report_sxw('report.conditional.deed.of.sale', 'glimsol.conditional.deed.of.sale', 'addons/glimsol_check/report/conditional_deed_of_sale.rml', parser=cdos)
    