#!/usr/bin/python3
# -*- utf-8 -*-
#
#
# Script to replace string in files
#
# Copyright (C) 2017 -2016 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#
import gi
try:
    gi.require_version('Nautilus', '3.0')
    gi.require_version('Gtk', '3.0')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import Nautilus as FileManager
from gi.repository import Gtk
from gi.repository import GObject
import os
import sys
import urllib
import codecs
import os
import json

import locale
import gettext

APP = 'nautilus-renamer'
APP_CONF = APP+'.conf'
CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.config')
CONFIG_APP_DIR = os.path.join(CONFIG_DIR, APP)
CONFIG_FILE = os.path.join(CONFIG_APP_DIR, APP_CONF)
ROOTDIR = '/usr/share/'
LANGDIR = os.path.join(ROOTDIR, 'locale-langpack')

PARAMS = {
    'file_dir': '',
    'patterns': ['{filename}+{extension}']
    }

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, LANGDIR)
gettext.textdomain(APP)
_ = gettext.gettext


class Configuration(object):

    def __init__(self):
        self.params = PARAMS
        self.read()

    def get(self, key):
        try:
            return self.params[key]
        except KeyError:
            self.params[key] = PARAMS[key]
            return self.params[key]

    def set(self, key, value):
        self.params[key] = value

    def read(self):
        try:
            f = codecs.open(CONFIG_FILE, 'r', 'utf-8')
        except IOError:
            self.save()
            f = open(CONFIG_FILE, 'r')
        try:
            self.params = json.loads(f.read())
        except ValueError:
            self.save()
        f.close()

    def save(self):
        if not os.path.exists(CONFIG_APP_DIR):
            os.makedirs(CONFIG_APP_DIR)
        f = open(CONFIG_FILE, 'w')
        f.write(json.dumps(self.params))
        f.close()
########################################################################
'''
New functions to help work with this extension
'''


def format_number(pattern, number):
    return pattern[:len(pattern)-len(number)]+number
########################################################################


def get_files(files_in):
    files = []
    for file_in in files_in:
        mfile = (urllib.url2pathname(file_in.get_uri())[7:])
        if os.path.isfile(mfile):
            files.append(mfile)
    if len(files) > 0:
        return files
    return None


