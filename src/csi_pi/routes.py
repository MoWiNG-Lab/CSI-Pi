from starlette.routing import Route
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from src.csi_pi.controller import Controller


def get_routes(controller: Controller):
    return [
        # Static Routes
        Route("/", controller.index),
        Mount('/js', app=StaticFiles(directory='src/csi_pi/resources/js'), name="js"),

        # Perform Actions
        Route("/data", controller.get_data_as_zip),
        Route("/annotation", controller.new_annotation, methods=['POST']),
        Route("/enable_csi", controller.enable_csi, methods=['POST']),
        Route("/disable_csi", controller.disable_csi, methods=['POST']),

        # API
        Route("/server-stats", controller.get_server_stats),
        Route("/data-directory", controller.get_data_directory),
        Route("/annotation-metrics", controller.get_annotation_metrics),
        Route("/device-list", controller.get_device_list),
        Route("/device-metrics", controller.get_device_metrics),
        Route("/experiment-name", controller.get_experiment_name),
        Route("/experiment-name", controller.set_experiment_name, methods=['POST']),
        Route("/notes", controller.get_notes),
        Route("/notes", controller.set_notes, methods=['POST']),
    ]