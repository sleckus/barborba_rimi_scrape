from models.db import DB


class BarboraItem():

    def __init__(self, driver):
        self.driver = driver

    def save(self):
        self.db = DB()
        query = ("INSERT INTO `items`(`title`, `price`, `unit`, `size`, `property`, `category`, `shop`) VALUES ("
                 "%s, %s, %s, %s, %s, %s, %s)")
        self.db.conn.cursor().execute(query, (self.title, 0, "", self.size, "", "", "Barbora"))
        self.db.conn.commit()
        self.db.close()

    def fill(self):
        bip = BarboraItemPage(self.driver)
        self.title = bip.get_title()
        self.size = bip.get_size()