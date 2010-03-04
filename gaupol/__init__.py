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

"""GTK+ user interface for the Gaupol subtitle editor.

:var COMBO_SEPARATOR: String used as a separator for :class:`gtk.ComboBox`

   :attr:`COMBO_SEPARATOR` can be inserted into a combo box's model, and
   :func:`gaupol.util.separate_combo` will recognize it.

:var fields: Enumerations for subtitle field types
:var length_units: Enumerations for length unit types
:var targets: Enumerations for action target types
:var toolbar_styles: Enumerations for toolbar style types

:var field_actions: Dictionary mapping :attr:`gaupol.formats` to actions
:var framerate_actions: Dictionary mapping :attr:`aeidon.framerates` to actions
:var mode_actions: Dictionary mapping :attr:`aeidon.modes` to actions
"""

import aeidon
import gobject
import gtk
import os

__version__ = "0.15.99"

COMBO_SEPARATOR = "<separator/>"

gtk.rc_parse(os.path.join(aeidon.DATA_DIR, "ui", "gtkrc"))
gobject.threads_init()

from gaupol.unittest import *
from gaupol import util
from gaupol.enums.fields import *
from gaupol.enums.styles import *
from gaupol.enums.targets import *
from gaupol.enums.units import *
from gaupol.enumuim import *
from gaupol.errors import *
from gaupol.attrdict import *
from gaupol.config import *
conf = ConfigurationStore()
from gaupol import ruler
from gaupol.meta import *
from gaupol.entries import *
from gaupol.renderers import *
from gaupol.output import *
from gaupol.view import *
from gaupol.page import *
from gaupol.extension import *
from gaupol.dialogs.about import *
from gaupol.dialogs.builder import *
from gaupol.dialogs.debug import *
from gaupol.dialogs.encoding import *
from gaupol.dialogs.file import *
from gaupol.dialogs.language import *
from gaupol.dialogs.message import *
from gaupol.dialogs.open import *
from gaupol.dialogs.previewerr import *
from gaupol.dialogs.save import *
from gaupol.dialogs.textedit import *
from gaupol.dialogs.video import *
