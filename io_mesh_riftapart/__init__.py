# MIT License
# 
# Copyright (c) 2022 thtrandomlurker
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

bl_info = {
    "name": "Rift Apart Model",
    "author": "Thatrandomlurker",
    "version": (0, 0, 1),
    "blender": (3, 1, 2),
    "location": "File > Import-Export",
    "description": "Import Ratchet & Clank Rift Apart .model files",
    "warning": "",
    "doc_url": "",
    "support": 'TESTING',
    "category": "Import-Export",
}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

class ImportRiftApartModel(Operator, ImportHelper):
    """Import a .model file from RaC PS5"""
    bl_idname = "rift_apart.import_model"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Rift Apart Model"
    from . import import_model

    # ImportHelper mixin class uses this
    filename_ext = ".model"

    filter_glob: StringProperty(
        default="*.model",
        options={'HIDDEN'}
    )

    def execute(self, context):
        return import_model.ReadModelFile(context, self.filepath)
    
def menu_func_import(self, context):
    self.layout.operator(ImportRiftApartModel.bl_idname, text="Import Rift Apart Model")

# Register and add to the "file selector" menu (required to use F3 search "Text Import Operator" for quick access)
def register():
    bpy.utils.register_class(ImportRiftApartModel)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportRiftApartModel)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
