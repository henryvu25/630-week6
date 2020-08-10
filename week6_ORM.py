"""
These classes are for a POS at a grocery store. The objects instatiated can be used with
SQLAlchemy to store and retrieve from the internal SQLite database

"""
import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
    
class Produce(Base):
    def __init__(self, name, unitPrice, weight, isOrganic = False):
        self.name = name
        self.unitPrice = unitPrice
        self.weight = weight #in pounds
        self.isOrganic = isOrganic #can be used for statistical analysis and business decisions
        self.taxAmt = self.getTax()
        self.totalPrice = unitPrice * self.weight * (1+ self.taxAmt)
        
    __tablename__ = 'produce'
    
    produce_id = Column(Integer, primary_key=True)
    name = Column(String)
    unitPrice = Column(Float)
    weight = Column(Float)
    isOrganic = Column(Boolean)
    taxAmt = Column(Float)
    totalPrice = Column(Float)
        
    def getTax(self): #each subclass has it's own tax rate
        taxAmt = 0.0
        return taxAmt
    
    def discount(self, percentOff):
        decimal = percentOff / 100
        self.unitPrice *= (1 - decimal)
    
    def getWeight(self): 
        return self.weight
    
    def setWeight(self, w): #produce is usually weighed at the register and can be adjusted if you add more items
        self.weight = w
        return self.weight
    
    def __str__(self):
        return "\n{}\nUnit Price: ${:.2f}\nWeight: {:.2f} lbs.\nTotal Price: ${:.2f}\n".format(self.name, self.unitPrice, self.weight, self.totalPrice)
    
class Alcohol(Base):   
    def __init__(self, name, unitPrice, abv, ofAge = False):
        self.name = name
        self.unitPrice = unitPrice
        self.abv = abv #percent alcohol by volume
        self.ofAge = ofAge #Of age to purchase set to False until ID is verified
        self.taxAmt = self.getTax()
        self.totalPrice = unitPrice * (1 + self.taxAmt)
        
    __tablename__ = 'alcohol'
    
    alcohol_id = Column(Integer, primary_key=True)
    name = Column(String)
    unitPrice = Column(Float)
    abv = Column(Float)
    ofAge = Column(Boolean)
    taxAmt = Column(Float)
    totalPrice = Column(Float)
        
    def getTax(self): #beer, wine, and spirits have different tax amounts
        if self.abv <= 10: 
            taxAmt = 0.05 #these percentages are just examples (amounts vary state to state)
        elif self.abv > 10 and self.abv <= 20:
            taxAmt = 0.1
        else:
            taxAmt = 0.2
        return taxAmt
    
    def verifyId(self, year, month, date):
        birthday = datetime.datetime(year, month, date)
        today = datetime.datetime.today()
        dateStr = str((today - birthday)/365.25) #divides the days into years and converts the long datetime object to a string
        age = int(dateStr[:2]) #converts the first two characters of that string to an int
        if age >= 21:
            self.ofAge = True
        else:
            print("Not of age. Purchase prohibited.\n")       
    
    def __str__(self):
        return "\n{}\nUnit Price: ${:.2f}\nABV: {:.1f}%\nAlcohol Tax: {}%\nTotal Price: ${:.2f}\n".format(self.name, self.unitPrice, self.abv, self.taxAmt*100, self.totalPrice)

class Frozen(Base):
    def __init__(self, name, unitPrice, year, month, date, quantity = 1):
        self.name = name
        self.unitPrice = unitPrice
        self.expiration = datetime.datetime(year, month, date)
        self.quantity = quantity
        self.taxAmt = self.getTax()
        self.totalPrice = unitPrice * self.quantity * (1 + self.taxAmt)
        
    __tablename__ = 'frozen'
    
    frozen_id = Column(Integer, primary_key=True)
    name = Column(String)
    unitPrice = Column(Float)
    expiration = Column(DateTime)
    quantity = Column(Integer)
    taxAmt = Column(Float)
    totalPrice = Column(Float)
        
    def getTax(self):
        taxAmt = 0.0
        return taxAmt
    
    def getQuantity(self):
        return self.quantity
    
    def setQuantity(self, q): #can have option to change quantity instead of scanning the same item multiple times
        self.quantity = q
        return self.quantity
    
    def expired(self):
        today = datetime.datetime.today()
        if today > self.expiration:
            print("Item has expired, please replace.")
            return True
        else:
            return False
        
    def __str__(self):
        return "\n{}\nUnit Price: ${:.2f}\nQuantity: {}\nTotal Price: ${:.2f}\n".format(self.name, self.unitPrice, self.quantity, self.totalPrice)

    
def main():
    engine = create_engine('sqlite:///:memory:', echo=False)
    
    Base.metadata.create_all(engine)
    
    produce1 = Produce("Apple", 1.00, 1.0) #objects instantiated
    print(produce1)
    
    alcohol1 = Alcohol("Whiskey", 25.00, 40)
    print(alcohol1)
    
    frozen1 = Frozen("Ice Cream", 10.00, 2020, 8, 29)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    session.add(produce1) #objects added in session
    session.add(alcohol1)
    session.add(frozen1)
    
    newProduce1 = session.query(Produce).filter_by(name="Apple").first() #objects retrieved
    print(newProduce1)
    
    newAlcohol1 = session.query(Alcohol).filter_by(name="Whiskey").first()
    print(newAlcohol1)
    
    newFrozen1 = session.query(Frozen).filter_by(name="Ice Cream").first()
    print(newFrozen1)
    
    
main()