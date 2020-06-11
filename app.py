from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem, ILeftBodyTouch, IRightBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox
from redis.exceptions import ConnectionError


KV = '''
<Content>
    id: modal
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "120dp"

    MDTextField:
        id: new_pr_name
        hint_text: "Product name"
        required: True
        helper_text_mode: "on_error"
        helper_text: "This filed is required!"

    MDTextField:
        id: new_pr_qty
        hint_text: "Quantity"
        required: True
        helper_text_mode: "on_error"
        helper_text: "This filed is required and must be a positive number!"
        on_text: app.qty_filed_validate(self)

<OneLineAvatarIconListItem>:
    on_size:
        self.ids._right_container.width = qty.width + minus_btn.width + plus_btn.width + delete_btn.width
        self.ids._right_container.x = qty.width + minus_btn.width + plus_btn.width + delete_btn.width

    LeftCheckbox:
        on_release: app.checkbox_handler(self)
    
    Container:
    
        MDLabel:
            id: qty
            text_size: (20, None)

        MDIconButton:
            id: minus_btn
            icon: "minus"
            on_release: app.plus_minus_btn_handler(self)

        MDIconButton:
            id: plus_btn
            icon: "plus"
            on_release: app.plus_minus_btn_handler(self)
            
        MDIconButton:
            id: delete_btn
            icon: "delete"
            theme_text_color: "Custom"
            text_color: app.theme_cls.accent_color
            on_release: app.show_alert_dialog(self)


BoxLayout:
    orientation: "vertical"
    padding: 0, 0, 0, 20
    
    MDToolbar:
        title: "Shopping List"
        md_bg_color: app.theme_cls.primary_color
        specific_text_color: 1, 1, 1, 1
        

    ScrollView:

        MDList:
            id: scroll
            
            
    MDFloatingActionButton:
        icon: 'plus'
        md_bg_color: app.theme_cls.primary_color
        pos_hint: {'center_x': .9}
        on_release: app.show_new_product_dialog()
'''


class Content(BoxLayout):
    pass


class LeftCheckbox(ILeftBodyTouch, MDCheckbox):
    """Custom left container."""


class Container(IRightBodyTouch, MDBoxLayout):
    adaptive_width = True


