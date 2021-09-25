from starlette.routing import Route

from src.csi_pi.controller import Controller


def get_routes(controller: Controller):
    return [
        # Static Routes
        Route("/", controller.index),

        # Perform Actions
        Route("/data", controller.get_data_as_zip),
        Route("/annotation", controller.new_annotation, methods=['POST']),
        Route("/power_up", controller.power_up, methods=['POST']),
        Route("/power_down", controller.power_down, methods=['POST']),

        # API
        Route("/data-directory", controller.get_data_directory),
        Route("/annotation-metrics", controller.get_annotation_metrics),
        Route("/device-list", controller.get_device_list),
        Route("/device-metrics", controller.get_device_metrics),
    ]