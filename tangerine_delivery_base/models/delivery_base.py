import requests
from requests.exceptions import ConnectionError, ConnectTimeout
from odoo import fields, models, _
from odoo.exceptions import UserError
from ..settings import utils


class DeliveryBase(models.Model):
    _inherit = ['delivery.carrier']

    image = fields.Binary(string='Icon image')
    access_token = fields.Char(string='Access Token')
    domain = fields.Char(string='Domain')
    route_api_ids = fields.One2many(
        'delivery.route.api',
        'provider_id',
        string='Routes API',
        context={'active_test': False}
    )
    status_ids = fields.One2many(
        'delivery.status',
        'provider_id',
        string='Status',
        context={'active_test': False}
    )

    def action_test_connection(self):
        self.ensure_one()
        try:
            if not self.domain:
                raise UserError(_('The field domain is required'))
            requests.get(self.domain, timeout=3)
            return utils.notification(
                notification_type='success',
                message=f'{self.domain} connection successfully'
            )
        except ConnectTimeout:
            return utils.notification(
                notification_type='danger',
                message=f'{self.domain} connection timeout'
            )
        except ConnectionError:
            return utils.notification(
                notification_type='danger',
                message=f'{self.domain} connection error'
            )

    def get_access_token(self):
        self.ensure_one()
        if not hasattr(self, f'{self.delivery_type}_get_access_token'):
            raise NotImplementedError(_(f'Subclass has no attributes {self.delivery_type}_get_access_token'))
        elif self.delivery_type in ['base_on_rule', 'fixed']:
            raise UserError(_('Get access token method does not support for provider has type Based on rules or Fixed Price'))
        return getattr(self, f'{self.delivery_type}_get_access_token')()


class DeliveryRouteAPI(models.Model):
    _name = 'delivery.route.api'
    _inherit = ['mail.thread']
    _description = 'Delivery Routes API'

    provider_id = fields.Many2one('delivery.carrier', string='Provider', required=True)
    domain = fields.Char(related='provider_id.domain', string='Domain')
    name = fields.Char(string='Name', tracking=True)
    code = fields.Char(string='Code', required=True, tracking=True, index=True)
    route = fields.Char(string='Route', required=True, tracking=True)
    description = fields.Text(string='Description')
    method = fields.Selection([
        ('POST', 'POST'),
        ('DELETE', 'DELETE'),
        ('PUT', 'PUT'),
        ('GET', 'GET')
    ], string='Method', required=True, tracking=True)
    active = fields.Boolean(default=True)
    headers = fields.Json(string='Headers', tracking=True)


class DeliveryStatus(models.Model):
    _name = 'delivery.status'
    _inherit = ['mail.thread']
    _description = 'Delivery Status'

    provider_id = fields.Many2one('delivery.carrier', string='Provider', required=True, tracking=True)
    name = fields.Char(string='Name', tracking=True)
    code = fields.Char(string='Code', tracking=True)
    description = fields.Char(string='Description')

    _sql_constraints = [
        ('provider_code_uniq', 'unique(provider_id,code)', 'Provider status code must be unique.'),
    ]


