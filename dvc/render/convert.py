import json
from typing import Dict, List, Union

from dvc_render import ImageRenderer, VegaRenderer

from dvc.render import REVISION_FIELD, REVISIONS_KEY, SRC_FIELD, TYPE_KEY
from dvc.render.image_converter import ImageConverter
from dvc.render.vega_converter import VegaConverter

CONVERTERS = {
    VegaRenderer.TYPE: VegaConverter,
    ImageRenderer.TYPE: ImageConverter,
}


def to_datapoints(renderer_class, data: Dict, props: Dict):
    converter: Union[VegaConverter, ImageConverter] = CONVERTERS[
        renderer_class.TYPE
    ](props)

    datapoints = []
    for revision, rev_data in data.items():
        for filename, file_data in rev_data.get("data", {}).items():
            if "data" in file_data:
                processed, final_props = converter.convert(
                    revision, filename, file_data.get("data")
                )
                datapoints.extend(processed)
    return datapoints, final_props


def to_json(renderer) -> List[Dict]:
    if renderer.TYPE == "vega":
        # TODO: Adapt to #7367
        return [
            {
                TYPE_KEY: renderer.TYPE,
                REVISIONS_KEY: sorted(
                    {
                        datapoint.get(REVISION_FIELD)
                        for datapoint in renderer.datapoints
                    }
                ),
                "content": json.loads(renderer.partial_html()),
            }
        ]
    if renderer.TYPE == "image":
        return [
            {
                TYPE_KEY: renderer.TYPE,
                REVISIONS_KEY: datapoint.get(REVISION_FIELD),
                "url": datapoint.get(SRC_FIELD),
            }
            for datapoint in renderer.datapoints
        ]
    raise ValueError(f"Invalid renderer: {renderer.TYPE}")
