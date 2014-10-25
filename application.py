from haldane import make_application

application = make_application()

if __name__ == '__main__':
    application.run(
        debug=application.config['DEBUG'],
        host=application.config['LISTEN_INTERFACE'],
        port=application.config['PORT'])
