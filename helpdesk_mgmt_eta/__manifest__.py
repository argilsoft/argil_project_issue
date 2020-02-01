# -*- encoding: utf-8 -*-

{
    "name"          : "Helpdesk - Fecha Estimada Cierre",
    "version"       : "1.0",
    "author"        : "Argil Consulting",
    "category"      : "Helpdesk",
    "description"   : """
    Este modulo agrega el campo <Fecha Estimada> (Fecha estimada en que se entregaría la solución al Ticket)
""",
    "website"       : "http://www.argil.mx",
    #"license" : "AGPL-3",
    "depends"       : ["helpdesk_mgmt",
        ],
    "data"          : [
        'views/helpdesk_ticket_view.xml'
    ],
    "installable"   : True,
}
