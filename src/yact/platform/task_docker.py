from contextlib import contextmanager
from pathlib import Path

from docker import DockerClient, from_env
from docker.errors import DockerException, ImageNotFound
from docker.models.containers import Container


class TaskContainerException(Exception):
    pass


class TaskContainer:
    """
    TaskContainer is a container (wrapper) that runs a shell command.
    Don't call constructor directly, call function run_container with a with block.
    """

    image_name: str
    container_workdir: str
    host_workdir: str

    client: DockerClient | None = None
    container: Container | None = None

    def __init__(self, **kwargs):
        try:
            self.image_name = kwargs.pop('image_name')
            self.container_workdir = kwargs.pop('container_workdir')
            self.host_workdir = kwargs.pop('host_workdir')

            self.client = from_env()
            print(f'Pulling image {self.image_name}')
            self.client.images.pull(self.image_name)
            print(f'Pulled image {self.image_name}')
        except DockerException:
            raise TaskContainerException('Looks like docker engine is not found. Please launch docker engine and try again.')
        except Exception as err:
            raise TaskContainerException(err)


    def run(self):
        try:
            self.container = self.client.containers.run(
                self.image_name,
                remove=True,
                stdin_open=True,
                tty=True,
                detach=True,
                volumes={
                    self.host_workdir: {
                        'bind': self.container_workdir,
                        'mode': 'rw',
                    },
                },
            )
            print(f'Container {self.container.name} is now running.')
        except ImageNotFound:
            raise TaskContainerException(f'Image {self.image_name} is not found. Please pull the image first.')

        return self


    def close(self):
        # Usually a graceful shutdown offered by container.stop() is preferred. Since we are running
        # the docker container as an interactive tty, the underlying shell doesn't terminate immediately
        # when the signal is received. Consequently, docker enforces a grace period of 10s to shut down
        # the process - that's too long. So we use container.kill() to send a SIGKILL to immediately
        # shut down the process.

        if self.container:
            print(f'Closing container {self.container.name}')
            self.container.kill()   # No need to run remove if we kill.


    def exec_cmd(self, cmd) -> str:
        # Always change the directory to the container workdir.
        cmd = f'sh -c "cd {self.container_workdir}; {cmd}"'

        result = self.container.exec_run(cmd, stream=False, demux=False)
        return result.output.decode('utf-8')


@contextmanager
def run_container(
    image_name='alpine:latest',
    container_workdir='/home/yact',
    host_workdir=str(Path.cwd()),
):
    host_workdir_path = Path(host_workdir)
    if not host_workdir_path.is_relative_to(Path.cwd()):
        # Docker only accepts a host mount path as an absolute path.
        # Convert a relative path (to the program workdir).
        host_workdir = Path.cwd() / host_workdir_path

    kwargs = {
        'image_name': image_name,
        'container_workdir': container_workdir,
        'host_workdir': host_workdir,
    }

    tc = TaskContainer(**kwargs)
    tc.run()
    try:
        yield tc
    finally:
        tc.close()
