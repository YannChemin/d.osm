#!/usr/bin/env python3

############################################################################
#
# MODULE:        d.osm
# AUTHOR(S):     Yann Chemin
# PURPOSE:       Fetch OSINT-relevant OpenStreetMap features from the
#                Overpass API for the current computational region and
#                display them with pre-baked GRASS symbols.
# COPYRIGHT:     (C) 2026 by Yann Chemin
#
#                This program is free and unencumbered software released
#                into the public domain. See the UNLICENSE file that comes
#                with this addon for details, or https://unlicense.org
#
#############################################################################

# %module
# % description: Fetch OSM features (military installations, checkpoints, power infrastructure, communications towers) from Overpass for the current region and display them.
# % keyword: display
# % keyword: vector
# % keyword: OSM
# % keyword: OSINT
# %end
# %option
# % key: types
# % type: string
# % required: no
# % multiple: yes
# % options: military_airfield,military_base,bunker,naval_base,training_area,checkpoint,border_control,power_plant,substation,communications_tower
# % description: Which feature types to query (default: all)
# %end
# %option G_OPT_V_OUTPUT
# % key: output
# % required: no
# % answer: osm
# % description: Name for the imported vector map
# %end
# %option
# % key: format
# % type: string
# % required: no
# % options: symbols,attributes
# % answer: symbols
# % description: symbols renders each feature type with its icon; attributes only prints the matching attribute table
# %end
# %option
# % key: size
# % type: integer
# % required: no
# % answer: 20
# % description: Symbol size in format=symbols mode
# %end
# %option
# % key: endpoint
# % type: string
# % required: no
# % answer: https://overpass-api.de/api/interpreter
# % description: Overpass API endpoint URL
# %end
# %option
# % key: timeout
# % type: integer
# % required: no
# % answer: 60
# % description: Overpass query timeout in seconds
# %end

"""Fetch OSINT-relevant OSM features from Overpass for the current
computational region and display them with pre-baked GRASS symbols.

Fully independent, fully open-source companion to the private d.osint
addon: no local database, no dependency on any other project's code, no
non-stdlib Python dependency (json/urllib only -- GDAL/OGR is still used
internally by v.in.ogr, but that's GRASS's own business). Every query is
live against the public Overpass API for whatever the current GRASS
computational region happens to be.

All ten GRASS symbol files are embedded below as static text, generated
once (ahead of time, not at runtime) from openly-licensed sources via the
public-domain `svg2grasssymbol` converter -- see this addon's README.md
for provenance. There is no live SVG-to-symbol conversion step here.
"""

import json
import os
import tempfile
import urllib.error
import urllib.parse
import urllib.request

import grass.script as gs

GRASS_SYMBOL_GROUP = "osm"

