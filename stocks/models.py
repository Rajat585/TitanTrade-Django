from django.db import models

# class Stock(models.Model):
#     symbol = models.CharField(max_length=20, unique=True)
#     price = models.FloatField()
#     volume = models.IntegerField()
#     timestamp = models.DateTimeField(auto_now=True)

class Stock(models.Model):
    name = models.CharField(max_length=100, default="Unknown")
    symbol = models.CharField(max_length=20, unique=True)
    price = models.FloatField()
    volume = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.symbol} - {self.price}"

class StockHistory(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField()
    price = models.FloatField()


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
    

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
