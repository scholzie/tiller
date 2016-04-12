import tillerlib.tillerlib as tl
from tillerlib.resources.tiller import TillerResource

import logging

class TerraformResource(TillerResource):
    """docstring for TerraformResource"""
    def __init__(self, name, path, *args, **kwargs):
        logging.debug("[Tiller:TerraformResource:__init__]")
        super(TerraformResource, self).__init__(name, path, *args, **kwargs)

    def plan(self):
        pass

    def build(self):
        pass

    def show(self):
        pass

    def destroy(self):
        pass
