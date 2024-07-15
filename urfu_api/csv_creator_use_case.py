import copy
import csv

from .dto import UrfuApiModel


class CsvCreatorUseCase:
    def __init__(self):
        self.themes = {
            "3.csv": {}
        }

    @staticmethod
    def save_csv(model: UrfuApiModel, filename: str):
        headers = (
            "Рег.№",
            "СНИЛС",
            "Состояние",
            "Вид конкурса",
            "Оригинал док. об образовании",
            "Приоритет",
            "Направление (специальность)",
            "Образовательная программа (институт/филиал)",
            "Форма обучения",
            "Бюджетная (контрактная) основа",
            "Вступительные испытания по предметам",
            "Индивидуальные достижения",
            "Сумма конкурсных баллов",
        )
        rows = []
        for page in model.items:
            for item in page.applications:
                row = (
                    page.regnum,
                    page.snils,
                    item.status,
                    item.compensation,
                    "Да" if item.edu_doc_original else "Нет",
                    item.priority,
                    item.speciality,
                    item.program,
                    item.familirization,
                    item.compensation,
                    ";".join(
                        [f"{field}: {value.mark} ({value.case})" for field, value in item.marks.items()]),
                    item.achievs,
                    item.total_mark,
                )
                rows.append(row)
        with open(filename, mode='w') as employee_file:
            employee_writer = csv.writer(employee_file)
            employee_writer.writerow(headers)
            employee_writer.writerows(rows)

    @staticmethod
    def filter_managers(themes: dict, model: UrfuApiModel) -> UrfuApiModel:
        new_items = []
        for item in model.items:
            new_applications = [
                x for x in item.applications
                if x.speciality in themes or len(themes) == 0
            ]
            if new_applications:
                item.applications = new_applications
                new_items.append(item)
        model.items = new_items
        return model

    def execute(self, model: UrfuApiModel):
        for key, value in self.themes.items():
            model_modification = copy.deepcopy(model)
            self.save_csv(self.filter_managers(themes=value, model=model_modification), filename=key)
