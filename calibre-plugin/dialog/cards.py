#
# Copyright (C) 2023 github.com/ping
#
# This file is part of the OverDrive Libby Plugin by ping
# OverDrive Libby Plugin for calibre / libby-calibre-plugin
#
# See https://github.com/ping/libby-calibre-plugin for more
# information
#
from urllib.parse import urljoin

from calibre.utils.config import tweaks
from calibre.utils.date import dt_as_local, format_date
from lxml import etree
from qt.core import (
    QCursor,
    QDesktopServices,
    QFrame,
    QGridLayout,
    QLabel,
    QMenu,
    QMouseEvent,
    QPalette,
    QPixmapCache,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QUrl,
    QWidget,
    Qt,
    pyqtSignal,
)

from .base import BaseDialogMixin
from .. import DEMO_MODE
from ..borrow_book import LibbyBorrowHold
from ..compat import _c
from ..libby import LibbyClient
from ..models import LibbyCardsModel
from ..utils import (
    PluginIcons,
    obfuscate_date,
    obfuscate_int,
    obfuscate_name,
    svg_to_pixmap,
)

# noinspection PyUnreachableCode
if False:
    load_translations = _ = lambda x=None: x


load_translations()

gui_libby_borrow_hold = LibbyBorrowHold()


class ClickableQLabel(QLabel):
    clicked = pyqtSignal(QMouseEvent)
    doubleClicked = pyqtSignal(QMouseEvent)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, ev):
        self.clicked.emit(ev)

    def mouseDoubleClickEvent(self, ev):
        self.doubleClicked.emit(ev)


