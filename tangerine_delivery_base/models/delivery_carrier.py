from odoo import models, _


class DeliveryCarrierBase(models.Model):
    _inherit = 'delivery.carrier'

    def toggle_prod_environment(self):
        for carrier in self:
            carrier.prod_environment = not carrier.prod_environment
            if not hasattr(self, f'{self.delivery_type}_toggle_prod_environment'):
                raise NotImplementedError(_(f'Subclass has no attributes {self.delivery_type}_toggle_prod_environment'))
            getattr(self, f'{self.delivery_type}_toggle_prod_environment')()
