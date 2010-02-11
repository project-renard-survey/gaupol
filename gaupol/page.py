# Copyright (C) 2005-2009 Osmo Salomaa
#
# This file is part of Gaupol.
#
# Gaupol is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Gaupol is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaupol. If not, see <http://www.gnu.org/licenses/>.

"""User interface container and controller for a single project."""

import gaupol
import gtk
import os
import pango
import sys
_ = aeidon.i18n._

__all__ = ("Page",)


class Page(aeidon.Observable):

    """User interface container and controller for a single project.

    Instance variables:
     * edit_mode: Enumeration of the mode currently used in the view
     * project: The associated project instance
     * tab_label: gtk.Label contained in the tab_widget
     * tab_widget: Widget to use for page in a notebook tab
     * untitle: Title used if the main document is unsaved
     * view: The associated view instance

    Signals (arguments):
     * close-request (page)
     * view-created (page, view)

    This class represents one page in a notebook of user interfaces for
    projects. The view is updated automatically when project data changes.
    """

    __metaclass__ = aeidon.Contractual
    signals = ("close-request", "view-created")

    def __init__(self, count=0):
        """Initialize a Page object."""

        aeidon.Observable.__init__(self)
        self.edit_mode = gaupol.conf.editor.mode
        self.project = None
        self.tab_label = None
        self.tab_widget = None
        self.untitle = _("Untitled %d") % count
        self.view = gaupol.View(self.edit_mode)

        self._init_project()
        self._init_widgets()
        self._init_signal_handlers()
        self.update_tab_label()
        self.emit("view-created", self.view)

    def _assert_store(self, fields=None):
        """Assert that store's data matches project's."""

        if fields is None:
            fields = list(gaupol.fields)
            fields.remove(gaupol.fields.NUMBER)
        mode = self.edit_mode
        store = self.view.get_model()
        assert len(store) == len(self.project.subtitles)
        for i, subtitle in enumerate(self.project.subtitles):
            if gaupol.fields.START in fields:
                assert store[i][1] == subtitle.get_start(mode)
            if gaupol.fields.END in fields:
                assert store[i][2] == subtitle.get_end(mode)
            if gaupol.fields.DURATION in fields:
                if mode == aeidon.modes.TIME:
                    assert store[i][3] == subtitle.duration_seconds
                elif mode == aeidon.modes.FRAME:
                    assert store[i][3] == subtitle.duration_frame
            if gaupol.fields.MAIN_TEXT in fields:
                assert store[i][4] == subtitle.main_text
            if gaupol.fields.TRAN_TEXT in fields:
                assert store[i][5] == subtitle.tran_text

    def _get_subtitle_value(self, row, field):
        """Return value of subtitle data corresponding to row and field."""

        mode = self.edit_mode
        subtitle = self.project.subtitles[row]
        if field == gaupol.fields.START:
            return subtitle.get_start(mode)
        if field == gaupol.fields.END:
            return subtitle.get_end(mode)
        if field == gaupol.fields.DURATION:
            if mode == aeidon.modes.TIME:
                return subtitle.duration_seconds
            return subtitle.duration_frame
        if field == gaupol.fields.MAIN_TEXT:
            return subtitle.main_text
        if field == gaupol.fields.TRAN_TEXT:
            return subtitle.tran_text
        raise ValueError("Invalid field: %s" % repr(field))

    def _get_tab_close_button(self):
        """Initialize and return a tab close button."""

        button = gtk.Button()
        button.set_name("aeidon-tab-close-button")
        args = gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU
        image = gtk.image_new_from_stock(*args)
        button.add(image)
        button.set_relief(gtk.RELIEF_NONE)
        button.set_focus_on_click(False)
        width, height = image.size_request()
        padding = (6 if sys.platform == "win32" else 2)
        button.set_size_request(width + padding, height + padding)
        request_close = lambda x, self: self.emit("close-request")
        button.connect("clicked", request_close, self)
        button.set_tooltip_text(_("Close project"))
        return button

    def _init_project(self):
        """Initialize the project with proper properties."""

        framerate = gaupol.conf.editor.framerate
        limit = gaupol.conf.editor.limit_undo
        levels = gaupol.conf.editor.undo_levels
        undo_levels = (levels if limit else None)
        self.project = aeidon.Project(framerate, undo_levels)

    def _init_signal_handlers(self):
        """Initialize signal handlers."""

        self._init_signal_handlers_for_data()
        self._init_signal_handlers_for_tab_label()
        self._init_signal_handlers_for_undo()

    def _init_signal_handlers_for_data(self):
        """Initialize signal handlers for project data updates."""

        aeidon.util.connect(self, "project", "main-file-opened")
        aeidon.util.connect(self, "project", "main-texts-changed")
        aeidon.util.connect(self, "project", "positions-changed")
        aeidon.util.connect(self, "project", "subtitles-changed")
        aeidon.util.connect(self, "project", "subtitles-inserted")
        aeidon.util.connect(self, "project", "subtitles-removed")
        aeidon.util.connect(self, "project", "translation-file-opened")
        aeidon.util.connect(self, "project", "translation-texts-changed")

    def _init_signal_handlers_for_tab_label(self):
        """Initialize signal handlers for tab label updates."""

        aeidon.util.connect(self, "tab_label", "query-tooltip")
        update_label = lambda *args: args[-1].update_tab_label()
        self.project.connect("main-file-opened", update_label, self)
        self.project.connect("main-file-saved", update_label, self)
        self.project.connect("notify::main_changed", update_label, self)
        self.project.connect("notify::tran_changed", update_label, self)

    def _init_signal_handlers_for_undo(self):
        """Initialize signal handlers for undo level updates."""

        connect = gaupol.conf.editor.connect
        update_levels = lambda *args: args[-1]._update_undo_levels()
        connect("notify::limit_undo", update_levels, self)
        connect("notify::undo_levels", update_levels, self)

    def _init_widgets(self):
        """Initialize the widgets to use in a notebook tab."""

        self.tab_label = gtk.Label()
        self.tab_label.props.xalign = 0
        self.tab_label.set_ellipsize(pango.ELLIPSIZE_END)
        self.tab_label.set_max_width_chars(24)
        self.tab_label.set_tooltip_text(self.untitle)
        button = self._get_tab_close_button()
        hbox = gtk.HBox(False, 4)
        hbox.pack_start(self.tab_label, True, True, 0)
        hbox.pack_start(button, False, False, 0)
        hbox.set_data("button", button)
        self.tab_widget = gtk.EventBox()
        self.tab_widget.add(hbox)
        self.tab_widget.show_all()

    def _on_project_main_file_opened(self, *args):
        """Reload the entire view."""

        self.reload_view_all()
        gaupol.util.iterate_main()

    def _on_project_main_texts_changed(self, project, rows):
        """Reload and select main texts in rows."""

        if not rows: return
        fields = (gaupol.fields.MAIN_TEXT,)
        self.reload_view(rows, fields)
        if self.view.get_focus()[0] not in rows:
            col = self.view.columns.MAIN_TEXT
            self.view.set_focus(rows[0], col)
        self.view.select_rows(rows)
        gaupol.util.iterate_main()

    def _on_project_positions_changed(self, project, rows):
        """Reload and select positions in rows."""

        if not rows: return
        enum = gaupol.fields
        fields = (enum.START, enum.END, enum.DURATION)
        self.reload_view(rows, fields)
        if self.view.get_focus()[0] not in rows:
            self.view.set_focus(rows[0])
        self.view.select_rows(rows)
        gaupol.util.iterate_main()

    def _on_project_subtitles_changed(self, project, rows):
        """Reload and select subtitles in rows."""

        if not rows: return
        fields = [x for x in gaupol.fields]
        fields.remove(gaupol.fields.NUMBER)
        self.reload_view(rows, fields)
        if self.view.get_focus()[0] not in rows:
            self.view.set_focus(rows[0])
        self.view.select_rows(rows)
        gaupol.util.iterate_main()

    def _on_project_subtitles_inserted_ensure(self, value, project, rows):
        self._assert_store()

    def _on_project_subtitles_inserted(self, project, rows):
        """Insert rows to the view and select them."""

        if not rows: return
        mode = self.edit_mode
        store = self.view.get_model()
        for row in sorted(rows):
            subtitle = self.project.subtitles[row]
            store.insert(row)
            store[row][0] = row + 1
            store[row][1] = subtitle.get_start(mode)
            store[row][2] = subtitle.get_end(mode)
            if mode == aeidon.modes.TIME:
                store[row][3] = subtitle.duration_seconds
            elif mode == aeidon.modes.FRAME:
                store[row][3] = subtitle.duration_frame
            store[row][4] = subtitle.main_text
            store[row][5] = subtitle.tran_text
        self.view.set_focus(rows[0])
        self.view.select_rows(rows)
        gaupol.util.iterate_main()

    def _on_project_subtitles_removed_ensure(self, value, project, rows):
        self._assert_store()

    def _on_project_subtitles_removed(self, project, rows):
        """Remove rows from the view."""

        if not rows: return
        store = self.view.get_model()
        if len(rows) > 50:
            # Unset and later reset the model if removing a large amount of
            # rows, because a large batch of separate live updates directly
            # made to the view are slow, 50 being a rough empirical border.
            self.view.set_model(None)
        for row in reversed(sorted(rows)):
            store.remove(store.get_iter(row))
        if len(rows) > 50:
            self.view.set_model(store)
        if self.project.subtitles:
            row = min(rows[0], len(self.project.subtitles) - 1)
            col = self.view.get_focus()[1]
            self.view.set_focus(row, col)
        gaupol.util.iterate_main()

    def _on_project_translation_file_opened(self, *args):
        """Reload the entire view."""

        self.reload_view_all()
        gaupol.util.iterate_main()

    def _on_project_translation_texts_changed(self, project, rows):
        """Reload and select translation texts in rows."""

        if not rows: return
        fields = (gaupol.fields.TRAN_TEXT,)
        self.reload_view(rows, fields)
        if self.view.get_focus()[0] not in rows:
            col = self.view.columns.TRAN_TEXT
            self.view.set_focus(rows[0], col)
        self.view.select_rows(rows)
        gaupol.util.iterate_main()

    def _on_tab_label_query_tooltip(self, label, x, y, keyboard, tooltip):
        """Update the text in the tab tooltip."""

        main_file = self.project.main_file
        if main_file is None: return
        encoding = aeidon.encodings.code_to_long_name(main_file.encoding)
        markup  = _("<b>Path:</b> %s") % main_file.path + "\n\n"
        markup += _("<b>Format:</b> %s") % main_file.format.label + "\n"
        markup += _("<b>Character encoding:</b> %s") % encoding + "\n"
        markup += _("<b>Newlines:</b> %s") % main_file.newline.label
        tooltip.set_markup(markup)
        return True # to show the tooltip.

    def _update_undo_levels(self):
        """Update project's undo level count to match global configuration."""

        limit = gaupol.conf.editor.limit_undo
        limit = (gaupol.conf.editor.undo_levels if limit else None)
        self.project.undo_limit = limit

    def document_to_text_column(self, doc):
        """Translate document enumeration to view's column enumeration."""

        if doc == aeidon.documents.MAIN:
            return self.view.columns.MAIN_TEXT
        if doc == aeidon.documents.TRAN:
            return self.view.columns.TRAN_TEXT
        raise ValueError("Invalid document: %s" % repr(doc))

    def get_main_basename(self):
        """Return the basename of the main document."""

        if self.project.main_file is not None:
            return os.path.basename(self.project.main_file.path)
        return self.untitle

    def get_translation_basename(self):
        """Return the basename of the translation document."""

        if self.project.tran_file is not None:
            return os.path.basename(self.project.tran_file.path)
        basename = self.get_main_basename()
        if self.project.main_file is not None:
            extension = self.project.main_file.format.extension
            if basename.endswith(extension):
                basename = basename[:-len(extension)]
        return _("%s translation") % basename

    def reload_view_ensure(self, value, rows, fields):
        self._assert_store(fields)

    def reload_view(self, rows, fields):
        """Reload the view in rows and columns."""

        mode = self.edit_mode
        store = self.view.get_model()
        for row, field in ((x, y) for x in rows for y in fields):
            value = self._get_subtitle_value(row, field)
            store[row][field] = value

    def reload_view_all_ensure(self, value):
        self._assert_store()

    def reload_view_all(self):
        """Clear and repopulate the entire view."""

        store = self.view.get_model()
        self.view.set_model(None)
        store.clear()
        mode = self.edit_mode
        for i, subtitle in enumerate(self.project.subtitles):
            store.insert(i)
            store[i][0] = i + 1
            store[i][1] = subtitle.get_start(mode)
            store[i][2] = subtitle.get_end(mode)
            if mode == aeidon.modes.TIME:
                store[i][3] = subtitle.duration_seconds
            elif mode == aeidon.modes.FRAME:
                store[i][3] = subtitle.duration_frame
            store[i][4] = subtitle.main_text
            store[i][5] = subtitle.tran_text
        self.view.set_model(store)

    def text_column_to_document(self, col):
        """Translate view's column enumeration to document enumeration."""

        if col == self.view.columns.MAIN_TEXT:
            return aeidon.documents.MAIN
        if col == self.view.columns.TRAN_TEXT:
            return aeidon.documents.TRAN
        raise ValueError("Invalid column: %s" % repr(col))

    def update_tab_label(self):
        """Update the notebook tab label and return the title."""

        title = self.get_main_basename()
        if self.project.main_changed or self.project.tran_changed:
            title = "*%s" % title
        self.tab_label.set_text(title)
        return title