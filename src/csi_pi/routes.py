from starlette.routing import Route
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from src.csi_pi.controller import Controller


def get_routes(controller: Controller):
    return [
        # Static Routes
        Route("/", controller.index),
        Route("/annotate", controller.annotate_index),
        Mount('/css', app=StaticFiles(directory='src/csi_pi/resources/css'), name="css"),
        Mount('/js', app=StaticFiles(directory='src/csi_pi/resources/js'), name="js"),

        # Perform Actions
        Route("/data", controller.get_data_as_zip),
        Route("/reset", controller.reset, methods=['POST']),
        Route("/annotation", controller.new_annotation, methods=['POST']),
        Route("/enable_csi", controller.enable_csi, methods=['POST']),
        Route("/disable_csi", controller.disable_csi, methods=['POST']),

        # API
        Route("/server-stats", controller.get_server_stats),
        Route("/annotation-metrics", controller.get_annotation_metrics),
        Route("/device-metrics", controller.get_device_metrics),
        Route("/notes", controller.set_notes, methods=['POST']),
    ]
