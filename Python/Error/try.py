class SwitchClientException(Exception):
    pass


def try_error():
    try:
        print(f"start get error")
        raise SwitchClientException
    except SwitchClientException as e:
        print(f"get SwitchClientException {e}")
    except ValueError as e:
        print(f"get value error {e}")
    except Exception as e:
        print(f"get normal error {e}")


if __name__ == "__main__":
    try_error()
