from starlette.routing import Route

from src.csi_pi.controller import Controller


def get_routes(controller: Controller):
    return [
        Route("/", controller.index),
        Route("/annotation", controller.new_annotation, methods=['POST']),
        Route("/data-directory", controller.get_data_directory),
        Route("/data", controller.get_data_as_zip),
        Route("/power_up", controller.power_up, methods=['POST']),
        Route("/power_down", controller.power_down, methods=['POST']),
    ]