class CardWidget(QWidget):
    def __init__(self, card, library, tab, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.card = card
        self.library = library
        self.tab = tab
        self.icons = self.tab.icons
        layout = QGridLayout()
        layout.setColumnStretch(1, 1)
        self.setLayout(layout)
        widget_row_pos = 0

        # Library Card Icon
        library_card_lbl = QLabel(self)
        # render pixmap
        card_pixmap_cache_id = f'card_website_{library["websiteId"]}'
        card_pixmap = QPixmapCache.find(card_pixmap_cache_id)
        if not QPixmapCache.find(card_pixmap_cache_id):
            svg_root = etree.fromstring(self.icons[PluginIcons.Card])
            if not DEMO_MODE:
                stop1 = svg_root.find('.//stop[@class="stop1"]', svg_root.nsmap)
                stop1.attrib["stop-color"] = library["settings"]["primaryColor"]["hex"]
                stop2 = svg_root.find('.//stop[@class="stop2"]', svg_root.nsmap)
                stop2.attrib["stop-color"] = library["settings"]["secondaryColor"][
                    "hex"
                ]
            card_pixmap = svg_to_pixmap(
                etree.tostring(svg_root), size=(40, 30)
            )  # original size=(80, 60)
            QPixmapCache.insert(card_pixmap_cache_id, card_pixmap)
        library_card_lbl.setPixmap(card_pixmap)
        layout.addWidget(library_card_lbl, widget_row_pos, 0)

        # Library Name
        library_lbl = ClickableQLabel(
            library["name"]
            if not DEMO_MODE
            else (
                "Random "
                f'#{obfuscate_int(library["websiteId"], offset=int(library["websiteId"]/2), min_value=1, max_val=999)}'
                " Library"
            )
        )
        curr_font = library_lbl.font()
        curr_font.setPointSizeF(curr_font.pointSizeF() * 1.2)
        library_lbl.setFont(curr_font)
        library_lbl.setStyleSheet("font-weight: bold;")
        library_lbl.doubleClicked.connect(
            lambda: self.tab.display_debug("Library", self.library)
        )
        library_lbl.setContextMenuPolicy(Qt.CustomContextMenu)
        library_lbl.customContextMenuRequested.connect(
            self.library_lbl_context_menu_requested
        )
        library_lbl.setToolTip(_("Right-click for shortcuts"))
        layout.addWidget(library_lbl, widget_row_pos, 1, 1, 3)
        widget_row_pos += 1

        # Card Name
        card_name = (
            card["cardName"] if not DEMO_MODE else obfuscate_name(card["cardName"])
        )
        card_lbl = ClickableQLabel("<b>" + _("Card name") + "</b>: " + card_name)
        card_lbl.setTextFormat(Qt.RichText)
        card_lbl.doubleClicked.connect(
            lambda: self.tab.display_debug("Card", self.card)
        )
        layout.addWidget(card_lbl, widget_row_pos, 0, 1, 2)

        # Card Number
        if card.get("username"):
            card_username = (
                card["username"] if not DEMO_MODE else obfuscate_name(card["username"])
            )
            card_user_lbl = QLabel("<b>" + _("Card account") + "</b>: " + card_username)
            card_user_lbl.setTextInteractionFlags(
                Qt.TextSelectableByKeyboard | Qt.TextSelectableByMouse
            )
            layout.addWidget(card_user_lbl, widget_row_pos, 2, 1, 2)
        widget_row_pos += 1

        # Card Created Date
        if card.get("createDate"):
            dt_value = dt_as_local(LibbyClient.parse_datetime(card["createDate"]))
            card_create_lbl = QLabel(
                "<b>"
                + _("Created date")
                + "</b>: "
                + format_date(
                    dt_value
                    if not DEMO_MODE
                    else obfuscate_date(dt_value, year=dt_value.year),
                    tweaks["gui_timestamp_display_format"],
                )
            )
            card_create_lbl.setTextFormat(Qt.RichText)
            layout.addWidget(card_create_lbl, widget_row_pos, 0, 1, 2)

            # Verified Date
            if card.get("authorizeDate"):
                dt_value = dt_as_local(
                    LibbyClient.parse_datetime(card["authorizeDate"])
                )
                card_auth_lbl = QLabel(
                    "<b>"
                    + _("Verified date")
                    + "</b>: "
                    + format_date(
                        dt_value
                        if not DEMO_MODE
                        else obfuscate_date(dt_value, year=dt_value.year),
                        tweaks["gui_timestamp_display_format"],
                    )
                )
                card_auth_lbl.setTextFormat(Qt.RichText)
                layout.addWidget(card_auth_lbl, widget_row_pos, 2, 1, 2)
            widget_row_pos += 1

        # loans limits
        loans_limit = card.get("limits", {}).get("loan", 0)
        loans_count = card.get("counts", {}).get("loan", 0)
        loans_progressbar = QProgressBar(self)
        loans_progressbar.setFormat(_("Loans") + " %v/%m")
        loans_progressbar.setMinimum(0)
        loans_progressbar.setMaximum(
            loans_limit
            if not DEMO_MODE
            else obfuscate_int(loans_limit, offset=10, min_value=10)
        )
        loans_progressbar.setValue(
            loans_count if not DEMO_MODE else obfuscate_int(loans_count)
        )
        loans_progressbar.setContextMenuPolicy(Qt.CustomContextMenu)
        loans_progressbar.customContextMenuRequested.connect(
            self.loans_progressbar_context_menu_requested
        )
        loans_progressbar.setToolTip(_("Right-click for shortcuts"))
        layout.addWidget(loans_progressbar, widget_row_pos, 0, 1, 4)
        widget_row_pos += 1

        # holds limits
        holds_limit = card.get("limits", {}).get("hold", 0)
        holds_count = card.get("counts", {}).get("hold", 0)
        holds_progressbar = QProgressBar(self)
        holds_progressbar.setFormat(_("Holds") + " %v/%m")
        holds_progressbar.setMinimum(0)
        holds_progressbar.setMaximum(
            holds_limit
            if not DEMO_MODE
            else obfuscate_int(holds_limit, offset=10, min_value=3)
        )
        holds_progressbar.setValue(
            holds_count if not DEMO_MODE else obfuscate_int(holds_count)
        )
        holds_progressbar.setContextMenuPolicy(Qt.CustomContextMenu)
        holds_progressbar.customContextMenuRequested.connect(
            self.holds_progressbar_context_menu_requested
        )
        holds_progressbar.setToolTip(_("Right-click for shortcuts"))
        layout.addWidget(holds_progressbar, widget_row_pos, 0, 1, 4)

    def library_lbl_context_menu_requested(self):
        menu = QMenu(self)
        menu.addSection(_("Library"))
        view_in_libby_action = menu.addAction(_("View in Libby"))
        view_in_libby_action.setIcon(self.icons[PluginIcons.ExternalLink])
        view_in_libby_action.triggered.connect(self.open_libby_library)
        view_in_overdrive_action = menu.addAction(_("View in OverDrive"))
        view_in_overdrive_action.setIcon(self.icons[PluginIcons.ExternalLink])
        view_in_overdrive_action.triggered.connect(self.open_overdrive_library)
        menu.exec(QCursor.pos())

    def loans_progressbar_context_menu_requested(self):
        menu = QMenu(self)
        menu.addSection(_("Loans"))
        view_in_libby_action = menu.addAction(_("View in Libby"))
        view_in_libby_action.setIcon(self.icons[PluginIcons.ExternalLink])
        view_in_libby_action.triggered.connect(self.open_libby_loans)
        view_in_overdrive_action = menu.addAction(_("View in OverDrive"))
        view_in_overdrive_action.setIcon(self.icons[PluginIcons.ExternalLink])
        view_in_overdrive_action.triggered.connect(self.open_overdrive_loans)
        menu.exec(QCursor.pos())

    def holds_progressbar_context_menu_requested(self):
        menu = QMenu(self)
        menu.addSection(_("Holds"))
        view_in_libby_action = menu.addAction(_("View in Libby"))
        view_in_libby_action.setIcon(self.icons[PluginIcons.ExternalLink])
        view_in_libby_action.triggered.connect(self.open_libby_holds)
        view_in_overdrive_action = menu.addAction(_("View in OverDrive"))
        view_in_overdrive_action.setIcon(self.icons[PluginIcons.ExternalLink])
        view_in_overdrive_action.triggered.connect(self.open_overdrive_holds)
        menu.exec(QCursor.pos())

    def open_link(self, link):
        QDesktopServices.openUrl(QUrl(link))

    def overdrive_url(self):
        return f'https://{self.library["preferredKey"]}.overdrive.com/'

    def open_libby_library(self):
        self.open_link(f'https://libbyapp.com/library/{self.library["preferredKey"]}')

    def open_overdrive_library(self):
        self.open_link(self.overdrive_url())

    def open_libby_loans(self):
        self.open_link(
            f'https://libbyapp.com/shelf/loans/default,all,{self.library["websiteId"]}'
        )

    def open_libby_holds(self):
        self.open_link(
            f'https://libbyapp.com/shelf/holds/default,all,{self.library["websiteId"]}'
        )

    def open_overdrive_loans(self):
        self.open_link(urljoin(self.overdrive_url(), "account/loans"))

    def open_overdrive_holds(self):
        self.open_link(urljoin(self.overdrive_url(), "account/holds"))


class CardsDialogMixin(BaseDialogMixin):
    def __init__(self, gui, icon, do_user_config, icons):
        super().__init__(gui, icon, do_user_config, icons)

        self.libby_cards_model = LibbyCardsModel(None, [], self.db)  # model
        self.models.append(self.libby_cards_model)

        self.card_widgets = []
        self.cards_tab_widget = QWidget()
        self.cards_tab_widget.layout = QGridLayout()
        self.cards_tab_widget.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Maximum
        )
        self.cards_tab_widget.setLayout(self.cards_tab_widget.layout)
        self.cards_scroll_area = QScrollArea()
        self.cards_scroll_area.setBackgroundRole(QPalette.Window)
        self.cards_scroll_area.setFrameShadow(QFrame.Plain)
        self.cards_scroll_area.setFrameShape(QFrame.NoFrame)
        self.cards_scroll_area.setWidgetResizable(True)
        self.cards_scroll_area.setWidget(self.cards_tab_widget)
        widget_row_pos = 0

        # Refresh button
        self.cards_refresh_btn = QPushButton(_c("Refresh"), self)
        self.cards_refresh_btn.setIcon(self.icons[PluginIcons.Refresh])
        self.cards_refresh_btn.setAutoDefault(False)
        self.cards_refresh_btn.setToolTip(_("Get latest loans"))
        self.cards_refresh_btn.clicked.connect(self.cards_refresh_btn_clicked)
        btn_size = self.cards_refresh_btn.size()
        self.cards_refresh_btn.setMaximumSize(self.min_button_width, btn_size.height())
        self.cards_tab_widget.layout.addWidget(self.cards_refresh_btn, 0, 0, 1, 3)
        self.refresh_buttons.append(self.cards_refresh_btn)
        widget_row_pos += 1

        self.libby_cards_model = LibbyCardsModel(None, [], self.db)  # model
        self.models.append(self.libby_cards_model)

        self.libby_cards_model.modelReset.connect(
            lambda: self.libby_cards_model_reset(widget_row_pos)
        )
        self.cards_tab_index = self.add_tab(self.cards_scroll_area, _("Cards"))

    def cards_refresh_btn_clicked(self):
        self.sync()

    def libby_cards_model_reset(self, widget_row_pos):
        for card_widget in self.card_widgets:
            self.cards_tab_widget.layout.removeWidget(card_widget)
            card_widget.setParent(None)
            del card_widget
        self.card_widgets = []
        for i in range(self.libby_cards_model.rowCount()):
            card = self.libby_cards_model.data(
                self.libby_cards_model.index(i, 0), Qt.UserRole
            )
            library = self.libby_cards_model.get_library(
                self.libby_cards_model.get_website_id(card)
            )
            card_widget = CardWidget(card, library, self, self.cards_tab_widget)
            self.card_widgets.append(card_widget)
            self.cards_tab_widget.layout.addWidget(card_widget, widget_row_pos, 0)
            widget_row_pos += 1
            if DEMO_MODE:
                break