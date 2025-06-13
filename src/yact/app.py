from yact.platform.task_docker import TaskContainer

def main():
    with TaskContainer() as container:
        print(container.exec_cmd('ls -la /home/yact'))


if __name__ == "__main__":
    main()
