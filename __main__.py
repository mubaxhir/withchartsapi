import connexion


def main():
    app = connexion.FlaskApp(__name__, specification_dir='openapi/')
    app.add_api('openapi.yaml',validate_responses=True)
    app.run(port=8080,debug=True)

if __name__ == '__main__':
    main()
