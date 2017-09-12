#
# eChronos Real-Time Operating System
# Copyright (c) 2017, Commonwealth Scientific and Industrial Research
# Organisation (CSIRO) ABN 41 687 119 230.
#
# All rights reserved. CSIRO is willing to grant you a licence to the eChronos
# real-time operating system under the terms of the CSIRO_BSD_MIT license. See
# the file "LICENSE_CSIRO_BSD_MIT.txt" for details.
#
# @TAG(CSIRO_BSD_MIT)
#

from prj import Module


class AcamarConfigDemoModule(Module):
    xml_schema = """<schema></schema>"""

    files = [
        {'input': 'acamar-config-demo.c', 'render': True, 'type': 'c'},
    ]

module = AcamarConfigDemoModule()  # pylint: disable=invalid-name
