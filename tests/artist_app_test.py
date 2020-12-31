from project.app import app
from project.artist_app import generate_new_image_from_picks


mocked_values = [
    {
        'name': 'gnarsito.jpg',
        'content': b'gnarsito'
    },
    {
        'name': 'me.jpg',
        'content': b'me'
    }
]

def test_get_new_image_generated_from_picks():
    """Receive two images ids and return new image generated with the model"""
    # 1. recibir dos objetos (mockear request al oci para devolver dos objetos). 
    # 2. procesar los dos objetos en el modelo de pytorch
    # 3. verificar que una nueva imagen es creada y el metodo de upload es llamado con el parametro siendo la nueva imagen.
    new_image = generate_new_image_from_picks('13', '24')
    assert new_image.status_code == 200
    assert new_image.data == {name: 'gnarsito_me.jpg', content: 'artistu'}
