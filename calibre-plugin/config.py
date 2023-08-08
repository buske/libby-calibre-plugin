#
# Copyright (C) 2023 github.com/ping
#
# This file is part of the OverDrive Libby Plugin by ping
# OverDrive Libby Plugin for calibre / libby-calibre-plugin
#
# See https://github.com/ping/libby-calibre-plugin for more
# information
#

from calibre import confirm_config_name
from calibre.gui2 import error_dialog, show_restart_warning
from calibre.utils.config import JSONConfig

try:
    from calibre.gui2.preferences.create_custom_column import CreateNewCustomColumn
except:  # noqa
    CreateNewCustomColumn = None

from qt.core import (
    QCheckBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QIcon,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    Qt,
)

from . import DEMO_MODE, PLUGIN_NAME, logger
from .compat import _c
from .utils import PluginColors

# noinspection PyUnreachableCode
if False:
    load_translations = _ = lambda x=None: x

load_translations()

MAX_SEARCH_LIBRARIES = 24


class PreferenceKeys:
    LIBBY_SETUP_CODE = "libby_setup_code"
    LIBBY_TOKEN = "libby_token"
    HIDE_MAGAZINES = "hide_magazines"
    HIDE_EBOOKS = "hide_ebooks"
    HIDE_BOOKS_ALREADY_IN_LIB = "hide_books_in_already_lib"
    EXCLUDE_EMPTY_BOOKS = "exclude_empty_books"
    HIDE_HOLDS_UNAVAILABLE = "hide_holds_unavailable"
    PREFER_OPEN_FORMATS = "prefer_open_formats"
    MAIN_UI_WIDTH = "main_ui_width"
    MAIN_UI_HEIGHT = "main_ui_height"
    TAG_EBOOKS = "tag_ebooks"
    TAG_MAGAZINES = "tag_magazines"
    CONFIRM_RETURNS = "confirm_returns"
    CONFIRM_CANCELLATIONS = "confirm_cancels"
    OVERDRIVELINK_INTEGRATION = "enable_overdrivelink_integration"
    MARK_UPDATED_BOOKS = "mark_updated_books"
    MAGAZINE_SUBSCRIPTIONS = "magazine_subscriptions"
    # used to toggle the default borrow btn action
    LAST_BORROW_ACTION = "last_borrow_action"
    LAST_SELECTED_TAB = "last_selected_tab"
    ALWAYS_DOWNLOAD_AS_NEW = "always_download_new"
    NETWORK_TIMEOUT = "network_timeout"
    NETWORK_RETRY = "network_retry"
    SEARCH_RESULTS_MAX = "search_results_max"
    SEARCH_LIBRARIES = "search_libraries"
    CUSTCOL_BORROWED_DATE = "custcol_borrowed_dt"
    CUSTCOL_DUE_DATE = "custcol_due_dt"


class BorrowActions:
    BORROW = "borrow"
    BORROW_AND_DOWNLOAD = "borrow_and_download"


class PreferenceTexts:
    LIBBY_SETUP_CODE = _("Libby Setup Code")
    LIBBY_SETUP_CODE_DESC = _("8-digit setup code")
    HIDE_MAGAZINES = _("Hide Magazines")
    HIDE_EBOOKS = _("Hide Ebooks")
    HIDE_BOOKS_ALREADY_IN_LIB = _("Hide titles already in library")
    EXCLUDE_EMPTY_BOOKS = _("Exclude empty books when hiding titles already in library")
    HIDE_HOLDS_UNAVAILABLE = _("Hide unavailable holds")
    PREFER_OPEN_FORMATS = _("Prefer Open Formats")
    TAG_EBOOKS = _("Tag downloaded ebooks with")
    TAG_EBOOKS_PLACEHOLDER = _("Example: library,books")
    TAG_MAGAZINES = _("Tag downloaded magazines with")
    TAG_MAGAZINES_PLACEHOLDER = _("Example: library,magazines")
    CONFIRM_RETURNS = _("Always confirm returns")
    CONFIRM_CANCELLATIONS = _("Always confirm holds cancellation")
    OVERDRIVELINK_INTEGRATION = _("Enable OverDrive Link Plugin integration")
    MARK_UPDATED_BOOKS = _("Mark updated books")
    ALWAYS_DOWNLOAD_AS_NEW = _("Always download as a new book")
    NETWORK_TIMEOUT = _("Connection timeout")
    NETWORK_RETRY = _c("Retry attempts")
    SEARCH_RESULTS_MAX = _("Maximum search results")
    SEARCH_LIBRARIES = _("Library Keys (comma-separated, max: {n})").format(
        n=MAX_SEARCH_LIBRARIES
    )
    CUSTCOL_BORROWED_DATE = _("Custom column for Borrowed Date")
    CUSTCOL_DUE_DATE = _("Custom column for Due Date")


