import os

from hello_settings import ENV_DICT, BACKEND_PATH


if __name__ == '__main__':
    os.environ['AWS_ACCESS_KEY_ID'] = ENV_DICT['AWS_ACCESS_KEY_ID']
    os.environ['AWS_SECRET_ACCESS_KEY'] = ENV_DICT['AWS_SECRET_ACCESS_KEY']
    print ENV_DICT['AWS_ACCESS_KEY_ID']
    spawn_server_yml = os.path.join(BACKEND_PATH, 'devops/spawn_server.yml')
    os.system('ansible-playbook {}'.format(spawn_server_yml))