# tag_key/tag_value select the Overpass query and classify results;
# symbol is the bundled GRASS symbol name (see _SYMBOLS below); label is
# the human-readable name shown in the "label" attribute column.
RULES = [
    {"tag_key": "military", "tag_value": "airfield", "symbol": "military_airfield", "label": "Military Airfield"},
    {"tag_key": "military", "tag_value": "base", "symbol": "military_base", "label": "Military Base"},
    {"tag_key": "military", "tag_value": "bunker", "symbol": "bunker", "label": "Bunker"},
    {"tag_key": "military", "tag_value": "naval_base", "symbol": "naval_base", "label": "Naval Base"},
    {"tag_key": "military", "tag_value": "training_area", "symbol": "training_area", "label": "Training Area"},
    {"tag_key": "barrier", "tag_value": "checkpoint", "symbol": "checkpoint", "label": "Checkpoint"},
    {"tag_key": "amenity", "tag_value": "border_control", "symbol": "border_control", "label": "Border Control"},
    {"tag_key": "power", "tag_value": "plant", "symbol": "power_plant", "label": "Power Plant"},
    {"tag_key": "power", "tag_value": "substation", "symbol": "substation", "label": "Substation"},
    {"tag_key": "man_made", "tag_value": "communications_tower", "symbol": "communications_tower", "label": "Communications Tower"},
]
# --- begin embedded GRASS symbols (generated once from symbols/*.svg via
# the standalone svg2grasssymbol converter -- see README.md) ---
_SYMBOLS = {
    "border_control": """VERSION 1.0
BOX -7.5000 -7.5000 7.5000 7.5000
POLYGON
 RING
  LINE
   -6.5000 4.7500
   -6.4964 4.8235
   -6.4856 4.8963
   -6.4677 4.9677
   -6.4429 5.0370
   -6.4114 5.1035
   -6.3736 5.1667
   -6.3298 5.2258
   -6.2803 5.2803
   -6.2258 5.3298
   -6.1667 5.3736
   -6.1035 5.4114
   -6.0370 5.4429
   -5.9677 5.4677
   -5.8963 5.4856
   -5.8235 5.4964
   -5.7500 5.5000
   -4.6360 5.5000
   -4.6135 5.4997
   -4.5910 5.4987
   -4.5686 5.4970
   -4.5463 5.4947
   -4.5240 5.4917
   -4.5019 5.4880
   -4.4799 5.4837
   -4.4581 5.4787
   -4.4365 5.4730
   -4.4151 5.4667
   -4.3939 5.4597
   -4.3730 5.4520
   -0.9870 4.1820
   -0.9346 4.1601
   -0.8840 4.1343
   -0.8355 4.1047
   -0.7894 4.0715
   -0.7459 4.0350
   -0.7053 3.9952
   -0.6679 3.9525
   -0.6338 3.9071
   -0.6032 3.8593
   -0.5763 3.8092
   -0.5533 3.7573
   -0.5343 3.7038
   -0.5194 3.6490
   -0.5086 3.5932
   -0.5022 3.5368
   -0.5000 3.4800
   -0.5000 -2.4800
   -0.5022 -2.5368
   -0.5086 -2.5932
   -0.5194 -2.6490
   -0.5343 -2.7038
   -0.5533 -2.7573
   -0.5763 -2.8092
   -0.6032 -2.8593
   -0.6338 -2.9071
   -0.6679 -2.9525
   -0.7053 -2.9952
   -0.7459 -3.0350
   -0.7894 -3.0715
   -0.8355 -3.1047
   -0.8840 -3.1343
   -0.9346 -3.1601
   -0.9870 -3.1820
   -4.5000 -4.5000
   -4.5000 -4.7500
   -4.5036 -4.8235
   -4.5144 -4.8963
   -4.5323 -4.9677
   -4.5571 -5.0370
   -4.5886 -5.1035
   -4.6264 -5.1667
   -4.6702 -5.2258
   -4.7197 -5.2803
   -4.7742 -5.3298
   -4.8333 -5.3736
   -4.8965 -5.4114
   -4.9630 -5.4429
   -5.0323 -5.4677
   -5.1037 -5.4856
   -5.1765 -5.4964
   -5.2500 -5.5000
   -5.7500 -5.5000
   -5.8235 -5.4964
   -5.8963 -5.4856
   -5.9677 -5.4677
   -6.0370 -5.4429
   -6.1035 -5.4114
   -6.1667 -5.3736
   -6.2258 -5.3298
   -6.2803 -5.2803
   -6.3298 -5.2258
   -6.3736 -5.1667
   -6.4114 -5.1035
   -6.4429 -5.0370
   -6.4677 -4.9677
   -6.4856 -4.8963
   -6.4964 -4.8235
   -6.5000 -4.7500
   -6.5000 4.7500
  END
 END
 RING
  LINE
   -3.5000 -0.9860
   -3.5000 3.8840
   -3.5007 3.9029
   -3.5029 3.9217
   -3.5064 3.9403
   -3.5114 3.9585
   -3.5177 3.9764
   -3.5253 3.9937
   -3.5343 4.0104
   -3.5445 4.0263
   -3.5558 4.0414
   -3.5683 4.0557
   -3.5818 4.0689
   -3.5962 4.0811
   -3.6116 4.0922
   -3.6277 4.1021
   -3.6446 4.1107
   -3.6620 4.1180
   -4.1620 4.3050
   -4.1908 4.3139
   -4.2205 4.3192
   -4.2506 4.3210
   -4.2807 4.3191
   -4.3103 4.3136
   -4.3391 4.3046
   -4.3665 4.2922
   -4.3923 4.2765
   -4.4160 4.2579
   -4.4373 4.2366
   -4.4559 4.2128
   -4.4714 4.1870
   -4.4838 4.1595
   -4.4928 4.1307
   -4.4982 4.1011
   -4.5000 4.0710
   -4.5000 -1.1530
   -4.4966 -1.1944
   -4.4869 -1.2333
   -4.4714 -1.2693
   -4.4507 -1.3020
   -4.4254 -1.3309
   -4.3961 -1.3555
   -4.3635 -1.3755
   -4.3280 -1.3903
   -4.2903 -1.3997
   -4.2510 -1.4030
   -4.2107 -1.3999
   -4.1700 -1.3900
   -3.6700 -1.2240
   -3.6518 -1.2170
   -3.6341 -1.2087
   -3.6172 -1.1990
   -3.6011 -1.1879
   -3.5859 -1.1757
   -3.5716 -1.1623
   -3.5585 -1.1479
   -3.5466 -1.1325
   -3.5358 -1.1161
   -3.5264 -1.0990
   -3.5184 -1.0813
   -3.5117 -1.0629
   -3.5066 -1.0441
   -3.5029 -1.0249
   -3.5007 -1.0055
   -3.5000 -0.9860
  END
 END
 RING
  LINE
   -2.5000 3.3200
   -2.5000 -0.4870
   -2.4984 -0.5166
   -2.4932 -0.5459
   -2.4847 -0.5743
   -2.4728 -0.6015
   -2.4578 -0.6271
   -2.4399 -0.6508
   -2.4192 -0.6721
   -2.3962 -0.6909
   -2.3712 -0.7068
   -2.3444 -0.7196
   -2.3163 -0.7292
   -2.2872 -0.7354
   -2.2577 -0.7380
   -2.2280 -0.7372
   -2.1986 -0.7328
   -2.1700 -0.7250
   -1.6700 -0.5580
   -1.6518 -0.5510
   -1.6341 -0.5427
   -1.6172 -0.5330
   -1.6011 -0.5219
   -1.5859 -0.5097
   -1.5716 -0.4963
   -1.5585 -0.4819
   -1.5466 -0.4665
   -1.5358 -0.4501
   -1.5264 -0.4330
   -1.5184 -0.4153
   -1.5117 -0.3969
   -1.5066 -0.3781
   -1.5029 -0.3589
   -1.5007 -0.3395
   -1.5000 -0.3200
   -1.5000 3.1340
   -1.5007 3.1529
   -1.5029 3.1717
   -1.5064 3.1903
   -1.5114 3.2085
   -1.5177 3.2264
   -1.5253 3.2437
   -1.5343 3.2604
   -1.5445 3.2763
   -1.5558 3.2914
   -1.5683 3.3057
   -1.5818 3.3189
   -1.5962 3.3311
   -1.6116 3.3422
   -1.6277 3.3521
   -1.6446 3.3607
   -1.6620 3.3680
   -2.1620 3.5550
   -2.1908 3.5639
   -2.2205 3.5692
   -2.2506 3.5710
   -2.2807 3.5691
   -2.3103 3.5636
   -2.3391 3.5546
   -2.3665 3.5422
   -2.3923 3.5265
   -2.4160 3.5079
   -2.4373 3.4866
   -2.4559 3.4628
   -2.4714 3.4370
   -2.4838 3.4095
   -2.4928 3.3807
   -2.4982 3.3511
   -2.5000 3.3210
  END
 END
 RING
  LINE
   6.5000 4.7500
   6.4964 4.8235
   6.4856 4.8963
   6.4677 4.9677
   6.4429 5.0370
   6.4114 5.1035
   6.3736 5.1667
   6.3298 5.2258
   6.2803 5.2803
   6.2258 5.3298
   6.1667 5.3736
   6.1035 5.4114
   6.0370 5.4429
   5.9677 5.4677
   5.8963 5.4856
   5.8235 5.4964
   5.7500 5.5000
   4.6360 5.5000
   4.6192 5.4998
   4.6024 5.4992
   4.5856 5.4982
   4.5689 5.4969
   4.5522 5.4952
   4.5355 5.4931
   4.5189 5.4906
   4.5023 5.4878
   4.4859 5.4846
   4.4694 5.4810
   4.4531 5.4771
   4.4369 5.4728
   4.4207 5.4681
   4.4047 5.4631
   4.3888 5.4577
   4.3730 5.4520
   0.9870 4.1820
   0.9346 4.1601
   0.8840 4.1343
   0.8355 4.1047
   0.7894 4.0715
   0.7459 4.0350
   0.7053 3.9952
   0.6679 3.9525
   0.6338 3.9071
   0.6032 3.8593
   0.5763 3.8092
   0.5533 3.7573
   0.5343 3.7038
   0.5194 3.6490
   0.5086 3.5932
   0.5022 3.5368
   0.5000 3.4800
   0.5000 -2.4800
   0.5022 -2.5368
   0.5086 -2.5932
   0.5194 -2.6490
   0.5343 -2.7038
   0.5533 -2.7573
   0.5763 -2.8092
   0.6032 -2.8593
   0.6338 -2.9071
   0.6679 -2.9525
   0.7053 -2.9952
   0.7459 -3.0350
   0.7894 -3.0715
   0.8355 -3.1047
   0.8840 -3.1343
   0.9346 -3.1601
   0.9870 -3.1820
   4.5000 -4.5000
   4.5000 -4.7500
   4.5069 -4.8517
   4.5268 -4.9493
   4.5590 -5.0418
   4.6024 -5.1284
   4.6563 -5.2082
   4.7198 -5.2802
   4.7918 -5.3437
   4.8716 -5.3976
   4.9582 -5.4410
   5.0507 -5.4732
   5.1483 -5.4931
   5.2500 -5.5000
   5.7500 -5.5000
   5.8235 -5.4964
   5.8963 -5.4856
   5.9677 -5.4677
   6.0370 -5.4429
   6.1035 -5.4114
   6.1667 -5.3736
   6.2258 -5.3298
   6.2803 -5.2803
   6.3298 -5.2258
   6.3736 -5.1667
   6.4114 -5.1035
   6.4429 -5.0370
   6.4677 -4.9677
   6.4856 -4.8963
   6.4964 -4.8235
   6.5000 -4.7500
   6.5000 4.7500
  END
 END
 RING
  LINE
   3.6700 -1.2240
   3.6518 -1.2170
   3.6341 -1.2087
   3.6172 -1.1990
   3.6011 -1.1879
   3.5859 -1.1757
   3.5716 -1.1623
   3.5585 -1.1479
   3.5466 -1.1325
   3.5358 -1.1161
   3.5264 -1.0990
   3.5184 -1.0813
   3.5117 -1.0629
   3.5066 -1.0441
   3.5029 -1.0249
   3.5007 -1.0055
   3.5000 -0.9860
   3.5000 3.8840
   3.5007 3.9029
   3.5029 3.9217
   3.5064 3.9403
   3.5114 3.9585
   3.5177 3.9764
   3.5253 3.9937
   3.5343 4.0104
   3.5445 4.0263
   3.5558 4.0414
   3.5683 4.0557
   3.5818 4.0689
   3.5962 4.0811
   3.6116 4.0922
   3.6277 4.1021
   3.6446 4.1107
   3.6620 4.1180
   4.1620 4.3050
   4.1908 4.3139
   4.2205 4.3192
   4.2506 4.3210
   4.2807 4.3191
   4.3103 4.3136
   4.3391 4.3046
   4.3665 4.2922
   4.3923 4.2765
   4.4160 4.2579
   4.4373 4.2366
   4.4559 4.2128
   4.4714 4.1870
   4.4838 4.1595
   4.4928 4.1307
   4.4982 4.1011
   4.5000 4.0710
   4.5000 -1.1530
   4.4983 -1.1826
   4.4930 -1.2117
   4.4844 -1.2401
   4.4725 -1.2672
   4.4574 -1.2927
   4.4395 -1.3163
   4.4188 -1.3375
   4.3958 -1.3562
   4.3708 -1.3720
   4.3440 -1.3848
   4.3160 -1.3943
   4.2870 -1.4004
   4.2575 -1.4030
   4.2279 -1.4022
   4.1986 -1.3978
   4.1700 -1.3900
   3.6700 -1.2240
  END
 END
 RING
  LINE
   2.5000 3.3210
   2.5000 -0.4860
   2.4984 -0.5156
   2.4932 -0.5449
   2.4847 -0.5733
   2.4728 -0.6005
   2.4578 -0.6261
   2.4399 -0.6498
   2.4192 -0.6711
   2.3962 -0.6899
   2.3712 -0.7058
   2.3444 -0.7186
   2.3163 -0.7282
   2.2872 -0.7344
   2.2577 -0.7370
   2.2280 -0.7362
   2.1986 -0.7318
   2.1700 -0.7240
   1.6700 -0.5570
   1.6518 -0.5501
   1.6342 -0.5417
   1.6174 -0.5321
   1.6013 -0.5211
   1.5861 -0.5089
   1.5719 -0.4956
   1.5588 -0.4812
   1.5469 -0.4659
   1.5361 -0.4496
   1.5267 -0.4326
   1.5186 -0.4149
   1.5120 -0.3966
   1.5068 -0.3779
   1.5030 -0.3588
   1.5007 -0.3394
   1.5000 -0.3200
   1.5000 3.1340
   1.5007 3.1529
   1.5029 3.1717
   1.5064 3.1903
   1.5114 3.2085
   1.5177 3.2264
   1.5253 3.2437
   1.5343 3.2604
   1.5445 3.2763
   1.5558 3.2914
   1.5683 3.3057
   1.5818 3.3189
   1.5962 3.3311
   1.6116 3.3422
   1.6277 3.3521
   1.6446 3.3607
   1.6620 3.3680
   2.1620 3.5550
   2.1908 3.5639
   2.2205 3.5692
   2.2506 3.5710
   2.2807 3.5691
   2.3103 3.5636
   2.3391 3.5546
   2.3665 3.5422
   2.3923 3.5265
   2.4160 3.5079
   2.4373 3.4866
   2.4559 3.4628
   2.4714 3.4370
   2.4838 3.4095
   2.4928 3.3807
   2.4982 3.3511
   2.5000 3.3210
  END
 END
END
""",
    "bunker": """VERSION 1.0
BOX -12.0000 -12.0000 12.0000 12.0000
POLYGON
 RING
  LINE
   -8.0000 -8.0000
   -8.0000 -6.0000
   -7.8463 -4.4393
   -7.3910 -2.9385
   -6.6518 -1.5554
   -5.6569 -0.3431
   -4.4446 0.6518
   -3.0615 1.3910
   -1.5607 1.8463
   -0.0000 2.0000
   1.5607 1.8463
   3.0615 1.3910
   4.4446 0.6518
   5.6569 -0.3431
   6.6518 -1.5554
   7.3910 -2.9385
   7.8463 -4.4393
   8.0000 -6.0000
   8.0000 -8.0000
  END
 END
END
""",
    "checkpoint": """VERSION 1.0
BOX -7.5000 -7.5000 7.5000 7.5000
POLYGON
 RING
  LINE
   0.0000 -6.5000
   0.8820 -6.4407
   1.7280 -6.2678
   2.5301 -5.9892
   3.2807 -5.6126
   3.9720 -5.1457
   4.5962 -4.5962
   5.1457 -3.9720
   5.6126 -3.2807
   5.9892 -2.5301
   6.2678 -1.7280
   6.4407 -0.8820
   6.5000 0.0000
   6.4407 0.8820
   6.2678 1.7280
   5.9892 2.5301
   5.6126 3.2807
   5.1457 3.9720
   4.5962 4.5962
   3.9720 5.1456
   3.2807 5.6126
   2.5301 5.9892
   1.7280 6.2678
   0.8820 6.4407
   0.0000 6.5000
   -0.8820 6.4407
   -1.7280 6.2678
   -2.5301 5.9892
   -3.2807 5.6126
   -3.9720 5.1456
   -4.5962 4.5962
   -5.1456 3.9720
   -5.6126 3.2807
   -5.9892 2.5301
   -6.2678 1.7280
   -6.4407 0.8820
   -6.5000 0.0000
   -6.4407 -0.8820
   -6.2678 -1.7280
   -5.9892 -2.5301
   -5.6126 -3.2807
   -5.1456 -3.9720
   -4.5962 -4.5962
   -3.9720 -5.1457
   -3.2807 -5.6126
   -2.5301 -5.9892
   -1.7280 -6.2678
   -0.8820 -6.4407
   0.0000 -6.5000
  END
 END
 RING
  LINE
   4.5000 1.5000
   4.5000 -1.5000
   -4.5000 -1.5000
   -4.5000 1.5000
   4.5000 1.5000
  END
 END
END
""",
    "communications_tower": """VERSION 1.0
BOX -7.5000 -7.5000 7.5000 7.5000
POLYGON
 RING
  LINE
   4.3545 1.0664
   3.9414 1.3477
   4.1124 1.6189
   4.2648 1.9010
   4.3978 2.1926
   4.5109 2.4926
   4.6036 2.7995
   4.6754 3.1120
   4.7261 3.4286
   4.7553 3.7478
   4.7630 4.0683
   4.7491 4.3886
   4.7136 4.7073
   4.6568 5.0228
   4.5790 5.3338
   4.4803 5.6388
   4.3614 5.9366
   4.2227 6.2256
   4.1392 6.3789
   4.5747 6.6250
   4.6655 6.4580
   4.8189 6.1385
   4.9504 5.8095
   5.0595 5.4723
   5.1456 5.1285
   5.2084 4.7798
   5.2476 4.4276
   5.2629 4.0735
   5.2545 3.7193
   5.2222 3.3664
   5.1662 3.0164
   5.0867 2.6711
   4.9843 2.3318
   4.8592 2.0003
   4.7121 1.6779
   4.5436 1.3661
   4.3545 1.0664
  END
 END
 RING
  LINE
   5.5066 -6.0652
   5.5066 -6.5000
   -5.4934 -6.5000
   -5.4934 -6.0652
   -3.0048 -6.0652
   -1.4561 1.1000
   -1.4454 1.1411
   -1.4312 1.1811
   -1.4138 1.2197
   -1.3930 1.2568
   -1.3693 1.2919
   -1.3426 1.3249
   -1.3132 1.3556
   -1.2814 1.3836
   -1.2473 1.4088
   -1.2111 1.4311
   -1.1732 1.4502
   -1.1338 1.4660
   -1.0933 1.4784
   -1.0518 1.4873
   -1.0097 1.4927
   -0.9673 1.4945
   -0.2418 1.4945
   -0.2418 2.8986
   -0.3335 2.9239
   -0.4227 2.9568
   -0.5089 2.9970
   -0.5914 3.0442
   -0.6697 3.0981
   -0.7433 3.1584
   -0.8115 3.2246
   -0.8740 3.2963
   -0.9304 3.3729
   -0.9801 3.4540
   -1.0229 3.5389
   -1.0585 3.6271
   -1.0866 3.7179
   -1.1070 3.8108
   -1.1197 3.9050
   -1.1244 4.0000
   -1.1022 4.2257
   -1.0363 4.4427
   -0.9294 4.6427
   -0.7856 4.8180
   -0.6103 4.9618
   -0.4103 5.0687
   -0.1933 5.1346
   0.0324 5.1568
   0.2581 5.1346
   0.4751 5.0687
   0.6751 4.9618
   0.8504 4.8180
   0.9942 4.6427
   1.1011 4.4427
   1.1670 4.2257
   1.1892 4.0000
   1.1842 3.9020
   1.1707 3.8047
   1.1489 3.7090
   1.1190 3.6155
   1.0811 3.5250
   1.0356 3.4380
   0.9828 3.3552
   0.9231 3.2774
   0.8569 3.2049
   0.7846 3.1384
   0.7070 3.0784
   0.6244 3.0252
   0.5376 2.9794
   0.4472 2.9412
   0.3538 2.9109
   0.2582 2.8888
   0.2582 1.4941
   0.9805 1.4941
   1.0229 1.4923
   1.0649 1.4869
   1.1064 1.4780
   1.1469 1.4656
   1.1863 1.4498
   1.2242 1.4307
   1.2603 1.4085
   1.2944 1.3833
   1.3263 1.3553
   1.3556 1.3247
   1.3823 1.2917
   1.4061 1.2566
   1.4268 1.2196
   1.4443 1.1810
   1.4585 1.1410
   1.4692 1.1000
   3.0170 -6.0648
  END
 END
 RING
  LINE
   0.9543 -1.2510
   -0.9412 -1.2510
   -1.2640 -2.7441
   1.2770 -2.7441
  END
 END
 RING
  LINE
   -1.3721 -3.2441
   -1.6954 -4.7393
   1.7082 -4.7393
   1.3851 -3.2441
  END
 END
 RING
  LINE
   -0.5640 0.4941
   -0.8331 -0.7510
   0.8463 -0.7510
   0.5771 0.4941
  END
 END
 RING
  LINE
   -1.9821 -6.0652
   1.9948 -6.0652
   1.8162 -5.2393
   -1.8038 -5.2393
  END
 END
 RING
  LINE
   -2.2900 2.4863
   -2.3949 2.6591
   -2.4868 2.8391
   -2.5653 3.0254
   -2.6299 3.2169
   -2.6803 3.4127
   -2.7161 3.6116
   -2.7373 3.8126
   -2.7437 4.0146
   -2.7352 4.2166
   -2.7119 4.4174
   -2.6739 4.6159
   -2.6215 4.8111
   -2.5549 5.0020
   -2.4745 5.1874
   -2.3806 5.3664
   -2.2739 5.5381
   -2.6880 5.8174
   -2.8142 5.6146
   -2.9252 5.4030
   -3.0204 5.1839
   -3.0992 4.9584
   -3.1612 4.7277
   -3.2061 4.4930
   -3.2336 4.2557
   -3.2437 4.0170
   -3.2361 3.7782
   -3.2111 3.5407
   -3.1687 3.3056
   -3.1091 3.0742
   -3.0327 2.8479
   -2.9398 2.6278
   -2.8311 2.4150
   -2.7070 2.2109
  END
 END
 RING
  LINE
   3.2568 4.0000
   3.2548 4.1182
   3.2484 4.2362
   3.2378 4.3539
   3.2229 4.4711
   3.2037 4.5877
   3.1803 4.7035
   3.1526 4.8184
   3.1208 4.9323
   3.0849 5.0448
   3.0449 5.1560
   3.0009 5.2657
   2.9529 5.3737
   2.9011 5.4799
   2.8453 5.5841
   2.7859 5.6862
   2.7227 5.7861
   2.3047 5.5107
   2.4093 5.3380
   2.5010 5.1581
   2.5792 4.9720
   2.6436 4.7806
   2.6938 4.5850
   2.7295 4.3863
   2.7505 4.1855
   2.7567 3.9836
   2.7482 3.7819
   2.7248 3.5813
   2.6868 3.3830
   2.6344 3.1881
   2.5678 2.9974
   2.4875 2.8122
   2.3937 2.6334
   2.2871 2.4619
   2.7012 2.1826
   2.7669 2.2837
   2.8288 2.3871
   2.8867 2.4928
   2.9407 2.6006
   2.9907 2.7103
   3.0365 2.8218
   3.0781 2.9350
   3.1155 3.0496
   3.1486 3.1655
   3.1773 3.2826
   3.2017 3.4006
   3.2216 3.5195
   3.2371 3.6391
   3.2482 3.7591
   3.2547 3.8795
   3.2568 4.0000
  END
 END
 RING
  LINE
   -3.9658 1.3818
   -4.1367 1.6620
   -4.2878 1.9534
   -4.4185 2.2545
   -4.5282 2.5638
   -4.6164 2.8800
   -4.6825 3.2015
   -4.7264 3.5267
   -4.7477 3.8543
   -4.7465 4.1825
   -4.7226 4.5099
   -4.6763 4.8348
   -4.6077 5.1558
   -4.5172 5.4713
   -4.4051 5.7798
   -4.2721 6.0798
   -4.1187 6.3700
   -4.5522 6.6200
   -4.7218 6.2992
   -4.8688 5.9676
   -4.9927 5.6266
   -5.0928 5.2778
   -5.1686 4.9230
   -5.2198 4.5638
   -5.2462 4.2020
   -5.2475 3.8392
   -5.2239 3.4771
   -5.1754 3.1176
   -5.1022 2.7622
   -5.0047 2.4128
   -4.8834 2.0708
   -4.7389 1.7381
   -4.5717 1.4160
   -4.3828 1.1063
  END
 END
END
""",
    "military_airfield": """VERSION 1.0
BOX -7.5000 -7.5000 7.5000 7.5000
POLYGON
 RING
  LINE
   -0.6818 6.8182
   -2.7273 6.8182
   -2.8835 6.8316
   -3.0114 6.8687
   -3.1108 6.9247
   -3.1818 6.9950
   -3.2244 7.0747
   -3.2386 7.1591
   -3.2244 7.2435
   -3.1818 7.3232
   -3.1108 7.3935
   -3.0114 7.4495
   -2.8835 7.4866
   -2.7273 7.5000
   2.7272 7.5000
   2.8834 7.4866
   3.0113 7.4495
   3.1107 7.3935
   3.1817 7.3232
   3.2243 7.2435
   3.2385 7.1591
   3.2243 7.0747
   3.1817 6.9950
   3.1107 6.9247
   3.0113 6.8687
   2.8834 6.8316
   2.7272 6.8182
   0.6818 6.8182
   0.6979 6.8058
   0.7424 6.7681
   0.8096 6.7046
   0.8939 6.6145
   0.9896 6.4973
   1.0909 6.3523
   1.1922 6.1789
   1.2879 5.9765
   1.3722 5.7444
   1.4394 5.4819
   1.4839 5.1886
   1.5000 4.8637
   1.5000 3.5000
   7.5000 3.5000
   7.5000 1.5000
   1.5000 -0.5000
   1.0000 -5.5000
   3.5000 -6.8182
   3.5000 -7.5000
   -3.5000 -7.5000
   -3.5000 -6.8182
   -1.0000 -5.5000
   -1.5000 -0.5000
   -7.5000 1.5000
   -7.5000 3.5000
   -1.5000 3.5000
   -1.5000 4.8636
   -1.4839 5.1885
   -1.4394 5.4819
   -1.3722 5.7443
   -1.2879 5.9764
   -1.1922 6.1789
   -1.0909 6.3523
   -0.9896 6.4973
   -0.8939 6.6145
   -0.8096 6.7046
   -0.7424 6.7681
   -0.6979 6.8058
   -0.6818 6.8182
  END
 END
END
""",
    "military_base": """VERSION 1.0
BOX -12.0000 -12.0000 12.0000 12.0000
POLYGON
 RING
  LINE
   0.0000 10.0000
   10.0000 3.0000
   6.0000 -9.0000
   -6.0000 -9.0000
   -10.0000 3.0000
  END
 END
END
""",
    "naval_base": """VERSION 1.0
BOX -12.0000 -12.0000 12.0000 12.0000
STRING
 ARC 0.0000 7.0000 2.3000 360 0 C
END
STRING
 LINE
  0.0000 4.7000
  0.0000 -7.0000
 END
END
STRING
 LINE
  -6.0000 -1.0000
  6.0000 -1.0000
 END
END
STRING
 LINE
  -8.0000 -3.0000
  -7.8463 -4.5607
  -7.3910 -6.0615
  -6.6518 -7.4446
  -5.6569 -8.6569
  -4.4446 -9.6518
  -3.0615 -10.3910
  -1.5607 -10.8463
  0.0000 -11.0000
  1.5607 -10.8463
  3.0615 -10.3910
  4.4446 -9.6518
  5.6569 -8.6569
  6.6518 -7.4446
  7.3910 -6.0615
  7.8463 -4.5607
  8.0000 -3.0000
 END
END
""",
    "power_plant": """VERSION 1.0
BOX -7.5000 -7.5000 7.5000 7.5000
POLYGON
 RING
  LINE
   6.5000 6.5000
   6.5000 -5.5000
   -6.5000 -5.5000
   -6.5000 -1.2200
   -6.4984 -1.1847
   -6.4943 -1.1498
   -6.4878 -1.1155
   -6.4789 -1.0818
   -6.4678 -1.0489
   -6.4544 -1.0169
   -6.4388 -0.9859
   -6.4211 -0.9560
   -6.4013 -0.9273
   -6.3795 -0.9001
   -6.3557 -0.8742
   -6.3300 -0.8500
   -3.3300 2.3700
   -3.2760 2.4114
   -3.2184 2.4443
   -3.1579 2.4689
   -3.0954 2.4853
   -3.0317 2.4934
   -2.9678 2.4933
   -2.9043 2.4852
   -2.8422 2.4689
   -2.7824 2.4447
   -2.7255 2.4125
   -2.6726 2.3723
   -2.6244 2.3244
   -2.6049 2.3008
   -2.5869 2.2761
   -2.5706 2.2505
   -2.5558 2.2240
   -2.5427 2.1967
   -2.5313 2.1687
   -2.5217 2.1400
   -2.5137 2.1108
   -2.5076 2.0811
   -2.5032 2.0511
   -2.5007 2.0207
   -2.5000 1.9900
   -2.5000 -1.0100
   0.6600 2.3600
   0.7129 2.4028
   0.7696 2.4373
   0.8294 2.4635
   0.8915 2.4816
   0.9549 2.4914
   1.0188 2.4931
   1.0825 2.4866
   1.1449 2.4720
   1.2054 2.4494
   1.2631 2.4187
   1.3171 2.3800
   1.3666 2.3334
   1.3874 2.3095
   1.4066 2.2844
   1.4241 2.2583
   1.4399 2.2312
   1.4539 2.2032
   1.4661 2.1745
   1.4765 2.1450
   1.4851 2.1149
   1.4917 2.0842
   1.4964 2.0532
   1.4992 2.0217
   1.5000 1.9900
   1.5000 -3.5000
   4.5000 -3.5000
   4.5000 6.5000
   6.5000 6.5000
  END
 END
END
""",
    "substation": """VERSION 1.0
BOX -12.0000 -12.0000 12.0000 12.0000
STRING
 LINE
  0.0000 11.0000
  11.0000 0.0000
  0.0000 -11.0000
  -11.0000 0.0000
  0.0000 11.0000
 END
END
POLYGON
 RING
  LINE
   1.0000 8.0000
   -5.0000 -1.0000
   -1.0000 -1.0000
   -2.5000 -8.0000
   5.0000 2.0000
   0.5000 2.0000
  END
 END
END
""",
    "training_area": """VERSION 1.0
BOX -12.0000 -12.0000 12.0000 12.0000
STRING
 ARC 0.0000 0.0000 9.0000 360 0 C
END
STRING
 ARC 0.0000 0.0000 5.0000 360 0 C
END
POLYGON
 RING
  ARC 0.0000 0.0000 1.1000 360 0 C
 END
END
STRING
 LINE
  0.0000 11.0000
  0.0000 7.0000
 END
END
STRING
 LINE
  0.0000 -7.0000
  0.0000 -11.0000
 END
END
STRING
 LINE
  -11.0000 0.0000
  -7.0000 0.0000
 END
END
STRING
 LINE
  7.0000 0.0000
  11.0000 0.0000
 END
END
""",
}
# --- end embedded GRASS symbols ---


