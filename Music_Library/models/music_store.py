from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError
from datetime import date, datetime, time, timedelta
import logging

_logger = logging.getLogger("name")

class music_library(models.Model):
    _name = 'new_music_library'

    name=fields.Char(compute='get_name', string="Name")
    song_name = fields.Char(string="Song Name:", required=True)
    artist = fields.Char(string="Artist Name:", required=True)
    year = fields.Char(string="Year:", required=True)
    album = fields.Char(string="Album Name:", required=True)
    price = fields.Float(string="Price:", required=True)

    @api.depends('song_name')
    def get_name(self):
        for record in self:
            if record.song_name:
                record.name = record.song_name

class client_information(models.Model):
    _name = 'new_client_info'

    name = fields.Char(compute='complete_name',string="Name")
    firstname = fields.Char(string="Client Name:",required=True)
    middlename = fields.Char(string="Middle Name:", required=True)
    lastname = fields.Char(string="Last Name:", required=True)
    clientname = fields.Char(compute='complete_name', string="Full Name:")
    bday = fields.Date(string="Birth date:", selection='someinfobutton',
                       default=datetime.today(), required=True)
    age = fields.Char(compute='compute_age', string="Age")
    state = fields.Selection(selection=[
        ('clientname', 'Client Name'),
        ('someinfo', 'Some Info'),
        ('otherinfo', 'Other Info')
    ], default='clientname', string="States")

    @api.depends('bday')
    def compute_age(self):
        for record in self:
            if record.bday is not False:
                calculated_bday = (datetime.today().date() -
                                   datetime.strptime(record.bday, '%Y-%m-%d')
                                   .date())
                record.age = (calculated_bday.days // 365)

    @api.depends('firstname','middlename','lastname')
    def complete_name(self):
        for record in self:
            if record.firstname and record.middlename and record.lastname:
                record.name = (record.firstname+" "
                                +record.middlename+" "
                                +record.lastname)
                record.clientname = (record.firstname+" "
                                    +record.middlename+" "
                                    +record.lastname)

    @api.multi
    def clientnamebutton(self):
        return self.write({'state': 'someinfo'})

    @api.multi
    def someinfobutton(self):
        return self.write({'state': 'otherinfo'})

    @api.multi
    def otherinfobutton(self):
        return self.write({'state': 'clientname'})

class music_store(models.Model):
    _name = 'new_music_store'

    name=fields.Char(compute="get_name",string="Name")
    client_id= fields.Many2one('new_client_info', string="Client Name")
    datepurchase = fields.Date(string="Date of purchase:",
                               default=datetime.today(), required=True)
    purchase_line_ids =  fields.One2many('new_purchase_lines', 'store_id',
                                         string="Song Name")
    total = fields.Float(compute="compute_lines_total", string="Total:")
    discounted = fields.Float(compute="compute_lines_discount",
                              string="Discount:")
    state = fields.Selection(selection=[
        ('approve', 'Approved')
    ], default='approve', string="Approved")
    state_button = fields.Selection(selection=[
        ('choose', 'Choose Type of Discount'),
        ('percentage', 'Percentage'),
        ('amount', 'Amount')
    ], default='choose', string="Choose Type of Discount")
    percentage_discount = fields.Float(string="Discounted Percentage")
    amount_discount = fields.Float(string="Discounted Amount")

    # @api.multi
    # def print_purchase(self):
    #     assert len(self.ids) == 1, 'This option should only be used for a single id at a time'
    #     result = self.env['report'].get_action(self, 'music_library_store.music_library_reports')
    #     return result


    @api.multi
    def approve_button(self):
        return self.write({'state': 'approve'})

    @api.depends('state_button')
    def change_state(self):
        if self.state_button == 'percentage':
            return self.write({'state_button': 'percentage'})
        elif self.state_button == 'amount':
            return self.write({'state_button': 'amount'})
        else:
            return self.write({'state_button': 'choose'})

    @api.depends('client_id')
    def get_name(self):
        for record in self:
            if record.client_id:
                record.name = record.client_id.name

    @api.onchange('percentage_discount')
    def set_percentage(self):
        for record in self:
            for percentage in record.purchase_line_ids:
                percentage.discount = record.percentage_discount

    @api.onchange('amount_discount')
    def set_amount(self):
        amount_divided = 0.0
        number_of_lines = 0.0
        for record in self:
            number_of_lines = len(record.purchase_line_ids)
            for amount in record.purchase_line_ids:
                amount_divided = record.amount_discount / number_of_lines
                amount_precentage_divided = amount_divided / amount.total
                amount.discount = amount_precentage_divided * 100

    @api.depends('purchase_line_ids.discount')
    def compute_lines_discount(self):
        for record in self:
            total_discount = 0.0
            for purchase_line in record.purchase_line_ids:
                record.discounted = purchase_line.discount_invi

    @api.depends('purchase_line_ids.discount')
    def compute_lines_total(self):
        for record in self:
            total_amount = 0.0
            for purchase_line in record.purchase_line_ids:
                total_amount += purchase_line.amount
            record.total = total_amount



class purchase_lines(models.Model):
    _name = 'new_purchase_lines'

    name=fields.Char(string="Name")
    store_id = fields.Many2one("new_music_store")
    song_id = fields.Many2one("new_music_library", string="Song Name:")
    prices = fields.Float(related="song_id.price", string="Price:")
    quantity = fields.Integer(string="Quantity:")
    discount = fields.Float(string="Discount:")
    amount = fields.Float(compute="get_total", string="Total:")
    discount_invi = fields.Float(compute="get_total",
                                 string="Invisible Discount Amount")
    total = fields.Float(string="total amount")

    @api.depends('quantity','discount')
    def get_total(self):
        for record in self:
            total_amount = 0
            for amount in record:
                total_amount = amount.prices * amount.quantity
            record.amount = total_amount
            record.total = total_amount

        for record in self:

            discount_decimal = 0
            amount_discounted = 0
            total_amount_discounted = 0

            if record.store_id.state_button == "percentage":
                discount_decimal = record.discount / 100
                amount_discounted = record.total * discount_decimal
                record.discount_invi = amount_discounted
                total_amount_discounted = record.total - amount_discounted
                record.amount = total_amount_discounted

            if record.store_id.state_button == "amount":
                discount_decimal = record.discount / 100
                amount_discounted = record.total * discount_decimal
                record.discount_invi = amount_discounted
                total_amount_discounted = record.total - amount_discounted
                record.amount = total_amount_discounted
