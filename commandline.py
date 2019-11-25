# Name : Jess Kwek
# Class: DISM/FT/1B/02


import database.db as db
from validate_email import validate_email
import os


def main():
    def get_all_food():
        food_list = []
        food_dict = {}
        all_da_food = db.get_food()
        for x in all_da_food:
            food_list.append(x[0])
            food_dict[x[0]] = x[1]
        return (food_list, food_dict)

    def login():
        name = input("Username: ")
        password = input("Password: ")
        check = db.sign_in(name, password)
        if check:
            return name
        else:
            return None

    def register():
        while True:
            name = input("Username: \nor press 0 to go back\n>>>")
            email = input("Email: ")
            password = input("Password: ")
            confirm = input("Retype Passowrd: ")
            if name == "0":
                break
            if not password == confirm:
                print("Passwords do not match!\n")
            elif not validate_email(email):
                print("Please enter a valid email!\n")
            else:
                register = db.sign_up(name, email, password)
                if register == "existed":
                    print("Username and/or exists!\n")
                elif register == "No":
                    print("Something went wrong. Please try again later\n")
                else:
                    print("Success!\n")
                    break

    def mainmenu(username):
        def order(listt, fav):
            def get_fav():
                return db.get_fav(username)[0][0].split(",")

            food_list = []
            i = 0
            output = "\nThis is our menu!\n" + "{:50}".format(
                "Food") + "Price\n"
            for x, y in listt.items():
                i += 1
                output += "{:50}".format(f'{i}) {x}') + "$" + str(y) + "\n"
                food_list.append(x)
            print(output)
            while True:
                fav_string = ""
                try:
                    buy = int(
                        input(
                            f"\nWhat would you like to order today?Press 0 to return.Press 1 to {i} to order food"
                        ))
                    if buy > i or buy < 0:
                        raise NameError
                    elif buy == 0:
                        break
                    else:
                        food = food_list[buy - 1]
                        food_exist = db.check_cart(username, food)
                        if food_exist:
                            overwrite = input(
                                "\nThis food already exist on your cart already. Would you want to overwrite it?\n\nPress x to overwrite.\n\nPress any other key to return. "
                            )
                            if not overwrite == "x":
                                break
                            else:
                                db.overwrite(username, food)
                        quantity = int(
                            input(f"How many of {food} would you like?"))
                        if fav:
                            in_fav = db.check_fav(username, food)
                            if not in_fav:
                                add_fav = int(
                                    input(
                                        f"{food} is not in your favourite list, would you like to add it in?\n1) Yes\n0) No\n>>>"
                                    ))
                                if not (add_fav == 1 or add_fav == 0):
                                    raise NameError
                                elif add_fav == 1:
                                    fav_list = get_fav()
                                    if not fav_list == [""]:
                                        fav_list.append(food)
                                        for x in fav_list:
                                            fav_string += f"{x},"
                                        fav_string = fav_string.rstrip(",")
                                    else:
                                        fav_string = food
                                    db.order(username, fav_string, food,
                                             quantity, True)
                                else:
                                    db.order(username, "", food, quantity,
                                             False)
                            else:
                                db.order(username, "", food, quantity, False)
                        else:
                            db.order(username, "", food, quantity, False)
                except NameError as e:
                    print("Please enter a valid input!\n")
                except ValueError as e:
                    print("Please enter a number!\n")

        def display():
            order(food_dict, True)

        def search():
            while True:
                search = {}
                search_item = input(
                    "\nHello! What would you like to search for today? Press 0 to return\n>>>"
                )
                if search_item == "0":
                    break
                for x, y in food_dict.items():
                    if search_item.casefold() in x.casefold():
                        search[x] = y
                if search.__len__() > 0:
                    order(search, True)
                else:
                    print(
                        "There are no results to show. Please ensure your spelling is correct!\n"
                    )

        def favourites():
            def delete():
                fav_string = ""
                i = 1
                output = ""
                for x, y in fav_dict.items():
                    output += f'{i}) {x}\n'
                    i += 1
                print(output)
                try:
                    remove = int(
                        input(
                            f"\nWhat would you like to delete? Press 0 to return to main menu. Press 1 to {i-1} to delete"
                        ))
                    if remove > i or remove < 0:
                        raise NameError
                    fav_list.remove(fav_list[remove])
                    for x in fav_list:
                        fav_string += f"{x},"
                    fav_string = fav_string.rstrip(",")
                    db.update_fav(username, fav_string)
                except NameError as e:
                    print("Please enter a valid number!")
                except ValueError as e:
                    print("Please enter a number!")

            try_list = db.get_fav(username)
            print(try_list)
            if try_list == None:
                print("Something went wrong. Please try again later\n")
            elif try_list == [('', )]:
                print("You have nothing in favourites! Time to add some!\n")
            else:
                fav_list = try_list[0][0].split(",")
                fav_dict = {}
                for x in fav_list:
                    fav_dict[x] = food_dict.get(x)
                while True:
                    try:
                        choice = int(
                            input(
                                "What would you want to do?\n1)Delete favourites\n2)Order favourites!\n3)Return to main menu\n>>>"
                            ))
                        if not (choice == 1 or choice == 2 or choice == 3):
                            raise NameError
                        elif choice == 1:
                            delete()
                        elif choice == 2:
                            order(fav_dict, True)
                        elif choice == 3:
                            break
                    except NameError as e:
                        print("Please enter a valid number!")
                    except ValueError as e:
                        print("Please enter a number!")

        def cart():
            def modify():
                def edit():
                    try:
                        change = int(
                            input(
                                f"\nWhat food would you like to edit? Press 0 to return to main menu. Press 1 to {i-1} to edit the quantity of the food"
                            ))
                        if change > i or change < 0:
                            raise NameError
                        edit_food = food_list[change - 1]
                        quantity = int(
                            input(
                                f"\nHow many of {edit_food} do you want? (Press 0 to return)"
                            ))
                        db.update_cart(username, edit_food, quantity)
                    except NameError as e:

                        print("Please enter a valid number!")
                    except ValueError as e:

                        print("Please enter a number!")

                def delete():
                    try:
                        begone = int(
                            input(
                                f"\nWhat food would you like to edit? Press 0 to return to main menu. Press 1 to {i-1} to edit the quantity of the food"
                            ))
                        if begone > i or begone < 0:
                            raise NameError
                        db.overwrite(username, cart_list[begone - 1])
                    except NameError as e:

                        print("Please enter a valid number!")
                    except ValueError as e:

                        print("Please enter a number!")

                try:
                    choice = int(
                        input(
                            "\nHow would you want to modify the cart?\n1)Edit quantity\n2)Delete\n3)Return to main menu\n>>>"
                        ))
                    if not (choice == 1 or choice == 2 or choice == 3):
                        raise NameError
                    elif choice == 1:
                        edit()
                    elif choice == 2:
                        delete()
                except NameError as e:
                    print("Please enter a valid number!")
                except ValueError as e:
                    print("Please enter a number!")

            def pay():
                print(
                    f"Thank you for using the SP Automated Menu! Your order will cost ${total_string}!"
                )
                db.clear_cart(username)
                os._exit(0)

            refresh = False
            listt = db.get_cart(username)
            if listt == None:
                print("Something went wrong. Please try again later\n")
            elif listt == []:
                print("You have nothing your cart! Time to add some!\n")
            else:
                output = "\n" + "{:6}".format("S/N") + "{:40}".format(
                    "Name") + "Price\n"
                i = 1
                total = 0
                cart_dict = {}
                cart_list = []
                for x in listt:
                    cart_list.append(x[0])
                    summ = round(x[1] * food_dict.get(x[0]), 2)
                    cart_dict[x[0]] = [x[1], summ]
                    print(x[1])
                    output += "{:6}".format(f"{i})") + "{:40}".format(
                        f"{x[1]} {x[0]}") + "{:.2f}".format(summ) + "\n"
                    total += summ
                    i += 1
                print(output)
                while True:
                    try:
                        choice = int(
                            input(
                                "\nWhat would you like to do today?\n1)Modify cart\n2)Check out!\n3)Return to main menu\n>>>"
                            ))
                        if not (choice == 1 or choice == 2 or choice == 3):
                            raise NameError
                        elif choice == 1:
                            modify()
                            refresh = True
                            break
                        elif choice == 2:
                            total_string = "{:.2f}".format(total)
                            pay()
                        elif choice == 3:
                            break
                    except NameError as e:

                        print("Please enter a valid input!")
                    except ValueError as e:

                        print("Please enter a number!")
                if refresh:
                    cart()

        while True:
            try:
                choice = int(
                    input(
                        "What would you like to do today?\n1)Display Main Menu\n2)Search\n3)Favourites\n4)Display Cart\n5)Logout\n>>>"
                    ))
                if not (choice == 1 or choice == 2 or choice == 3
                        or choice == 4 or choice == 5):
                    raise NameError
                if choice == 1:
                    display()
                elif choice == 2:
                    search()
                elif choice == 3:
                    favourites()
                elif choice == 4:
                    cart()
                elif choice == 5:
                    break
            except ValueError as e:
                print("Please enter a number!\n")
            except NameError as e:
                print("Invalid input!\n")

    db.create_database()
    both = get_all_food()
    food_list = both[0]
    food_dict = both[1]
    while True:
        try:
            welcome = int(
                input("Welcome to SPAM!\n1)Login\n2)Register\n0)Exit\n>>>>"))
            if not (welcome == 1 or welcome == 2 or welcome == 0):
                raise NameError
            elif welcome == 1:
                signed_in = login()
                if signed_in is not None:
                    mainmenu(signed_in)
                else:
                    print("Incorrect username and/or password!")
            elif welcome == 2:
                register()
            else:
                break
        except ValueError:
            print("Please enter a number!")
        except NameError as e:
            print("Please enter a valid input!")


main()