PREFS = JSONConfig(f"plugins/{PLUGIN_NAME}")

PREFS.defaults[PreferenceKeys.LIBBY_SETUP_CODE] = ""
PREFS.defaults[PreferenceKeys.LIBBY_TOKEN] = ""
PREFS.defaults[PreferenceKeys.HIDE_MAGAZINES] = False
PREFS.defaults[PreferenceKeys.HIDE_EBOOKS] = False
PREFS.defaults[PreferenceKeys.HIDE_BOOKS_ALREADY_IN_LIB] = False
PREFS.defaults[PreferenceKeys.EXCLUDE_EMPTY_BOOKS] = True
PREFS.defaults[PreferenceKeys.HIDE_HOLDS_UNAVAILABLE] = True
PREFS.defaults[PreferenceKeys.PREFER_OPEN_FORMATS] = True
PREFS.defaults[PreferenceKeys.TAG_EBOOKS] = ""
PREFS.defaults[PreferenceKeys.TAG_MAGAZINES] = ""
PREFS.defaults[confirm_config_name(PreferenceKeys.CONFIRM_RETURNS)] = True
PREFS.defaults[confirm_config_name(PreferenceKeys.CONFIRM_CANCELLATIONS)] = True
PREFS.defaults[PreferenceKeys.OVERDRIVELINK_INTEGRATION] = True
PREFS.defaults[PreferenceKeys.MARK_UPDATED_BOOKS] = True
PREFS.defaults[PreferenceKeys.ALWAYS_DOWNLOAD_AS_NEW] = False
PREFS.defaults[PreferenceKeys.NETWORK_TIMEOUT] = 30
PREFS.defaults[PreferenceKeys.NETWORK_RETRY] = 1
PREFS.defaults[PreferenceKeys.SEARCH_RESULTS_MAX] = 20
PREFS.defaults[PreferenceKeys.SEARCH_LIBRARIES] = []
PREFS.defaults[PreferenceKeys.CUSTCOL_BORROWED_DATE] = ""
PREFS.defaults[PreferenceKeys.CUSTCOL_DUE_DATE] = ""
PREFS.defaults[PreferenceKeys.MAIN_UI_WIDTH] = 0
PREFS.defaults[PreferenceKeys.MAIN_UI_HEIGHT] = 0
PREFS.defaults[PreferenceKeys.MAGAZINE_SUBSCRIPTIONS] = []
PREFS.defaults[PreferenceKeys.LAST_BORROW_ACTION] = BorrowActions.BORROW
PREFS.defaults[PreferenceKeys.LAST_SELECTED_TAB] = 0


