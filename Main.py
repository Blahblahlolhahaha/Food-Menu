# Name : Jess Kwek
# Class: DISM/FT/1B/02





import kivy
from kivy.app import App

from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput

from kivy.graphics import RoundedRectangle, Color, Canvas, Rectangle, Line

from kivy.utils import get_color_from_hex

from kivy.properties import ObjectProperty

from validate_email import validate_email
import database.db as db

from functools import partial

import math

class Login(Screen):
    # login screen
    def __init__(self, **kw):
        # get username and password from form
        self.username = ObjectProperty(None)
        self.password = ObjectProperty(None)
        super().__init__(**kw)

    def login(self):
        # check whether credentials are correct
        canlogin = db.sign_in(self.username.text, self.password.text)
        if canlogin:
            self.manager.switch_to(Maininterface(self.username.text))
        else:
            invalid_login()

    def register(self):
        # go to register screen
        self.manager.current = "register"


class Register(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        # get information of text boxes
        namee = ObjectProperty(None)
        email = ObjectProperty(None)
        password1 = ObjectProperty(None)
        password2 = ObjectProperty(None)
        name_label = ObjectProperty(None)
        email_label = ObjectProperty(None)
        password_label = ObjectProperty(None)

        self.username = False
        self.mail = False
        self.password = False

    def clear(self):
        # resets the form
        self.namee.text = ""
        self.email.text = ""
        self.password1.text = ""
        self.password2.text = ""

    def cancel(self):
        # goes back to login screen without doing anything
        self.clear()
        self.manager.current = "login"

    def check_validity(self):
        # form validation
        correct = True
        legit = validate_email(self.email.text)
        if not legit:
            self.email.text = ""
            self.mail = True
            correct = False

        if self.namee.text == "":
            self.namee.text = ""
            self.username = True
            correct = False
        if not self.password1.text == self.password2.text:
            self.password = True
            correct = False
        if correct:
            yes = db.sign_up(self.namee.text, self.email.text,
                             self.password1.text)
            print(yes)
            if yes == "Yes":
                self.clear()
                popup(True)
                self.manager.current = "login"
            elif yes == "existed":
                popup(False)
            else:
                Errorr()
        else:
            show = Invalid(self.username, self.mail, self.password)
            pop = Popup(title="Hello",
                        content=show,
                        size_hint=(None, None),
                        size=(400, 400))
            pop.open()


class Maininterface(Screen):
    def __init__(self, username="", display=0, **kw):
        # main screen and creates navi button and buttons
        super().__init__(**kw)
        self.functions_list = [
            self.main, self.search, self.favourites, self.cart
        ]
        
        self.username = username
        self.food_dict = self.get_all_food() # get all the food from menu
        self.outerbox = BoxLayout(orientation="vertical")

        # makes screen scrollable
        self.food = ScrollView(do_scroll_y=True,
                               do_scroll_x=False,
                               size_hint=(1, 0.9))
        
        self.grid = StartingGrid(size_hint_y=None)
        self.navigation_box = BoxLayout(size_hint=(1, 0.1))

        # navigation buttons
        self.navigation_box.add_widget(
            navigation_button(text="Menu", on_release=self.main))
        self.navigation_box.add_widget(
            navigation_button(text="Search", on_release=self.search))
        self.navigation_box.add_widget(
            navigation_button(text="Favourites", on_release=self.favourites))
        self.navigation_box.add_widget(
            navigation_button(text="Cart", on_release=self.cart))
        self.navigation_box.add_widget(
            navigation_button(text="Logout", on_release=self.logout))
        
        self.functions_list[display]()
        self.food.add_widget(self.grid)
        self.outerbox.add_widget(self.food)
        self.outerbox.add_widget(self.navigation_box)
        self.add_widget(self.outerbox)

    def display_food(self, dictt, fav=False):
        # display food from the dictionary used based on page
        count = 0
        for x, y in dictt.items():
            count += 1
            path = x.replace(" ", "_")
            self.image = Image(source=f"images/{path}.jpeg",
                               size_hint=(1, 0.4))
            self.food_name = Label(text=x,
                                   size_hint=(1, 0.2),
                                   color=(1, 1, 1, 1),
                                   font_size="24sp")
            price = "{:.2f}".format(y)
            self.food_price = Label(text=f"${price}",
                                    size_hint=(1, 0.2),
                                    color=(1, 1, 1, 1),
                                    font_size="24sp")
            self.button = order_button(text="Buy!!!!")
            self.button.bind(on_release=(partial(self.buy, x, y)))
            self.box = BoxLayout(orientation="vertical",
                                 size_hint=(0.9, 0.9),
                                 pos_hint={
                                     "x": 0.05,
                                     "top": 0.95
                                 })
            self.box.add_widget(self.image)
            self.box.add_widget(self.food_name)
            self.box.add_widget(self.food_price)
            if fav:
                self.begone = remove_button(text="Remove!")
                self.begone.bind(on_release=partial(self.remove_fav, x))
                self.button_grid = GridLayout(cols=2)
                self.button_grid.add_widget(self.button)
                self.button_grid.add_widget(self.begone)
                self.box.add_widget(self.button_grid)
            else:
                self.box.add_widget(self.button)
            self.floating = FloatLayout(size_hint_y=None, size=(400, 400))
            self.floating.add_widget(self.box)
            self.grid.add_widget(self.floating)
        self.grid.size = (800,400*math.ceil(count/2))
        if self.grid.size[1] < 540:
            self.grid.size = (800,540)
    def get_all_food(self):
        # get food from database
        food_dict = {}
        all_da_food = db.get_food()
        food_dict = {x[0]: x[1] for x in all_da_food}
        return food_dict

    def main(self, Button=""):
        # main menu
        self.grid.clear_widgets()
        self.display_food(self.food_dict)

    def search(self, Button=""):
        # search for food
        self.grid.clear_widgets()
        self.grid.size=(800,540)
        self.search_input = TextInput(multiline=False,
                                      hint_text="Type something to search!",
                                      size_hint=(0.8, 0.15),
                                      pos_hint={"top": 1})
        self.lets_search = search_button(text="Search!",
                                         size_hint=(0.2, 0.15),
                                         pos_hint={"top": 1})
        self.lets_search.bind(on_release=self.search_time)
        self.container = BoxLayout(orientation="horizontal")
        self.container.add_widget(self.search_input)
        self.container.add_widget(self.lets_search)
        self.grid.add_widget(self.container)

    def search_time(self, Button):
        # finds matching food from main menu
        self.grid.clear_widgets()
        search_item = self.search_input.text
        search_dict = {
            x: y
            for x, y in self.food_dict.items() if search_item.casefold() in x.casefold()
        }
        self.display_food(search_dict)

    def cart(self, Button=""):
        # shows cart of user
        self.grid.clear_widgets()
        cart_list = db.get_cart(self.username)
        if cart_list == []:
            # if user nvr order anything
            self.grid.size=(800,540)
            self.empty_cart = Label(text="You haven't ordered anything! ",
                                    color=(0, 0, 0, 1))
            self.grid.add_widget(self.empty_cart)
        else:
            self.main_container = BoxLayout(orientation="vertical")
            total = 0
            count = 1
            for x in cart_list:
                self.food_container = BoxLayout(orientation='horizontal')
                self.food_and_quantity = Label(text=f"{x[1]} {x[0]}",
                                               color=(1, 1, 1, 1),
                                               font_size="15sp",
                                               bold=True,
                                               halign="center")
                self.summ = Label(text="${:.2f}".format(
                    float(self.food_dict.get(x[0])) * int(x[1])),
                                  color=(1, 1, 1, 1),
                                  font_size="15sp",
                                  bold=True,
                                  halign="center")#label for sum of food
                total += round(float(self.summ.text.strip("$")), 2)
                self.change = edit_button(text="Edit!",
                                          pos_hint={"top": 0.575},
                                          size_hint=(0.5, 0.15))
                self.change.bind(
                    on_release=partial(self.buy, x[0], self.food_dict.get(
                        x[0]), self.username, True))
                self.delete = destroy_button(text="Remove",
                                             pos_hint={"top": 0.575},
                                             size_hint=(0.5, 0.15))
                self.delete.bind(on_release=partial(self.delete_from_cart,
                                                    x[0], self.username))
                self.food_container.add_widget(self.food_and_quantity)
                self.food_container.add_widget(self.summ)
                self.food_container.add_widget(self.change)
                self.food_container.add_widget(self.delete)
                self.main_container.add_widget(self.food_container)
                count += 1
            self.grid.size = (800,200*count)
            if self.grid.size[1] < 540:
                self.grid.size = (800,520)
            got_discount = db.check_discount(self.username)
            if got_discount[0] == 0:
                self.checkout = order_button(text="Pay!\n(${:.2f})".format(
                    round(total, 2)),
                                            pos_hint={"top": 0.4})
            else:
                self.checkout = order_button(text="Pay!\n(${:.2f})\nYou got a 10%% discount!".format(
                    round(total, 2)*0.9),
                                            pos_hint={"top": 0.4},font_size="15sp")
            self.checkout.bind(on_release=self.byebye)
            self.main_container.add_widget(self.checkout)
            self.grid.add_widget(self.main_container)

    def favourites(self, Button=""):
        # shows fav list of user
        self.grid.clear_widgets()
        try_list = db.get_fav(self.username)
        if try_list == "":
            gg_dot_com = Label(
                text="Something went wrong. Please try again later!",
                color=(0, 0, 0, 1))
            self.grid.add_widget(gg_dot_com)
        elif try_list == [('', )]:
            self.grid.size=(800,540)
            empty = Label(
                text="Your favourite list is empty! Time to add some!",
                color=(0, 0, 0, 1))
            self.grid.add_widget(empty)
        else:
            self.fav_list = try_list[0][0].split(",")
            self.fav_dict = {x: self.food_dict.get(x) for x in self.fav_list}
            self.display_food(self.fav_dict, True)

    def buy(self, x, y, username, edit=False, Button=""):
        food_exist = db.check_cart(self.username, x)#check whether food exitst on the cart already
        if not edit:
            if food_exist:
                show = Confirm(x, y, self.username, edit)
                self.manager.switch_to(show)
            else:
                show = Buy(x, y, self.username, edit)
                self.manager.switch_to(show)
        else:
            show = Buy(x, y, self.username, edit)
            self.manager.switch_to(show)

    def remove_fav(self, food, Button):
        # function used for removing favourites
        fav_string = ""
        index = self.fav_list.index(food)#gets index for food in fav-list of the user
        del self.fav_list[index] #delete food from list
        fav_string += ",".join(self.fav_list)#forms the csv used to store in db
        db.update_fav(self.username, fav_string)
        show = Maininterface(self.username)
        self.manager.switch_to(show)

    def delete_from_cart(self, food, username, Button):
        # deletes food from cart
        db.overwrite(username, food)
        show = Maininterface(self.username, 3)
        self.manager.switch_to(show)

    def byebye(self, Button):
        # screen shown when user is done
        db.clear_cart(self.username)
        self.manager.current = "thankyou"

    def logout(self, Button):
        # well logout
        db.clear_cart(self.username)
        self.manager.switch_to(Login())


class Buy(Screen):
    def __init__(self, food="", price="", username="", editt=False, **kw):
        # screen used for ordering food
        super().__init__(**kw)
        self.editt = editt
        self.food = food
        self.price = price
        self.username = username
        self.grid = StartingGrid()
        self.order_box = BoxLayout(orientation="horizontal")
        self.food_label = Label(text="Food:",
                                color=(1, 1, 1, 1),
                                font_size="30sp",
                                bold=True)
        self.choice = Label(text=self.food,
                            color=(1, 1, 1, 1),
                            font_size="30sp",
                            bold=True)
        self.ask_quantity = Label(text=f"How many {food}\nwould you want? ",
                                  color=(1, 1, 1, 1),
                                  font_size="25sp",
                                  bold=True)
        self.quantity = Label(text="0",
                              color=(1, 1, 1, 1),
                              size_hint=(0.34, 1),
                              font_size="30sp",
                              bold=True)

        # buttons used for adding and subtracting the quantity
        self.add = quantity_button("add")
        self.add.bind(on_release=(partial(self.edit, "add")))

        self.remove = quantity_button("minus")
        self.remove.bind(on_release=partial(self.edit, "minus"))

        self.order = Button(text="Order!\n($0.00)")
        self.order.bind(on_release=self.orderr)

        self.cancel = Button(text="cancel")
        self.cancel.bind(on_release=self.returnn)

        self.order_box.add_widget(self.remove)
        self.order_box.add_widget(self.quantity)
        self.order_box.add_widget(self.add)

        self.grid.add_widget(self.food_label)
        self.grid.add_widget(self.choice)
        self.fav_exists = db.check_fav(self.username, self.food)#check whether food is being added to fav b4 or not
        if not self.editt:
            if not self.fav_exists:
                # show the check box to add to fav
                self.fav_label = Label(text="Add to favourites?",
                                       color=(1, 1, 1, 1),
                                       font_size="30sp",
                                       bold=True)
                self.add_fav = CheckBox()
                self.grid.add_widget(self.fav_label)
                self.grid.add_widget(self.add_fav)
        self.grid.add_widget(self.ask_quantity)
        self.grid.add_widget(self.order_box)
        self.grid.add_widget(self.order)
        self.grid.add_widget(self.cancel)
        self.add_widget(self.grid)

    def edit(self, edit, random):
        # used to change the quantity
        if edit == "add":
            self.quantity.text = str(int(self.quantity.text) + 1)
            self.order.text = "Order!\n(${price})".format(
                price="{:.2f}".format(
                    float(self.price) * int(self.quantity.text)))
        else:
            if self.quantity.text != "0":
                self.quantity.text = str(int(self.quantity.text) - 1)
                self.order.text = "Order!\n(${price})".format(
                    price="{:.2f}".format(
                        float(self.price) * int(self.quantity.text)))

    def orderr(self, idkwhy):
        # add food to cart
        if self.quantity.text == "0":
            self.zero_quantity()
        else:
            if not self.editt:
                if not self.fav_exists:
                    if self.add_fav.active:
                        # get fav_list from db
                        fav_list = db.get_fav(self.username)[0][0].split(",")
                        if fav_list == [""]:
                            fav_string = self.food
                        else:
                            fav_list.append(self.food)
                            fav_string = ",".join(fav_list)
                        db.order(self.username, fav_string, self.food,
                                 self.quantity.text, True)
                    else:
                        db.order(self.username, "", self.food,
                                 self.quantity.text, False)
                else:
                    db.order(self.username, "", self.food, self.quantity.text,
                             False)
                back = Maininterface(self.username)
                self.manager.switch_to(back)
            else:
                # update cart based on edits
                db.update_cart(self.username, self.food, self.quantity.text)
                back = Maininterface(self.username, 3)
                self.manager.switch_to(back)

    def returnn(self, idkwhy):
        back = Maininterface(self.username)
        self.manager.switch_to(back)

    def zero_quantity(self):
        show = Zero_quantity()
        pop = Popup(title="Error",
                    content=show,
                    size_hint=(None, None),
                    size=(400, 400))
        pop.open()


class Invalid(Screen):
    def __init__(self, username, email, password, **kw):
        super().__init__(**kw)
        self.box = BoxLayout(orientation="vertical", spacing=20)
        if username:
            self.username = Label(text="Please fill in an username",
                                  size_hint=(0.8, 0.8),
                                  pos_hint={"x": 0.1})
            self.box.add_widget(self.username)
        if email:
            self.email = Label(text="Please fill in a valid email!",
                               size_hint=(0.8, 0.8),
                               pos_hint={"x": 0.1})
            self.box.add_widget(self.email)
        if password:
            self.password = Label(text="Passwords do not match!",
                                  size_hint=(0.8, 0.8),
                                  pos_hint={"x": 0.1})
            self.box.add_widget(self.password)
        self.dismiss = Label(
            text="(Press anywhere outside this popup to dismiss)",
            size_hint=(0.8, 0.8),
            pos_hint={"x": 0.1})
        self.box.add_widget(self.dismiss)
        self.add_widget(self.box)


class Confirm(Screen):
    def __init__(self, food, price, username, edit=False, **kw):
        super().__init__(**kw)
        self.food = food
        self.username = username
        self.price = price

    def overwrite(self):
        db.overwrite(self.username, self.food)
        show = Buy(self.food, self.price, self.username)
        self.manager.switch_to(show)

    def cancel(self):
        show = Maininterface(self.username)
        self.manager.switch_to(show)


class Menu(Screen):
    pass


class Success(Screen):
    pass


class User_exists(Screen):
    pass


class Fail(Screen):
    pass


class Zero_quantity(Screen):
    pass


class Thank_you(Screen):
    pass


class navigation_button(Button):
    pass


class edit_button(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_normal = ""
        self.background_color = (0.98, 0.55, 0.35, 1)


class destroy_button(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_normal = ""
        self.background_color = (0.82, 0.10, 0.16, 1)


class order_button(edit_button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.size_hint = (1, 0.2)


class remove_button(destroy_button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.size_hint = (1, 0.2)


class quantity_button(Button):
    def __init__(self, what, **kw):
        super().__init__(**kw)
        self.size_hint = (0.33, 0.7)
        self.pos_hint = {"top": 0.85}
        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)
        with self.canvas:
            if what == "add":
                self.rect = Rectangle(source="images/right_arrow.png",
                                      pos=self.pos,
                                      size=self.size)
            elif what == "minus":
                self.rect = Rectangle(source="images/left_arrow.png",
                                      pos=self.pos,
                                      size=self.size)
            self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class search_button(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.text = "Search!!"


class StartingGrid(GridLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.cols = 2
        with self.canvas:
            Color(0.01, 0.6, 0.9, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class Bigboss(ScreenManager):
    pass


def popup(valid):
    if valid:
        show = Success()
    else:
        show = User_exists()
    pop = Popup(title="Hello",
                content=show,
                size_hint=(None, None),
                size=(200, 200))
    pop.open()


def Errorr():
    show = Fail()
    pop = Popup(title="Hello",
                content=show,
                size_hint=(None, None),
                size=(200, 200))
    pop.open()


def invalid_login():
    print("hello world")


class Main(App):
    def build(self):
        pass


if __name__ == "__main__":
    db.create_database()
    Main().run()