class App(MDApp):
    title = 'Shopping List'
    dialog_new_product = None
    dialog_alert = None
    dialog_connection_failed = None

    def __init__(self, db):
        super().__init__()
        self.products = {}
        self.db = db

    def build(self):
        self.theme_cls.primary_palette = "LightGreen"
        self.theme_cls.accent_palette = "Red"

        return Builder.load_string(KV)

    def on_start(self):
        self.fetch_products()
        self.render_products()

    def fetch_products(self):
        try:
            for key in self.db.keys():
                self.products.update({
                    key.decode(): int(self.db.get(key.decode()).decode())
                })
        except ConnectionError:
            self.show_connection_failed_dialog()

    def show_connection_failed_dialog(self):
        if not self.dialog_connection_failed:
            text = 'Can not connect to server. Please check your internet connection.'
            self.dialog_connection_failed = MDDialog(
                title=text,
                buttons=[
                    MDFlatButton(
                        text="Retry", text_color=self.theme_cls.primary_color,
                        on_release=self.reload_btn_handler
                    ),
                ],
            )
            self.dialog_connection_failed.size_hint_y = 0.4
        self.dialog_connection_failed.open()

    def reload_btn_handler(self, inst):
        self.fetch_products()

        if self.products:
            self.dialog_connection_failed.dismiss()
            self.render_products()

    def render_products(self):
        if self.products:
            for name, qty in self.products.items():
                list_item = OneLineAvatarIconListItem(text=name)
                list_item.ids.qty.text = str(qty)
                self.root.ids.scroll.add_widget(list_item)

    def show_new_product_dialog(self):
        if not self.dialog_new_product:
            self.dialog_new_product = MDDialog(
                title="Add new product:",
                type="custom",
                content_cls=Content(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL", text_color=self.theme_cls.primary_color,
                        on_release=self.close_new_product_dialog
                    ),
                    MDFlatButton(
                        text="OK", text_color=self.theme_cls.primary_color,
                        on_release=self.new_product_ok_btn_handler
                    ),
                ],
            )
            self.dialog_new_product.size_hint_y = 0.4
        self.dialog_new_product.open()

    def close_new_product_dialog(self, inst):
        product_el = self.dialog_new_product.content_cls.ids.new_pr_name
        qty_el = self.dialog_new_product.content_cls.ids.new_pr_qty

        self.clear_dialog_fields(product_el, qty_el)
        self.dialog_new_product.dismiss()

    def clear_dialog_fields(self, product_el, qty_el):
        product_el.text = ''
        qty_el.text = ''

    def new_product_ok_btn_handler(self, inst):
        product_el = self.dialog_new_product.content_cls.ids.new_pr_name
        qty_el = self.dialog_new_product.content_cls.ids.new_pr_qty
        product = product_el.text.lower()

        if product:
            if not qty_el.error:
                product = product_el.text.lower()
                qty = int(qty_el.text)

                if not self.products.get(product):
                    self.add_new_product(product, qty)
                else:
                    qty_el = self.get_product_qty_el(product)
                    current_qty = int(qty_el.text)

                    self.increment_product_qty(
                        product, current_qty, qty_el, new_qty=qty
                    )

                self.dialog_new_product.dismiss()
            self.clear_dialog_fields(product_el, qty_el)

    def add_new_product(self, product, qty):
        result = self.db.set(product, qty)

        if result:
            self.products.update({product: qty})
            list_item = OneLineAvatarIconListItem(text=product)
            list_item.ids.qty.text = str(qty)
            self.root.ids.scroll.add_widget(list_item)

    def get_product_qty_el(self, product):
        for list_item in self.root.ids.scroll.children:
            if list_item.text == product:
                return list_item.ids.qty

    def increment_product_qty(self, product, qty, qty_el, new_qty=1):
        if self.db.exists(product):
            result = self.db.incr(product, new_qty)

            if result:
                new_qty = qty + new_qty
                self.products[product] = new_qty
                qty_el.text = str(new_qty)

    def show_alert_dialog(self, btn_el):
        current_product = btn_el.parent.parent.parent.text
        alert_text = f"Delete {current_product}?"

        if not self.dialog_alert:
            self.dialog_alert = MDDialog(
                text=alert_text,
                buttons=[
                    MDFlatButton(
                        text="CANCEL", text_color=self.theme_cls.primary_color,
                        on_release=self.close_alert_dialog

                    ),
                    MDFlatButton(
                        text="DELETE", text_color=self.theme_cls.primary_color
                    ),
                ],
            )

        for btn in self.dialog_alert.buttons:
            if btn.text == 'DELETE':
                btn.on_release = lambda: self.alert_delete_btn_handler(btn_el)

        self.dialog_alert.text = alert_text
        self.dialog_alert.open()

    def close_alert_dialog(self, inst):
        self.dialog_alert.dismiss()

    def alert_delete_btn_handler(self, btn_el):
        product_el = btn_el.parent.parent.parent
        self.delete_product(product_el)
        self.dialog_alert.dismiss()

    def delete_product(self, product_el):
        product = product_el.text

        if self.db.exists(product):
            result = self.db.delete(product)

            if result:
                self.products.pop(product)
                products_list = product_el.parent
                products_list.remove_widget(product_el)

    def plus_minus_btn_handler(self, inst):
        product_el = inst.parent.parent.parent
        qty_el = product_el.ids.qty
        product = product_el.text
        qty = int(qty_el.text)

        method = inst.icon

        if method == 'plus':
            self.increment_product_qty(product, qty, qty_el)
        else:
            self.decrement_product_qty(product, qty, product_el, qty_el)

    def decrement_product_qty(self, product, qty, product_el, qty_el):
        if qty > 1:
            if self.db.exists(product):
                result = self.db.decr(product, 1)

                if result:
                    new_qty = qty - 1
                    self.products[product] = new_qty
                    qty_el.text = str(new_qty)
        else:
            self.delete_product(product_el)

    def checkbox_handler(self, checkbox):
        product_el = checkbox.parent.parent
        qty_el = product_el.ids.qty
        self.mark_product_field(product_el, qty_el)

    def mark_product_field(self, product_el, qty_el):
        if product_el.theme_text_color == 'Primary':
            product_el.theme_text_color = 'Custom'
            qty_el.theme_text_color = 'Custom'
            product_el.text_color = [0.2, 0.42, 0.12, 1]
            qty_el.text_color = [0.2, 0.42, 0.12, 1]
        else:
            product_el.theme_text_color = 'Primary'
            qty_el.theme_text_color = 'Primary'

    def qty_filed_validate(self, filed_el):
        try:
            qty = int(filed_el.text)
            if qty > 0:
                filed_el.error = False

        except ValueError:
            filed_el.error = True
