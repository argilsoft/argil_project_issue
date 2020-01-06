# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import get_records_pager, pager as portal_pager, CustomerPortal
import logging
_logger = logging.getLogger(__name__)

class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values['issue_count'] = request.env['project.issue'].search_count([
            '|',
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
            #('state', 'in', ['purchase', 'done', 'cancel'])
        ])
        return values

    @http.route(['/my/project_issue', '/my/project_issue/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_project_issues(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        ProjectIssue = request.env['project.issue']

        domain = [
            '|',
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
        ]

        archive_groups = self._get_archive_groups('project.issue', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        searchbar_sortings = {
            'code'  : {'label': _('code'), 'order': 'code desc, id desc'},
            'date'  : {'label': _('Newest'), 'order': 'create_date desc, id desc'},
            'name'  : {'label': _('Name'), 'order': 'name asc, id asc'},
            'stage' : {'label': _('Stage'), 'order': 'stage_id'},
            'update': {'label': _('Last Stage Update'), 'order': 'date_last_stage_update desc'},
        }
        # default sort by value
        if not sortby:
            sortby = 'code'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # count for pager
        issue_count = ProjectIssue.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/project_issue",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=issue_count,
            page=page,
            step=self._items_per_page
        )
        # search the project issues to display, according to the pager data
        orders = ProjectIssue.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        request.session['my_issues_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'orders': orders,
            'page_name': 'project_issue',
            'pager': pager,
            'archive_groups': archive_groups,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'default_url': '/my/project_issue',
        })
        return request.render("project_issue.portal_my_project_issues", values)

    @http.route(['/my/project_issue/<int:order_id>'], type='http', auth="user", website=True)
    def portal_my_project_issue(self, order_id=None, **kw):
        order = request.env['project.issue'].browse(order_id)
        try:
            order.check_access_rights('read')
            order.check_access_rule('read')
        except AccessError:
            return request.redirect('/my')
        history = request.session.get('my_issues_history', [])
        values = {
            'order': order.sudo(),
        }
        values.update(get_records_pager(history, order))
        return request.render("project_issue.portal_my_project_issue", values)
