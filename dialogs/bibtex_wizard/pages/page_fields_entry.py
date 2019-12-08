#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017, 2018 Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from dialogs.document_wizard.pages.page import Page, PageView

import os


class FieldsEntryPage(Page):

    def __init__(self, wizard, current_values):
        self.wizard = wizard
        self.current_values = current_values
        self.view = FieldsEntryPageView(self.wizard.fields)
        self.required_fields = list()
        self.blank_required_fields = list()

    def observe_view(self):
        def text_deleted(buffer, position, n_chars, field_name):
            text = buffer.get_text()
            if field_name == 'identifier':
                self.current_values['identifier'] = text
            else:
                self.current_values['fields'][field_name] = text
            if text == '' and field_name in self.required_fields:
                self.blank_required_fields.append(field_name)
            self.wizard.check_required_fields()

        def text_inserted(buffer, position, chars, n_chars, field_name):
            text = buffer.get_text()
            if field_name == 'identifier':
                self.current_values['identifier'] = text
            else:
                self.current_values['fields'][field_name] = text
            if text != '':
                try: self.blank_required_fields.remove(field_name)
                except ValueError: pass
            self.wizard.check_required_fields()

        self.view.identifier_entry.text_entry.get_buffer().connect('deleted-text', text_deleted, 'identifier')
        self.view.identifier_entry.text_entry.get_buffer().connect('inserted-text', text_inserted, 'identifier')

        for entry_view in self.view.required_entry_views.values():
            entry_view.text_entry.get_buffer().connect('deleted-text', text_deleted, entry_view.field_name)
            entry_view.text_entry.get_buffer().connect('inserted-text', text_inserted, entry_view.field_name)

        for entry_view in self.view.optional_entry_views.values():
            entry_view.text_entry.get_buffer().connect('deleted-text', text_deleted, entry_view.field_name)
            entry_view.text_entry.get_buffer().connect('inserted-text', text_inserted, entry_view.field_name)

    def load_presets(self, presets):
        for entry_view in self.view.required_entry_views.values():
            entry_view.text_entry.set_text('')

        for entry_view in self.view.optional_entry_views.values():
            entry_view.text_entry.set_text('')

    def on_activation(self):
        pass


class FieldsEntryPageView(Gtk.VBox):

    def __init__(self, fields):
        Gtk.VBox.__init__(self)
        self.get_style_context().add_class('bibtex-wizard-page')

        self.scrolled_window = Gtk.ScrolledWindow()
        self.vbox = Gtk.VBox()
        self.vbox.set_margin_start(18)
        self.vbox.set_margin_top(18)
        self.vbox.set_margin_bottom(18)
        self.vbox.set_margin_right(382)
        self.scrolled_window.add(self.vbox)

        self.headerbar_subtitle = 'Step 2: Entry fields'

        self.header1 = Gtk.Label()
        self.header1.set_xalign(0)
        self.header1.set_margin_bottom(12)
        self.header1.get_style_context().add_class('document-wizard-header')
        self.header1.set_text('Required fields')

        self.required_entry_views = dict()
        self.required_fields_entries = Gtk.VBox()
        self.identifier_entry = FieldsEntryView('identifier')
        self.required_fields_entries.pack_start(self.identifier_entry, False, False, 0)
        for field_name, attributes in fields.items():
            self.required_entry_views[field_name] = FieldsEntryView(field_name)
            self.required_fields_entries.pack_start(self.required_entry_views[field_name], False, False, 0)

        self.header2 = Gtk.Label()
        self.header2.set_xalign(0)
        self.header2.set_margin_bottom(12)
        self.header2.set_margin_top(18)
        self.header2.get_style_context().add_class('document-wizard-header')
        self.header2.set_text('Optional fields')
        
        self.optional_entry_views = dict()
        self.optional_fields_entries = Gtk.VBox()
        for field_name, attributes in fields.items():
            self.optional_entry_views[field_name] = FieldsEntryView(field_name)
            self.optional_fields_entries.pack_start(self.optional_entry_views[field_name], False, False, 0)

        self.vbox.pack_start(self.header1, False, False, 0)
        self.vbox.pack_start(self.required_fields_entries, False, False, 0)
        self.vbox.pack_start(self.header2, False, False, 0)
        self.vbox.pack_start(self.optional_fields_entries, False, False, 0)
        self.pack_start(self.scrolled_window, True, True, 0)
        self.show_all()


class FieldsEntryView(Gtk.Revealer):

    def __init__(self, field_name):
        Gtk.Revealer.__init__(self)
        self.box = Gtk.HBox()
        self.field_name = field_name
        self.label = Gtk.Label(field_name + ':')
        self.label.set_xalign(0)
        self.label.set_margin_right(6)
        self.text_entry = Gtk.Entry()
        self.text_entry.set_size_request(230, -1)
        self.box.pack_start(self.label, True, True, 0)
        self.box.pack_start(self.text_entry, False, False, 0)
        self.add(self.box)
        self.set_reveal_child(True)


