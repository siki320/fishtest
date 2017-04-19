######################## BEGIN LICENSE BLOCK ########################
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301  USA
######################### END LICENSE BLOCK #########################


# ------- add by caiyifeng -------
# add current path to pythonpath
import os, sys
current_path = os.path.abspath( os.path.dirname(__file__) )
if current_path not in sys.path:
    sys.path.append(current_path)
# ------- (end) add by caiyifeng -------


__version__ = "1.0.1"

def detect(aBuf):
    import universaldetector
    u = universaldetector.UniversalDetector()
    u.reset()
    u.feed(aBuf)
    u.close()
    return u.result
