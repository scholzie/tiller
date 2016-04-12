import tillerlib.tillerlib as tl
from tillerlib.resources.tiller import TillerResource

import logging

class TerraformResource(TillerResource):
    """docstring for TerraformResource"""
    def __init__(self, name, path, *args, **kwargs):
        logging.debug("[Tiller:TerraformResource:__init__]")
        super(TerraformResource, self).__init__(name, path, *args, **kwargs)

    def plan(self):
        # TODO: implement TerraformResource.plan()
        pass

    def build(self):
        # TODO: implement TerraformResource.build()
        pass

    def show(self):
        # TODO: implement TerraformResource.show()
        pass

    def destroy(self):
        # TODO: implement TerraformResource.destroy()
        pass