def _build_overpass_query(rules, bbox, timeout_s):
    south, west, north, east = bbox
    bbox_str = f"{south},{west},{north},{east}"
    clauses = []
    for rule in rules:
        for elem_type in ("node", "way", "relation"):
            clauses.append(f'{elem_type}["{rule["tag_key"]}"="{rule["tag_value"]}"]({bbox_str});')
    body = "\n  ".join(clauses)
    return f"[out:json][timeout:{timeout_s}];\n(\n  {body}\n);\nout center tags;\n"


def _fetch_overpass(endpoint, query, timeout_s):
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    req = urllib.request.Request(
        endpoint, data=data, headers={"User-Agent": "d.osm/0.1 (GRASS GIS addon)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s + 30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        gs.fatal(_("Overpass request failed: {}").format(exc))


def _classify(tags, rules_by_tag):
    for (key, value), rule in rules_by_tag.items():
        if tags.get(key) == value:
            return rule
    return None


def _elements_to_geojson_features(elements, rules_by_tag):
    features = []
    for element in elements:
        tags = element.get("tags", {})
        rule = _classify(tags, rules_by_tag)
        if rule is None:
            continue
        if "lat" in element and "lon" in element:
            lat, lon = element["lat"], element["lon"]
        elif element.get("center"):
            lat, lon = element["center"]["lat"], element["center"]["lon"]
        else:
            continue
        elem_type = element.get("type", "node")
        elem_id = element.get("id")
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "symbol": rule["symbol"],
                "label": rule["label"],
                "name": tags.get("name", ""),
                "osm_type": elem_type,
                "osm_id": elem_id,
            },
        })
    return features


