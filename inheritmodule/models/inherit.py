from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError
import logging

_logger = logging.getLogger("name")

class inherit_music_store(models.Model):

    _inherit='new_music_store'

    song_id_new = fields.Many2one('new_customer_information')

    @api.multi
    def approve_button(self):
        if self.purchase_line_ids:
            song_list = []
            for rec in self.purchase_line_ids:
                song_list.append((0,0,{'song_name':rec.song_id.name,
                                       'price':rec.prices,
                                       'quantity':rec.quantity,
                                       'discount':rec.discount,
                                       'amount':rec.amount
                                       }))
            #_logger.info("\n\n\n\n\nCustomer: %s\n\n\n"%(song_list))
        new_customer = self.env['new_customer_information'].search([('customer_name','=',self.name)])

        if new_customer:
            for list in new_customer:
                if list.customer_name == self.name:
                    res = list.write({'products': song_list
                                    })
        if not new_customer:
            new_customer.create({'customer_name': self.name,
                                       'products': song_list
                                       })


class customer_information(models.Model):

    _name='new_customer_information'
    _rec_name='customer_name'

    customer_name=fields.Char(string="Customer Name")
    products = fields.One2many('new_music','song_id_new',string='Products', readonly="True")

class music_information(models.Model):

    _name='new_music'

    song_id_new = fields.Many2one('new_customer_information')
    song_name = fields.Char(string="Song Name:")
    price = fields.Float(string="Price:")
    quantity = fields.Integer(string="Quantity:")
    discount = fields.Float(string="Discount:")
    amount = fields.Float(string="Total:")

