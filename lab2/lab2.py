import sys

from PyQt6.QtCore import QObject, Qt, QRegularExpression, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import QApplication, QFormLayout, QGroupBox, QLabel, QLineEdit, QMainWindow, QVBoxLayout, QWidget

class CurrencyModel(QObject):
    amounts_changed = pyqtSignal(dict)
    rates_changed = pyqtSignal(dict)

    def __init__(self, usd_rate=80.0, eur_rate=100.0, parent=None):
        super().__init__(parent)
        self._rates = {"RUB": 1.0, "USD": usd_rate, "EUR": eur_rate}
        self._rub = 0.0

    def amounts(self):
        return {code: self._rub / rate for code, rate in self._rates.items()}

    def rates(self):
        return {code: rate for code, rate in self._rates.items() if code != "RUB"}

    @pyqtSlot(str, float)
    def set_amount(self, code, value):
        self._rub = value * self._rates[code]
        self.amounts_changed.emit(self.amounts())

    @pyqtSlot(str, float)
    def set_rate(self, code, value):
        if value > 0:
            self._rates[code] = value
            self.amounts_changed.emit(self.amounts())
        self.rates_changed.emit(self.rates())


class NumberEdit(QLineEdit):
    value_edited = pyqtSignal(str, float)

    def __init__(self, code, decimals=2, parent=None):
        super().__init__(parent)
        self.code = code
        self._decimals = decimals
        self._value = 0.0
        self._editing = False

        regex = QRegularExpression(rf"^\d{{0,12}}([.,]\d{{0,{decimals}}})?$")
        self.setValidator(QRegularExpressionValidator(regex, self))
        self.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.textEdited.connect(self._on_text_edited)
        self.editingFinished.connect(self._reformat)

    @pyqtSlot(str)
    def _on_text_edited(self, text):
        text = text.replace(",", ".")
        value = float(text) if text.strip(".") else 0.0
        self._editing = True
        try:
            self.value_edited.emit(self.code, value)
        finally:
            self._editing = False

    def set_value(self, value):
        self._value = value
        if not self._editing:
            self.setText(self._format(value))

    @pyqtSlot()
    def _reformat(self):
        self.setText(self._format(self._value))

    def _format(self, value):
        return f"{value:.{self._decimals}f}"


class MainWindow(QMainWindow):
    CURRENCIES = {"RUB": "Рубли, ₽", "USD": "Доллары, $", "EUR": "Евро, €"}

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setWindowTitle("Конвертер валют")

        self.amount_edits = {}
        amount_box = QGroupBox("Сумма")
        amount_form = QFormLayout(amount_box)
        for code, title in self.CURRENCIES.items():
            edit = NumberEdit(code, decimals=2)
            edit.value_edited.connect(model.set_amount)
            amount_form.addRow(title, edit)
            self.amount_edits[code] = edit

        self.rate_edits = {}
        rates_box = QGroupBox("Курс (рублей за 1 единицу)")
        rates_form = QFormLayout(rates_box)
        for code, title in (("USD", "1 $ ="), ("EUR", "1 € =")):
            edit = NumberEdit(code, decimals=4)
            edit.value_edited.connect(model.set_rate)
            rates_form.addRow(title, edit)
            self.rate_edits[code] = edit

        self.cross_label = QLabel()

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(amount_box)
        layout.addWidget(rates_box)
        layout.addWidget(self.cross_label)
        self.setCentralWidget(central)

        model.amounts_changed.connect(self.show_amounts)
        model.rates_changed.connect(self.show_rates)
        model.rates_changed.connect(self.show_cross_rate)

        self.show_amounts(model.amounts())
        self.show_rates(model.rates())
        self.show_cross_rate(model.rates())

    @pyqtSlot(dict)
    def show_amounts(self, amounts):
        for code, value in amounts.items():
            self.amount_edits[code].set_value(value)

    @pyqtSlot(dict)
    def show_rates(self, rates):
        for code, value in rates.items():
            self.rate_edits[code].set_value(value)

    @pyqtSlot(dict)
    def show_cross_rate(self, rates):
        self.cross_label.setText(f"Кросс-курс: 1 € = {rates['EUR'] / rates['USD']:.4f} $")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    model = CurrencyModel(usd_rate=80.0, eur_rate=100.0)
    model.set_amount("USD", 100.0)

    window = MainWindow(model)
    window.show()
    sys.exit(app.exec())
