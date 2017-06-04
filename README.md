Only the `PropUtils.py` and `sprite-data` files are required.

**Usage**
```python
import dustmaker
from PropUtils import PropUtils, Pivot

with open('map.file', 'rb') as f:
	map = dustmaker.read_map(f.read())

# If props are scaled, make sure to set use_scale=True
prop_utils = PropUtils()

# Get prop data by index
set_index = 1
group_index = 0
sprite_index = 1
prop_data = prop_utils.prop_data[set_index][group_index]['sprites'][sprite_index]

# Get prop data by name.
# Format: "GROUP_NAME PROP_NAME"
# See sprite-data.json for sprite names
prop1_data = prop_utils.name_prop_map['lighting city_lamp_standing']
prop2_data = prop_utils.name_prop_map['foliage flower_red']

# Create a prop from data
prop1 = PropUtils.from_data(prop1_data)
prop2 = PropUtils.from_data(prop2_data)

# Place a prop centred at a 0, 0
pos = prop_utils.set_prop_location(0, 0, prop1, Pivot.CENTRE, prop1_data)
map.add_prop(19, pos[0], pos[1], prop1)

# Other pivot points can be used, eg. TOP_LEFT, BOTTOM
# Some props also have a more "logical" pivot defined. Use Pivot.ATTACHMENT
pos = prop_utils.set_prop_location(10, 0, prop2, Pivot.ATTACHMENT, prop2_data)
map.add_prop(19, pos[0], pos[1], prop2)
```
