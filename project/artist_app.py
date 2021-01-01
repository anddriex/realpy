import oci

from project.app import app
from flask import current_app, request, jsonify
from project.oci.configuration import oci_config

# with app.test_request_context('/'):
#     print(request.method)
#     print(request.path)


@app.route('/generate_new_image_from_picks/<int:structure_id>/<int:style_id>')
def get_new_image_from_picks(structure_id, style_id):
    response = [
        {
            'id': style_id,
            'name': 'gnarsito.jpg',
            'path': 'gnarsito'
        },
        {
            'id': structure_id,
            'name': 'me.jpg',
            'path': 'me'
        }
    ]
    object_storage = oci.object_storage.ObjectStorageClient(oci_config)
    namespace = object_storage.get_namespace().data
    gnarsito = object_storage.get_object(
        namespace,
        'artist-bucket',
        'gnarsito.jpg'
    )

    print(gnarsito)
    amdss

    with app.app_context():
        return jsonify(_generate_image_with_model(response))


def _generate_image_with_model(response):
    return {
        'id': '33',
        'name': 'gnarsito_me.jpg',
        'path': 'artistu'
    }
