# coding: utf-8

from hubspot.connection.testing import MockPortalConnection
from nose.tools import eq_
from nose.tools import assert_raises

from hubspot.contacts import save_contact, update_contact
from hubspot.contacts.testing import SaveContact, SaveContactClientError, \
    UpdateContact

from tests._utils import make_contact
from tests.test_properties import STUB_STRING_PROPERTY

from hubspot.connection.exc import HubspotClientError


class TestSaveContact(object):

    def test_save_single_contact(self):
        contact = make_contact(None)
        connection = self._make_connection_for_contact(1, contact)

        vid = save_contact(contact, connection)

        eq_(1, vid)

    @staticmethod
    def _make_connection_for_contact(vid, contact, available_property=None):
        available_property = available_property or STUB_STRING_PROPERTY
        simulator = SaveContact(vid, contact, [available_property])
        connection = MockPortalConnection(simulator)
        return connection

    def test_invalid_property_raises_hubspot_client_error(self):
        contact = make_contact(None, properties={'is_polite': 'notavalidinput'})
        connection = self._make_connection_for_contact_with_exception(contact, HubspotClientError("Property notavalidinput is invalid", "request-id"))

        with assert_raises(HubspotClientError) as context:
            with connection:
                save_contact(contact, connection)
        eq_(context.exception.message, "Property notavalidinput is invalid")

    @staticmethod
    def _make_connection_for_contact_with_exception(contact, exception, available_property=None):
        available_property = available_property or STUB_STRING_PROPERTY
        simulator = SaveContactClientError(contact, exception, [available_property])
        connection = MockPortalConnection(simulator)
        return connection


class TestUpdateContact(object):

    def test_update_single_contact(self):
        contact = make_contact(1)
        connection = self._make_connection_for_contact(contact)

        update_contact(contact, connection)

    @staticmethod
    def _make_connection_for_contact(contact, available_property=None):
        available_property = available_property or STUB_STRING_PROPERTY
        simulator = UpdateContact(contact, [available_property])
        connection = MockPortalConnection(simulator)
        return connection
