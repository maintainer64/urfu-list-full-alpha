import argparse


def parser_input_dto():
    parser = argparse.ArgumentParser(description="Управление работой приложения заявок.")
    parser.add_argument(
        "command", choices=["parse", "upload"],
        help="Команда: upload (загрузить вручную), parse (собрать новый csv файл)"
    )
    args = parser.parse_args()
    return args.command


if __name__ == "__main__":
    from urfu_list_priority import job

    {
        "upload": job,
    }[parser_input_dto()]()