def install_symbols(gisbase, symbol_names):
    """Copy the needed pre-baked symbols into $GISBASE/etc/symbol/osm/.
    No conversion happens here -- _SYMBOLS is static text embedded above."""
    dest_root = os.path.join(gisbase, "etc", "symbol", GRASS_SYMBOL_GROUP)
    os.makedirs(dest_root, exist_ok=True)
    for name in symbol_names:
        content = _SYMBOLS.get(name)
        if content is None:
            continue
        dest = os.path.join(dest_root, name)
        if not os.path.exists(dest) or open(dest).read() != content:
            with open(dest, "w") as fh:
                fh.write(content)


def main():
    options, flags = gs.parser()

    requested_types = options["types"].split(",") if options["types"] else None
    rules = [r for r in RULES if requested_types is None or r["symbol"] in requested_types]
    rules_by_tag = {(r["tag_key"], r["tag_value"]): r for r in rules}

    region = gs.parse_command("g.region", flags="bg")
    bbox = (
        float(region["ll_s"]), float(region["ll_w"]),
        float(region["ll_n"]), float(region["ll_e"]),
    )

    query = _build_overpass_query(rules, bbox, int(options["timeout"]))
    payload = _fetch_overpass(options["endpoint"], query, int(options["timeout"]))
    features = _elements_to_geojson_features(payload.get("elements", []), rules_by_tag)

    output = options["output"]
    if not features:
        gs.warning(_("Overpass returned no matching features for the current region"))
        gs.run_command("v.edit", map=output, tool="create", overwrite=True)
        return

    geojson = {"type": "FeatureCollection", "features": features}
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".geojson", delete=False, encoding="utf-8"
    ) as fh:
        json.dump(geojson, fh)
        geojson_path = fh.name

    try:
        gs.run_command(
            "v.in.ogr", input=geojson_path, output=output, overwrite=True,
        )
    finally:
        os.unlink(geojson_path)

    if options["format"] == "attributes":
        gs.run_command("v.db.select", map=output)
        return

    present_symbols = sorted({f["properties"]["symbol"] for f in features})
    gisbase = os.environ["GISBASE"]
    install_symbols(gisbase, present_symbols)

    size = options["size"]
    for i, symbol in enumerate(present_symbols):
        if i > 0:
            # File-based rendering overwrites GRASS_RENDER_FILE on each
            # d.* call unless told to composite onto existing content.
            os.environ["GRASS_RENDER_FILE_READ"] = "TRUE"
        gs.run_command(
            "d.vect",
            map=output,
            where=f"symbol = '{symbol}'",
            icon=f"{GRASS_SYMBOL_GROUP}/{symbol}",
            size=size,
        )


if __name__ == "__main__":
    main()
