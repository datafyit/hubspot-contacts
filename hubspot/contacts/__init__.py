##############################################################################
#
# Copyright (c) 2014, 2degrees Limited.
# All Rights Reserved.
#
# This file is part of hubspot-contacts
# <https://github.com/2degrees/hubspot-contacts>, which is subject to the
# provisions of the BSD at
# <http://dev.2degreesnetwork.com/p/2degrees-license.html>. A copy of the
# license should accompany this distribution. THIS SOFTWARE IS PROVIDED "AS IS"
# AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

from itertools import chain

from pyrecord import Record

from hubspot.contacts._constants import BATCH_SAVING_SIZE_LIMIT
from hubspot.contacts._constants import CONTACTS_API_SCRIPT_NAME, COMPANIES_API_SCRIPT_NAME
from hubspot.contacts._property_utils import get_property_type_by_property_name, get_property_type_by_property_name_companies
from hubspot.contacts.generic_utils import ipaginate
from hubspot.contacts.request_data_formatters.contacts import \
    format_contact_data_for_saving, format_contacts_data_for_saving, \
    format_contact_properties_for_saving, format_company_data_for_saving


Contact = Record.create_type(
    'Contact',
    'vid',
    'email_address',
    'properties',
    'related_contact_vids',
    related_contact_vids=(),
    )

Company = Record.create_type(
    'Company',
    'properties',
    )


_CONTACTS_SAVING_URL_PATH = CONTACTS_API_SCRIPT_NAME + '/contact/batch/'
_CONTACT_CREATING_URL_PATH = CONTACTS_API_SCRIPT_NAME + '/contact/'
_CONTACT_UPDATING_URL_TEMPLATE = CONTACTS_API_SCRIPT_NAME + '/contact/vid/{contact_id}/profile'

_COMPANY_CREATING_URL_PATH = COMPANIES_API_SCRIPT_NAME + '/companies/'


def save_contacts(contacts, connection):
    """
    Request the creation and/or update of the ``contacts``.
    
    :param iterable contacts: The contacts to be created/updated
    :return: ``None``
    :raises hubspot.connection.exc.HubspotException:
    :raises hubspot.contacts.exc.HubspotPropertyValueError: If one of the
        property values on a contact is invalid.
    
    For each contact, only its email address and properties are passed to
    HubSpot. Any other datum (e.g., the VID) is ignored.
    
    As at this writing, this end-point does not process the requested changes
    immediately. Instead, it **partially** validates the input and, if it's all
    correct, the requested changes are queued.
    
    End-point documentation:
    http://developers.hubspot.com/docs/methods/contacts/batch_create_or_update
    
    """
    contacts_batches = ipaginate(contacts, BATCH_SAVING_SIZE_LIMIT)

    contacts_first_batch = next(contacts_batches, None)
    if not contacts_first_batch:
        return

    property_type_by_property_name = \
        get_property_type_by_property_name(connection)

    for contacts_batch in chain([contacts_first_batch], contacts_batches):
        contacts_batch_data = format_contacts_data_for_saving(
            contacts_batch,
            property_type_by_property_name,
            )
        connection.send_post_request(
            _CONTACTS_SAVING_URL_PATH,
            contacts_batch_data,
            )


def create_contact(contact, connection):
    property_type_by_property_name = \
        get_property_type_by_property_name(connection)
    contact_data = format_contact_data_for_saving(
            contact,
            property_type_by_property_name,
            )
    response = connection.send_post_request(
            _CONTACT_CREATING_URL_PATH,
            contact_data,
            )
    return response["vid"]


def update_contact(contact, connection):
    property_type_by_property_name = \
        get_property_type_by_property_name(connection)
    properties_data = format_contact_properties_for_saving(
            contact.properties,
            property_type_by_property_name,
    )
    path = _CONTACT_UPDATING_URL_TEMPLATE.format(contact_id=contact.vid)
    connection.send_post_request(
            path,
            properties_data,
    )

def create_company(company, connection):
    property_type_by_property_name = \
        get_property_type_by_property_name_companies(connection)

    company_data = format_company_data_for_saving(company, property_type_by_property_name)

    response = connection.send_post_request(
            _COMPANY_CREATING_URL_PATH,
            company_data,
            )
    return response["companyId"]