class RenameDialog(Gtk.Dialog):  # needs GTK, Python, Webkit-GTK
    def __init__(self, files=None):
        Gtk.Dialog.__init__(self,
                            'Nautilus Renamer',
                            None,
                            Gtk.DialogFlags.MODAL |
                            Gtk.DialogFlags.DESTROY_WITH_PARENT,
                            (Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_size_request(600, 400)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect('destroy', self.on_close_dialog)
        #
        vbox0 = Gtk.VBox(spacing=5)
        vbox0.set_border_width(5)
        self.get_content_area().add(vbox0)
        #
        frame1 = Gtk.Frame()
        vbox0.pack_start(frame1, True, True, 0)
        #
        vbox11 = Gtk.VBox(spacing=5)
        vbox11.set_border_width(5)
        frame1.add(vbox11)
        #
        vbox11.pack_start(Gtk.Label('{filename} = %s' % _(
            'The name of the file')), False, False, 0)
        vbox11.pack_start(Gtk.Label('{extension} = %s' % _(
            'The extension of the file')), False, False, 0)
        vbox11.pack_start(Gtk.Label('{iterator} = %s' % _(
            'An iterator')), False, False, 0)
        vbox11.pack_start(Gtk.Label('format_number(pattern,number) = %s' % _(
            'A predefinied function to format numbers')), False, False, 0)
        #
        frame2 = Gtk.Frame()
        vbox0.pack_start(frame2, True, True, 0)
        #
        hbox21 = Gtk.HBox(spacing=5)
        hbox21.set_border_width(5)
        frame2.add(hbox21)
        #
        button20 = Gtk.Button()
        button20.set_image(Gtk.Image.new_from_stock(
            Gtk.STOCK_DIRECTORY, Gtk.IconSize.BUTTON))
        button20.set_size_request(32, 32)
        button20.set_tooltip_text(_('Load files'))
        button20.connect('clicked', self.on_button_load_clicked)
        hbox21.pack_start(button20, False, False, 0)
        #
        button23 = Gtk.Button()
        button23.set_image(Gtk.Image.new_from_stock(
            Gtk.STOCK_FIND, Gtk.IconSize.BUTTON))
        button23.set_size_request(32, 32)
        button23.set_tooltip_text(_('Preview'))
        button23.connect('clicked', self.on_click_button_preview)
        hbox21.pack_start(button23, False, False, 0)
        #
        button2 = Gtk.Button()
        button2.set_image(Gtk.Image.new_from_stock(
            Gtk.STOCK_EXECUTE, Gtk.IconSize.BUTTON))
        button2.set_size_request(32, 32)
        button2.set_tooltip_text(_('Rename'))
        button2.connect('clicked', self.on_button_rename_clicked)
        hbox21.pack_start(button2, False, False, 0)
        #
        hbox21.pack_start(Gtk.Label(_('Pattern')+':'), False, False, 0)
        #
        self.entry22 = Gtk.ComboBoxText.new_with_entry()
        hbox21.pack_start(self.entry22, True, True, 0)
        #
        button24 = Gtk.Button()
        button24.set_image(Gtk.Image.new_from_stock(
            Gtk.STOCK_SAVE, Gtk.IconSize.BUTTON))
        button24.set_size_request(32, 32)
        button24.set_tooltip_text(_('Save pattern'))
        button24.connect('clicked', self.on_click_button_save_pattern)
        hbox21.pack_start(button24, False, False, 0)
        #
        button25 = Gtk.Button()
        button25.set_image(Gtk.Image.new_from_stock(
            Gtk.STOCK_DELETE, Gtk.IconSize.BUTTON))
        button25.set_size_request(32, 32)
        button25.set_tooltip_text(_('Delete pattern'))
        button25.connect('clicked', self.on_click_button_remove_pattern)
        hbox21.pack_start(button25, False, False, 0)
        #
        frame3 = Gtk.Frame()
        vbox0.pack_start(frame3, True, True, 0)
        #
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_size_request(600, 300)
        scrolledwindow.set_border_width(2)
        frame3.add(scrolledwindow)
        self.treeview = Gtk.TreeView()
        scrolledwindow.add(self.treeview)
        self.treeview.connect('drag-data-received', self.drag_data_received)
        #
        model = Gtk.ListStore(str, str, str)
        self.treeview.set_model(model)
        #
        column = Gtk.TreeViewColumn(
            _('Source'), Gtk.CellRendererText(), text=1)
        self.treeview.append_column(column)
        #
        column = Gtk.TreeViewColumn(
            _('Modified'), Gtk.CellRendererText(), text=2)
        self.treeview.append_column(column)
        #
        if files:
            for file in files:
                if os.path.isfile(file):
                    head, tail = os.path.split(file)
                model.append([head, tail, ''])
        conf = Configuration()
        for pattern in conf.get('patterns'):
            self.entry22.append_text(pattern)
        self.entry22.set_active(0)
        self.show_all()
        configuration = Configuration()
        self.file_dir = configuration.get('file_dir')
        if len(self.file_dir) <= 0 or os.path.exists(self.file_dir) is False:
            self.file_dir = os.getenv('HOME')

    def drag_data_received(self, widget, drag_context, x, y, selection_data,
                           info, timestamp):
        filenames = selection_data.get_uris()
        for filename in filenames:
            if len(filename) > 8:
                filename = urllib.request.url2pathname(filename)
                filename = filename[7:]
                if os.path.exists(filename) and os.path.isfile(filename):
                    head, tail = os.path.split(filename)
                    model.append([head, tail, ''])
        return True

    def exists_pattern(self, pattern=None):
        model = self.entry22.get_model()
        for i in range(0, len(model)):
            if pattern == model[i][0]:
                return i
        return -1

    def get_patterns(self):
        patterns = []
        model = self.entry22.get_model()
        for i in range(0, len(model)):
            patterns.append(model[i][0])
        return patterns

    def on_click_button_save_pattern(self, widget):
        pattern_to_save = self.entry22.get_active_text()
        pattern_index = self.exists_pattern(pattern_to_save)
        if pattern_index == -1:
            self.entry22.append_text(pattern_to_save)
            pattern_index = len(self.entry22.get_model())
            conf = Configuration()
            conf.params['patterns'] = self.get_patterns()
            conf.save()
        self.entry22.set_active(pattern_index)

    def on_button_load_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(_('Select one or more files to rename'),
                                       self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.set_select_multiple(True)
        dialog.set_current_folder(self.file_dir)
        filter = Gtk.FileFilter()
        filter.set_name(_('All files'))
        filter.add_pattern('*.*')
        dialog.add_filter(filter)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filenames = dialog.get_filenames()
            if len(filenames) > 0:
                model = self.treeview.get_model()
                model.clear()
                for filename in filenames:
                    if os.path.isfile(filename):
                        head, tail = os.path.split(filename)
                    model.append([head, tail, ''])
                self.file_dir = os.path.dirname(filenames[0])
                if len(self.file_dir) <= 0 or os.path.exists(
                        self.file_dir) is False:
                    self.file_dir = os.getenv('HOME')
        dialog.destroy()

    def on_click_button_remove_pattern(self, widget):
        pattern_to_remove = self.entry22.get_active_text()
        model = self.entry22.get_model()
        itera = model.get_iter_first()
        while(itera is not None):
            pattern = model.get(itera, 0)[0]
            print(pattern)
            if pattern == pattern_to_remove:
                model.remove(itera)
                conf = Configuration()
                conf.params['patterns'] = self.get_patterns()
                conf.save()
                self.entry22.set_active(0)
                return
            itera = model.iter_next(itera)

    def on_click_button_preview(self, widget):
        model = self.treeview.get_model()
        itera = model.get_iter_first()
        num = 0
        while(itera is not None):
            source = model.get(itera, 1)[0]
            print(source)
            try:
                destination = self.evalua(source, num)
            except Exception as e:
                print(e)
                destination = 'Error'
            model.set(itera, 2, destination)
            itera = model.iter_next(itera)
            num += 1

    def on_close_dialog(self, widget):
        configuration = Configuration()
        configuration.set('file_dir', self.file_dir)
        configuration.save()
        self.hide()

    def on_button_rename_clicked(self, widget):
        self.on_click_button_preview(None)
        model = self.treeview.get_model()
        itera = model.get_iter_first()
        num = 0
        while(itera is not None):
            head = model.get(itera, 0)[0]
            source = os.path.join(head, model.get(itera, 1)[0])
            destination = os.path.join(head, model.get(itera, 2)[0])
            print('from %s to %s' % (source, destination))
            try:
                if model.get(itera, 2)[0] != 'Error':
                    os.rename(source, destination)
                    model.set(itera, 1, model.get(itera, 2)[0])
            except Exception as e:
                print(e)
                model.set(itera, 2, 'Error')
            itera = model.iter_next(itera)
            num += 1

    def evalua(self, mfile, num):
        pattern = self.entry22.get_active_text()
        filename, ext = os.path.splitext(mfile)
        print(filename)
        print(ext)
        pattern = pattern.replace('{filename}', '"'+filename+'"')
        pattern = pattern.replace('{extension}', '"'+ext+'"')
        pattern = pattern.replace('{iterator}', '"'+str(num)+'"')
        print(pattern)
        return eval(pattern)


class RenameFilesMenuProvider(GObject.GObject, FileManager.MenuProvider):
    """Implements the extension to the FileManager right-click menu"""
    def __init__(self):
        """FileManager crashes if a plugin doesn't implement the __init__
        method"""
        pass

    def rename_files(self, menu, selected):
        """Runs the Replace in Filenames on the given Directory"""
        files = get_files(selected)
        if files:
            dialog = RenameDialog(files)
            dialog.run()
            dialog.hide()
            dialog.destroy()

    def get_file_items(self, window, sel_items):
        """Adds the 'Replace in Filenames' menu item to the Nemo
        right-click menu, connects its 'activate' signal to the 'run'
        method passing the selected Directory/File"""
        item = FileManager.MenuItem(
            name='RenameFilesMenuProvider::Gtk-rename-files',
            label='Renombra archivos',
            tip='Renombra archivos',
            icon='Gtk-find-and-replace')
        item.connect('activate', self.rename_files, sel_items)
        return item,

if __name__ == '__main__':
    rd = RenameDialog(None)
    rd.run()
    rd.hide()
    rd.destroy()
    exit(0)
