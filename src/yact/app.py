from yact.platform.task_docker import TaskContainer, run_container


def main():
    with run_container(image_name='python:3.13.5-alpine', host_workdir='.yact-testdir') as container:
        print(container.exec_cmd('ls -la'))
        print(container.exec_cmd('python --version'))
        print(container.exec_cmd('pwd'))


if __name__ == "__main__":
    main()
