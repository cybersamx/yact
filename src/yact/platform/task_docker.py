from pathlib import Path

from docker import DockerClient, from_env
from docker.errors import DockerException, ImageNotFound, NotFound
from docker.models.containers import Container


class TaskContainerException(Exception):
    pass


class TaskContainer:
    """
    TaskContainer is a container (wrapper) that runs a shell command.
    """

    image_name: str
    container_workdir: str
    client: DockerClient = None
    container: Container = None

    def __init__(self, image_name='alpine:latest', container_workdir='/home/yact'):
        try:
            self.image_name = image_name
            self.container_workdir = container_workdir

            self.client = from_env()
            self.client.images.pull(self.image_name)
        except DockerException:
            raise TaskContainerException('Looks like docker engine is not found. Please launch docker engine and try again.')
        except Exception as err:
            raise TaskContainerException(err)


    def __enter__(self):
        try:
            print('Starting a container.')
            self.container = self.client.containers.run(
                self.image_name,
                remove=True,
                stdin_open=True,
                tty=True,
                detach=True,
                volumes={
                    str(Path.cwd()): {
                        'bind': self.container_workdir,
                        'mode': 'rw',
                    },
                },
            )
            print(f'Container {self.container.name} is now running.')
        except ImageNotFound:
            raise TaskContainerException(f'Image {self.image_name} is not found. Please pull the image first.')

        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


    def close(self):
        # Usually a graceful shutdown offered by container.stop() is preferred, but in docker that
        # grace period is 10s too long. So we use container.kill() to send a SIGKILL to immediately
        # shut down the process, which is a bash shell, running in docker.

        if self.container:
            self.container.kill()   # No need to run remove if we kill.


    def exec_cmd(self, cmd) -> str:
        result = self.container.exec_run(cmd, stream=False, demux=False)
        return result.output.decode('utf-8')

