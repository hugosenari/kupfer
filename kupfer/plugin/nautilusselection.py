import os

import dbus
import gobject

from kupfer.objects import Source, Leaf
from kupfer.objects import FileLeaf, SourceLeaf
from kupfer.obj.compose import MultipleLeaf
from kupfer.obj.helplib import PicklingHelperMixin
from kupfer.weaklib import DbusWeakCallback
from kupfer import plugin_support

__kupfer_name__ = _("Selected File")
__kupfer_sources__ = ("SelectionSource", )
__description__ = _("Provides current nautilus selection, using Kupfer's Nautilus Extension")
__version__ = ""
__author__ = "Ulrik Sverdrup <ulrik.sverdrup@gmail.com>"

plugin_support.check_dbus_connection()

class SelectedFile (FileLeaf):
	qf_id = "selectedfile"
	def __init__(self, filepath):
		"""@filepath is a filesystem byte string `str`"""
		basename = gobject.filename_display_basename(filepath)
		FileLeaf.__init__(self, filepath, _('Selected File "%s"') % basename)

	def __repr__(self):
		return "<%s %s>" % (__name__, self.qf_id)

class SelectedFiles (MultipleLeaf):
	qf_id = "selectedfile"
	def __init__(self, paths):
		files = [FileLeaf(path) for path in paths]
		MultipleLeaf.__init__(self, files, "Selected Files")

	def __repr__(self):
		return "<%s %s>" % (__name__, self.qf_id)

class InvisibleSourceLeaf (SourceLeaf):
	"""Hack to hide this source"""
	def is_valid(self):
		return False

class SelectionSource (Source, PicklingHelperMixin):
	def __init__(self):
		Source.__init__(self, _("Selected File"))
		self.unpickle_finish()

	def unpickle_finish(self):
		self._selection = []

	def initialize(self):
		session_bus = dbus.Bus()
		callback = DbusWeakCallback(self._selected_signal)
		callback.token = session_bus.add_signal_receiver(
				callback,
				"SelectionChanged",
				dbus_interface="se.kaizer.KupferNautilusPlugin",
				byte_arrays=True)

	def _selected_signal(self, selection):
		self._selection = selection
		self.mark_for_update()

	def get_items(self):
		if len(self._selection) == 1:
			yield SelectedFile(self._selection[0])
		elif len(self._selection) > 1:
			yield SelectedFiles(self._selection)

	def get_description(self):
		return None
	def provides(self):
		yield FileLeaf
		yield MultipleLeaf
	def get_leaf_repr(self):
		return InvisibleSourceLeaf(self)
