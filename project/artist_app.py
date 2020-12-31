from project.app import app

@app.route('/generate_new_image_from_picks/<int:structure_id>/<int:style_id>')
def generate_new_image_from_picks(structure_id, style_id):
    response = [
        {
            'name': 'gnarsito.jpg',
            'content': b'gnarsito'
        },
        {
            'name': 'me.jpg',
            'content': b'me'
        }
    ]

    return jsonify({})