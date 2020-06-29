class AuctionSystem(object):

    def __init__(self):
        self._users = []
        self._items = []

    def register_user(self, user_id, name):
        self._users.append(User(user_id, name))

    def post_item(self, item):
        self._items.append(item)
        for user in self._users:
            if user.id == item.owner_id:
                user.add_post(item.id)
                return

    def make_bid(self, user_id, item_id, price):
        for item in self._items:
            if item.id == item_id:
                item.add_bid(user_id, price)
        for user in self._users:
            if user.id == user_id:
                user.add_bid(item_id, price)

    def get_items(self):
        for item in self._items:
            print(str(item))

    def get_user(self, user_id):
        for user in self._users:
            if user.id == user_id:
                return str(user)

    def search_posts(self, user_id):
        posts = []
        for user in self._users:
            if user.id == user_id:
                posts = user.posts
        for post in posts:
            print(post)
                
    def search_user_bids(self, user_id):
        bids = []
        for user in self._users:
            if user.id == user_id:
                bids = user.bids
        for bid in bids:
            print(bid)
    
    def search_item_bids(self, item_id):
        bids = []
        for item in self._items:
            if item.id == item_id:
                bid = item.bid
        print(bid)
    

class Item(object):

    def __init__(self, item_id, name, description, user_id):
        self._item_id = item_id
        self._name = name
        self._description = description
        self._user_id = user_id
        self._bid = Bid()

    def add_bid(self, user_id, price):
        self._bid.add_bid(user_id, price)

    @property
    def id(self):
        return self._item_id

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def owner_id(self):
        return self._user_id

    @property
    def bid(self):
        return self._bid

    def __str__(self):
        string = "Item_Id: %s\nItem_Name: %s\nItem_Description: %s\nOwner_Id: %s\n"\
                 %(self._item_id, self._name, self._description, self._user_id)
        string += str(self._bid)
        return string


class Electronic(Item):

    def __init__(self, item_id, name, description, user_id, voltage, brand):
        Item.__init__(self, item_id, name, description, user_id)
        self._voltage = voltage
        self._brand = brand

    def __str__(self):
        string = Item.__str__(self)
        string += "Voltage: %s\nBrand:%s\n"%(self._voltage, self._brand)
        return string


class Furniture(Item):
    def __init__(self, item_id, name, description, user_id, material, age):
        Item.__init__(self, item_id, name, description, user_id)
        self._age = age
        self._material = material

    def __str__(self):
        string = Item.__str__(self)
        string += "Material: %s\nAge:%s\n" % (self._material, self._age)
        return string


class Book(Item):
    def __init__(self, item_id, name, description, user_id, author, publish_year):
        Item.__init__(self, item_id, name, description, user_id)
        self._author = author
        self._publish_year = publish_year

    def __str__(self):
        string = Item.__str__(self)
        string += "Author: %s\nPublish_Year:%s\n" % (self._author, self._publish_year)
        return string


class User(object):

    def __init__(self, user_id, name):
        self._user_id = user_id
        self._name = name
        self._posts = []
        self._bids = []

    def add_post(self, item_id):
        self._posts.append(item_id)

    def add_bid(self, item_id, price):
        self._bids.append((item_id, price))

    @property
    def id(self):
        return self._user_id

    @property
    def name(self):
        return self._name

    @property
    def posts(self):
        return self._posts
    
    @property
    def bids(self):
        return self._bids

    def __str__(self):
        string = "User_Id: %s\nName: %s\nMy Posts:\n"%(self._user_id, self._name)
        for post in self._posts:
            string += (post + "\n")

        string += "Bids Made:\n"
        for bid in self._bids:
            string += (bid[0] + " $" + str(bid[1]) + "\n")
        return string


class Bid(object):

    def __init__(self):
        self._bids = []

    def add_bid(self, user_id, price):
        self._bids.append((user_id, price))

    def __str__(self):
        string = "All_Bids:\n"
        for bid in self._bids:
            string += (bid[0] + "  $" + str(bid[1]) + "\n")
        return string

system = AuctionSystem()
system.register_user("U001","Jack")
system.register_user("U002","Tom")
system.register_user("U003","Jason")
system.register_user("U004","David")
book = Book("I001","Agile Design","AnAgile Design Guide book", "U001", "Aarthi", "1996")
electronic = Electronic("I002","Iphone7","latest iphone", "U003","220V", "Apple")
furniture = Furniture("I003","Table","a nice table", "U003", "Wood", "5 years")
system.post_item(book)
system.post_item(electronic)
system.post_item(furniture)
system.make_bid("U002","I001", 800)
system.make_bid("U003","I001", 900)
system.make_bid("U003","I002", 200)
system.make_bid("U004","I002", 220)
system.make_bid("U001","I002", 250)
system.make_bid("U004","I002", 300)
system.make_bid("U001","I002", 350)
system.make_bid("U004","I001", 920)
system.make_bid("U004","I003", 40)
system.make_bid("U002","I003", 50)
system.make_bid("U001","I003", 60)
system.make_bid("U002","I003", 80)


system.get_users()
print("---------------------")
system.get_items()
