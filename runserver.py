from haldane import make_application


if __name__ == '__main__':
    app = make_application()
    app.run(debug=app.config['DEBUG'], host=app.config['LISTEN_INTERFACE'], port=app.config['PORT'])
