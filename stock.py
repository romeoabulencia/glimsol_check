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

from openerp.osv import fields, osv


class stock_picking_out(osv.osv):
    _inherit = 'stock.picking.out'
    _name='stock.picking.out'
    _columns={
             "po_id":fields.many2one('purchase.order','PO Reference',required=False),
             "ar_id":fields.many2one('glimsol.acknowledgement.receipt','AR Reference',required=False),
#             'po_reference':fields.char('PO Reference',size=64,required=False),
#             'ar_reference':fields.char('AR Reference',size=64,required=False),} 
    }

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _name='stock.picking'
    _columns={
             "po_id":fields.many2one('purchase.order','PO Reference',required=False),
             "ar_id":fields.many2one('glimsol.acknowledgement.receipt','AR Reference',required=False),
#             'po_reference':fields.char('PO Reference',size=64,required=False),
#             'ar_reference':fields.char('AR Reference',size=64,required=False),} 
    }