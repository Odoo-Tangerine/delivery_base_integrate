# -*- coding: utf-8 -*-
import re
import pytz
import functools
from typing import NamedTuple, Any, Optional
from urllib.parse import urlencode, unquote_plus
from odoo import _, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.http import request
from .status import status


def response(response_status, message, data=None):
    response = {'status': response_status, 'message': message}
    if data:
        response.update({'data': data})
    return response


def validate_api_key(key_pram):
    def decorator(func):
        @functools.wraps(func)
        def wrap(self, *args, **kwargs):
            api_key = request.httprequest.headers.get('Authorization')
            if not api_key:
                return response(
                    message='The header Authorization missing',
                    response_status=status.HTTP_401_UNAUTHORIZED
                )
            api_key_config = request.env['ir.config_parameter'].sudo().get_param(key_pram)
            if api_key != api_key_config:
                return response(
                    message=f'The Client Secret {api_key} seems to have invalid.',
                    response_status=status.HTTP_403_FORBIDDEN
                )
            request.update_env(SUPERUSER_ID)
            return func(self, *args, **kwargs)
        return wrap
    return decorator


def notification(notification_type: str, message: str):
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'type': notification_type,
            'message': _(message),
            'next': {'type': 'ir.actions.act_window_close'},
        }
    }


def get_route_api(provider_id, code):
    route_id = provider_id.route_api_ids.search([('code', '=', code)])
    if not route_id:
        raise UserError(_(f'Route {code} not found'))
    return route_id


def datetime_to_rfc3339(dt, time_zone):
    dt = dt.astimezone(pytz.timezone(time_zone))
    return dt.isoformat()


def standardization_e164(phone_number):
    phone_number = re.sub(r'[^\d+]', '', phone_number)
    if phone_number.startswith('0'):
        phone_number = f'84{phone_number[1:]}'
    elif phone_number.startswith('+'):
        phone_number = phone_number[1:]
    return phone_number


class URLBuilder(NamedTuple):
    host: str
    routes: str
    params: str

    @classmethod
    def _add_query_params(cls, param_name: str, v: Optional[dict[str, str]] = None) -> str:
        if not v: return v
        elif not isinstance(v, dict): raise TypeError(f'{param_name} must be a dict')
        return urlencode(v)

    @classmethod
    def _add_routes(cls, param_name: str, v: Optional[list[str]] = None) -> str:
        if not v: return ''
        elif not isinstance(v, list): raise TypeError(f'{param_name} must be a list')
        return ''.join(v)

    @classmethod
    def _define_host(cls, param_name: str, v: str) -> str:
        if not v: raise KeyError(f'Key {param_name} missing')
        elif not isinstance(v, str): raise TypeError(f'Key {param_name} must be a string')
        return v

    @classmethod
    def to_url(cls, instance, is_unquote: Optional[bool] = None) -> str:
        if instance.params:
            if is_unquote:
                params = re.sub(r"'", '"', unquote_plus(instance.params))
            else:
                params = re.sub(r"'", '"', instance.params)
            return f'{instance.host}{instance.routes}?{params}'
        return f'{instance.host}{instance.routes}'

    @classmethod
    def builder(
            cls,
            host: str,
            routes: Optional[list[str]] = None,
            params: Optional[dict[str, Any]] = None,
            is_unquote: Optional[bool] = None
    ) -> str:
        instance = cls(
            cls._define_host('host', host),
            cls._add_routes('routes', routes),
            cls._add_query_params('params', params)
        )
        return cls.to_url(instance, is_unquote)
