from project.app import app

from project.artist_app import get_new_image_from_picks
import json

mocked_values = [
    {
        'id': '13',
        'name': 'gnarsito.jpg',
        'path': 'gnarsito'
    },
    {
        'id': '24',
        'name': 'me.jpg',
        'path': 'me'
    }
]


def test_get_new_image_generated_from_picks():
    """Receive two images ids and return new image generated with the model"""
    # 1. recibir dos objetos (mockear request al oci para devolver dos objetos).
    # 2. procesar los dos objetos en el modelo de pytorch
    # 3. verificar que una nueva imagen es creada y el metodo de upload es llamado con el parametro siendo la nueva imagen.
    new_image = get_new_image_from_picks('13', '24')
    assert new_image.data == 200
    assert json.loads(new_image.data.content) == {'id': '33', 'name': 'gnarsito_me.jpg', 'path': 'artistu'}