class ConfigWidget(QWidget):
    def __init__(self, plugin_action):
        super().__init__()
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.gui = plugin_action.gui
        self.db = self.gui.current_db.new_api
        # Setup Status
        is_configured = bool(PREFS[PreferenceKeys.LIBBY_TOKEN])
        if DEMO_MODE:
            is_configured = False
        self.custom_column_creator = (
            CreateNewCustomColumn(self.gui) if CreateNewCustomColumn else None
        )

        # ------------------------------------ LIBBY ------------------------------------
        libby_section = QGroupBox(_("Libby"))
        libby_layout = QFormLayout()
        libby_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        libby_section.setLayout(libby_layout)
        self.layout.addWidget(libby_section, 0, 0, 1, 2)

        self.libby_setup_status_lbl = QLabel(
            _("Libby is configured.")
            if is_configured
            else _("Libby is not configured yet.")
        )
        # bump up font size a little
        curr_font = self.libby_setup_status_lbl.font()
        curr_font.setPointSizeF(curr_font.pointSizeF() * 1.1)
        self.libby_setup_status_lbl.setFont(curr_font)
        # color
        self.libby_setup_status_lbl.setStyleSheet(
            f"font-weight: bold; color: {PluginColors.Green if is_configured else PluginColors.Red};"
        )
        libby_layout.addRow(self.libby_setup_status_lbl)

        # Libby Setup Code
        self.libby_setup_code_lbl = QLabel(
            '<a href="https://help.libbyapp.com/en-us/6070.htm">'
            + PreferenceTexts.LIBBY_SETUP_CODE
            + "</a>"
        )
        self.libby_setup_code_lbl.setTextFormat(Qt.RichText)
        self.libby_setup_code_lbl.setOpenExternalLinks(True)
        self.libby_setup_code_lbl.setMinimumWidth(150)
        self.libby_setup_code_txt = QLineEdit(self)
        self.libby_setup_code_txt.setPlaceholderText(
            PreferenceTexts.LIBBY_SETUP_CODE_DESC
        )
        self.libby_setup_code_txt.setInputMask("99999999")
        if not DEMO_MODE:
            self.libby_setup_code_txt.setText(PREFS[PreferenceKeys.LIBBY_SETUP_CODE])
        libby_layout.addRow(self.libby_setup_code_lbl, self.libby_setup_code_txt)

        # ------------------------------------ LOANS ------------------------------------
        loans_section = QGroupBox(_("Loans"))
        loan_layout = QFormLayout()
        loan_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        loans_section.setLayout(loan_layout)
        self.layout.addWidget(loans_section, 1, 0, 3, 1)

        # Hide Ebooks
        self.hide_ebooks_checkbox = QCheckBox(PreferenceTexts.HIDE_EBOOKS, self)
        self.hide_ebooks_checkbox.setChecked(PREFS[PreferenceKeys.HIDE_EBOOKS])
        loan_layout.addRow(self.hide_ebooks_checkbox)

        # Hide Magazine
        self.hide_magazines_checkbox = QCheckBox(PreferenceTexts.HIDE_MAGAZINES, self)
        self.hide_magazines_checkbox.setChecked(PREFS[PreferenceKeys.HIDE_MAGAZINES])
        loan_layout.addRow(self.hide_magazines_checkbox)

        # Hide books already in library
        self.hide_books_already_in_lib_checkbox = QCheckBox(
            PreferenceTexts.HIDE_BOOKS_ALREADY_IN_LIB, self
        )
        self.hide_books_already_in_lib_checkbox.setChecked(
            PREFS[PreferenceKeys.HIDE_BOOKS_ALREADY_IN_LIB]
        )
        loan_layout.addRow(self.hide_books_already_in_lib_checkbox)

        # Exclude empty books when hiding titles already in library
        self.exclude_empty_books_checkbox = QCheckBox(
            PreferenceTexts.EXCLUDE_EMPTY_BOOKS, self
        )
        self.exclude_empty_books_checkbox.setChecked(
            PREFS[PreferenceKeys.EXCLUDE_EMPTY_BOOKS]
        )
        loan_layout.addRow(self.exclude_empty_books_checkbox)

        # Always confirm returns
        self.confirm_returns_checkbox = QCheckBox(PreferenceTexts.CONFIRM_RETURNS, self)
        self.confirm_returns_checkbox.setChecked(
            PREFS[confirm_config_name(PreferenceKeys.CONFIRM_RETURNS)]
        )
        loan_layout.addRow(self.confirm_returns_checkbox)

        # Prefer Open Formats
        self.prefer_open_formats_checkbox = QCheckBox(
            PreferenceTexts.PREFER_OPEN_FORMATS, self
        )
        self.prefer_open_formats_checkbox.setChecked(
            PREFS[PreferenceKeys.PREFER_OPEN_FORMATS]
        )
        loan_layout.addRow(self.prefer_open_formats_checkbox)

        # Enable OverDrive Link plugin integration
        self.enable_overdrive_link_checkbox = QCheckBox(
            PreferenceTexts.OVERDRIVELINK_INTEGRATION, self
        )
        self.enable_overdrive_link_checkbox.setChecked(
            PREFS[PreferenceKeys.OVERDRIVELINK_INTEGRATION]
        )
        loan_layout.addRow(self.enable_overdrive_link_checkbox)

        # Mark updated books
        self.mark_updated_books_checkbox = QCheckBox(
            PreferenceTexts.MARK_UPDATED_BOOKS, self
        )
        self.mark_updated_books_checkbox.setChecked(
            PREFS[PreferenceKeys.MARK_UPDATED_BOOKS]
        )
        loan_layout.addRow(self.mark_updated_books_checkbox)

        # Always download as a new book
        self.always_download_as_new_checkbox = QCheckBox(
            PreferenceTexts.ALWAYS_DOWNLOAD_AS_NEW, self
        )
        self.always_download_as_new_checkbox.setChecked(
            PREFS[PreferenceKeys.ALWAYS_DOWNLOAD_AS_NEW]
        )
        loan_layout.addRow(self.always_download_as_new_checkbox)

        # Tag Ebooks
        self.tag_ebooks_txt = QLineEdit(self)
        self.tag_ebooks_txt.setPlaceholderText(PreferenceTexts.TAG_EBOOKS_PLACEHOLDER)
        if not DEMO_MODE:
            self.tag_ebooks_txt.setText(PREFS[PreferenceKeys.TAG_EBOOKS])
        loan_layout.addRow(PreferenceTexts.TAG_EBOOKS, self.tag_ebooks_txt)

        # Tag Magazines
        self.tag_magazines_txt = QLineEdit(self)
        self.tag_magazines_txt.setPlaceholderText(
            PreferenceTexts.TAG_MAGAZINES_PLACEHOLDER
        )
        if not DEMO_MODE:
            self.tag_magazines_txt.setText(PREFS[PreferenceKeys.TAG_MAGAZINES])
        loan_layout.addRow(PreferenceTexts.TAG_MAGAZINES, self.tag_magazines_txt)

        if self.custom_column_creator:
            # set custom columns to store borrow and due dates
            borrow_date_col_layout = QHBoxLayout()
            due_date_col_layout = QHBoxLayout()

            borrow_date_col_lbl = QLabel(PreferenceTexts.CUSTCOL_BORROWED_DATE)
            self.borrow_date_col_text = QLineEdit(self)
            self.borrow_date_col_text.setClearButtonEnabled(True)
            self.borrow_date_col_text.setText(
                PREFS[PreferenceKeys.CUSTCOL_BORROWED_DATE]
                if self.db.field_metadata.has_key(self.custom_column_name("borrowed"))
                else ""
            )
            borrow_date_col_lbl.setBuddy(self.borrow_date_col_text)
            borrow_date_col_layout.addWidget(borrow_date_col_lbl)
            borrow_date_col_layout.addWidget(self.borrow_date_col_text)

            due_date_col_lbl = QLabel(PreferenceTexts.CUSTCOL_DUE_DATE)
            self.due_date_col_text = QLineEdit(self)
            self.due_date_col_text.setClearButtonEnabled(True)
            self.due_date_col_text.setText(
                PREFS[PreferenceKeys.CUSTCOL_DUE_DATE]
                if self.db.field_metadata.has_key(self.custom_column_name("due"))
                else ""
            )
            due_date_col_lbl.setBuddy(self.due_date_col_text)
            due_date_col_layout.addWidget(due_date_col_lbl)
            due_date_col_layout.addWidget(self.due_date_col_text)

            label_min_width = max(
                due_date_col_lbl.sizeHint().width(),
                borrow_date_col_lbl.sizeHint().width(),
            )
            due_date_col_lbl.setMinimumWidth(label_min_width)
            borrow_date_col_lbl.setMinimumWidth(label_min_width)

            custom_col_buttons = []
            self.borrow_date_col_add_btn = None
            if not self.borrow_date_col_text.text():
                self.borrow_date_col_add_btn = QPushButton("", self)
                self.borrow_date_col_add_btn.clicked.connect(
                    lambda: self.create_custom_column(
                        self.borrow_date_col_text,
                        "borrowed",
                        {"description": _("Loan's borrowed/checkout date")},
                    )
                )
                custom_col_buttons.append(self.borrow_date_col_add_btn)
            self.due_date_col_add_btn = None
            if not self.due_date_col_text.text():
                self.due_date_col_add_btn = QPushButton("", self)
                self.due_date_col_add_btn.clicked.connect(
                    lambda: self.create_custom_column(
                        self.due_date_col_text,
                        "due",
                        {"description": _("Loan's due/expiry date")},
                    )
                )
                custom_col_buttons.append(self.due_date_col_add_btn)
            for btn in custom_col_buttons:
                btn.setIcon(QIcon.ic("plus.png"))
                btn.setToolTip(_c("Create a custom column"))
            if self.borrow_date_col_add_btn:
                borrow_date_col_layout.addWidget(self.borrow_date_col_add_btn)
            if self.due_date_col_add_btn:
                due_date_col_layout.addWidget(self.due_date_col_add_btn)
            for layout in (borrow_date_col_layout, due_date_col_layout):
                layout.setStretch(1, 1)
            loan_layout.addRow(borrow_date_col_layout)
            loan_layout.addRow(due_date_col_layout)

        # ------------------------------------ Holds ------------------------------------
        holds_section = QGroupBox(_("Holds"))
        holds_layout = QFormLayout()
        holds_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        holds_section.setLayout(holds_layout)
        self.layout.addWidget(holds_section, 1, 1)

        # Hide unavailable holds
        self.hide_holds_unavailable_checkbox = QCheckBox(
            PreferenceTexts.HIDE_HOLDS_UNAVAILABLE, self
        )
        self.hide_holds_unavailable_checkbox.setChecked(
            PREFS[PreferenceKeys.HIDE_HOLDS_UNAVAILABLE]
        )
        holds_layout.addRow(self.hide_holds_unavailable_checkbox)

        # Always confirm cancellations
        self.confirm_cancel_hold_checkbox = QCheckBox(
            PreferenceTexts.CONFIRM_CANCELLATIONS, self
        )
        self.confirm_cancel_hold_checkbox.setChecked(
            PREFS[confirm_config_name(PreferenceKeys.CONFIRM_CANCELLATIONS)]
        )
        holds_layout.addRow(self.confirm_cancel_hold_checkbox)

        # ------------------------------------ SEARCH ------------------------------------
        search_section = QGroupBox(_("Search"))
        search_layout = QFormLayout()
        search_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        search_section.setLayout(search_layout)
        self.layout.addWidget(search_section, 2, 1)

        self.search_results_max_txt = QSpinBox(self)
        self.search_results_max_txt.setRange(20, 60)
        self.search_results_max_txt.setSingleStep(10)
        self.search_results_max_txt.setValue(PREFS[PreferenceKeys.SEARCH_RESULTS_MAX])
        search_layout.addRow(
            PreferenceTexts.SEARCH_RESULTS_MAX, self.search_results_max_txt
        )
        self.search_libraries_txt = QTextEdit(self)
        self.search_libraries_txt.setAcceptRichText(False)
        self.search_libraries_txt.setPlaceholderText(
            _(
                "Up to {n} libraries, comma-separated. View your library key codes from the Cards tab. "
                "Example: lapl,sno-isle,livebrary,kcls"
            ).format(n=MAX_SEARCH_LIBRARIES)
        )
        self.search_libraries_txt.setPlainText(
            ",".join(PREFS[PreferenceKeys.SEARCH_LIBRARIES])
        )
        search_libraries_lbl = QLabel(PreferenceTexts.SEARCH_LIBRARIES)
        search_libraries_lbl.setBuddy(self.search_libraries_txt)
        search_libraries_layout = QVBoxLayout()
        search_libraries_layout.addWidget(search_libraries_lbl)
        search_libraries_layout.addWidget(self.search_libraries_txt)
        search_layout.addRow(search_libraries_layout)

        # ------------------------------------ NETWORK ------------------------------------
        network_section = QGroupBox(_("Network"))
        network_layout = QFormLayout()
        network_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        network_section.setLayout(network_layout)
        self.layout.addWidget(network_section, 3, 1)

        self.network_timeout_txt = QSpinBox(self)
        self.network_timeout_txt.setSuffix(_c(" seconds"))
        self.network_timeout_txt.setRange(10, 180)
        self.network_timeout_txt.setSingleStep(10)
        self.network_timeout_txt.setValue(PREFS[PreferenceKeys.NETWORK_TIMEOUT])
        network_layout.addRow(PreferenceTexts.NETWORK_TIMEOUT, self.network_timeout_txt)

        self.network_retry_txt = QSpinBox(self)
        self.network_retry_txt.setRange(0, 5)
        self.network_retry_txt.setValue(PREFS[PreferenceKeys.NETWORK_RETRY])
        network_layout.addRow(PreferenceTexts.NETWORK_RETRY, self.network_retry_txt)

        # Help label
        self.help_lbl = QLabel(
            '<a style="padding: 0 4px;" href="https://github.com/ping/libby-calibre-plugin#setup">'
            + _c("Help")
            + "</a>"
        )
        self.help_lbl.setAlignment(Qt.AlignRight)
        self.help_lbl.setTextFormat(Qt.RichText)
        self.help_lbl.setOpenExternalLinks(True)
        self.layout.addWidget(self.help_lbl, 4, 0, 1, 2)

        self.resize(self.sizeHint())

    def custom_column_name(self, col_type: str):
        return (
            f"{self.db.field_metadata.custom_field_prefix}libby_{col_type.lower()}_date"
        )

    def create_custom_column(self, txt_widget, col_type: str, display=None):
        """
        Launch calibre's create custom column UI for plugins.

        :param txt_widget:
        :param col_type:
        :param display:
        :return:
        """
        if not display:
            display = {}
        lookup_name = self.custom_column_name(col_type)
        result = self.custom_column_creator.create_column(
            lookup_name=lookup_name,
            column_heading=f"Libby {col_type.title()} Date",
            datatype="datetime",
            is_multiple=False,
            display=display,
            freeze_lookup_name=False,
        )
        if result[0] == self.custom_column_creator.Result.CANCELED:
            return
        if result[0] == self.custom_column_creator.Result.COLUMN_ADDED:
            txt_widget.setText(result[1])
        elif result[0] == self.custom_column_creator.Result.DUPLICATE_KEY:
            txt_widget.setText(lookup_name)
        else:
            return error_dialog(self, str(result[0]), result[1], show=True)

    def save_settings(self):
        if DEMO_MODE:
            return
        PREFS[PreferenceKeys.HIDE_MAGAZINES] = self.hide_magazines_checkbox.isChecked()
        PREFS[PreferenceKeys.HIDE_EBOOKS] = self.hide_ebooks_checkbox.isChecked()
        PREFS[
            PreferenceKeys.PREFER_OPEN_FORMATS
        ] = self.prefer_open_formats_checkbox.isChecked()
        PREFS[
            PreferenceKeys.HIDE_BOOKS_ALREADY_IN_LIB
        ] = self.hide_books_already_in_lib_checkbox.isChecked()
        PREFS[
            PreferenceKeys.EXCLUDE_EMPTY_BOOKS
        ] = self.exclude_empty_books_checkbox.isChecked()
        PREFS[PreferenceKeys.TAG_EBOOKS] = self.tag_ebooks_txt.text().strip()
        PREFS[PreferenceKeys.TAG_MAGAZINES] = self.tag_magazines_txt.text().strip()
        PREFS[
            PreferenceKeys.HIDE_HOLDS_UNAVAILABLE
        ] = self.hide_holds_unavailable_checkbox.isChecked()
        PREFS[
            confirm_config_name(PreferenceKeys.CONFIRM_RETURNS)
        ] = self.confirm_returns_checkbox.isChecked()
        PREFS[
            PreferenceKeys.OVERDRIVELINK_INTEGRATION
        ] = self.enable_overdrive_link_checkbox.isChecked()
        PREFS[
            PreferenceKeys.MARK_UPDATED_BOOKS
        ] = self.mark_updated_books_checkbox.isChecked()
        PREFS[
            PreferenceKeys.ALWAYS_DOWNLOAD_AS_NEW
        ] = self.always_download_as_new_checkbox.isChecked()
        PREFS[PreferenceKeys.NETWORK_TIMEOUT] = int(
            self.network_timeout_txt.cleanText().strip()
        )
        PREFS[PreferenceKeys.NETWORK_RETRY] = int(
            self.network_retry_txt.cleanText().strip()
        )
        PREFS[PreferenceKeys.SEARCH_RESULTS_MAX] = int(
            self.search_results_max_txt.cleanText().strip()
        )
        PREFS[PreferenceKeys.SEARCH_LIBRARIES] = list(
            set(
                [
                    lib_key.strip().lower()
                    for lib_key in self.search_libraries_txt.toPlainText()
                    .strip()
                    .split(",")
                    if lib_key.strip()
                ]
            )
        )[:MAX_SEARCH_LIBRARIES]
        if (
            self.custom_column_creator
            and hasattr(self, "borrow_date_col_text")
            and hasattr(self, "due_date_col_text")
        ):
            borrowed_date_custcol_name = (
                self.borrow_date_col_text.text() or ""
            ).strip()
            due_date_custcol_name = (self.due_date_col_text.text() or "").strip()
            if (
                borrowed_date_custcol_name
                and not borrowed_date_custcol_name.startswith(
                    self.db.field_metadata.custom_field_prefix
                )
            ) or (
                due_date_custcol_name
                and not due_date_custcol_name.startswith(
                    self.db.field_metadata.custom_field_prefix
                )
            ):
                # We could validate more, but we'll just be replicating more
                # calibre code. Field updates failures are silently caught
                # and do not break the download job.
                return error_dialog(
                    self,
                    _c("Custom columns"),
                    _c("The lookup name must begin with a '#'"),
                    show=True,
                )
            PREFS[PreferenceKeys.CUSTCOL_BORROWED_DATE] = (
                self.borrow_date_col_text.text() or ""
            )
            PREFS[PreferenceKeys.CUSTCOL_DUE_DATE] = self.due_date_col_text.text() or ""

        setup_code = self.libby_setup_code_txt.text().strip()
        if setup_code != PREFS[PreferenceKeys.LIBBY_SETUP_CODE]:
            # if libby sync code has changed, do sync and save token
            from .libby import LibbyClient

            if not LibbyClient.is_valid_sync_code(setup_code):
                # save a http request for get_chip()
                return error_dialog(
                    self,
                    _("Libby Setup Code"),
                    _("Invalid setup code format: {code}").format(code=setup_code),
                    show=True,
                )

            libby_client = LibbyClient(
                logger=logger,
                timeout=PREFS[PreferenceKeys.NETWORK_TIMEOUT],
                max_retries=PREFS[PreferenceKeys.NETWORK_RETRY],
            )
            chip_res = libby_client.get_chip()
            libby_client.clone_by_code(setup_code)
            if libby_client.is_logged_in():
                PREFS[PreferenceKeys.LIBBY_SETUP_CODE] = setup_code
                PREFS[PreferenceKeys.LIBBY_TOKEN] = chip_res["identity"]

        if self.custom_column_creator and (
            self.custom_column_creator.gui.must_restart_before_config
            or self.custom_column_creator.must_restart()
        ):
            msg = _c(
                "Some of the changes you made require a restart."
                " Please restart calibre as soon as possible."
            )
            return show_restart_warning(msg, self)
