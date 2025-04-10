import random
import time
from faker import Faker
import json

faker = Faker()

def create_random_line_item():
    qty = random.randint(1, 10)
    price = round(random.uniform(1.0, 100.0), 2)
    return {
        "ItemCode": f"ITEM{random.randint(100, 999)}",
        "ItemDescription": faker.word().capitalize(),
        "ItemPrice": price,
        "ItemQty": qty,
        "TotalValue": round(price * qty, 2)
    }

def create_random_invoice():
    num_items = random.randint(1, 5)
    line_items = [create_random_line_item() for _ in range(num_items)]
    total_amount = round(sum(item["TotalValue"] for item in line_items), 2)
    taxable_amount = round(total_amount * 0.9, 2)
    cgst = round(total_amount * 0.05, 2)
    sgct = round(total_amount * 0.05, 2)

    return {
        "InvoiceNumber": f"INV-{random.randint(100000, 999999)}",
        "CreatedTime": int(time.time()),
        "CustomerCardNo": faker.credit_card_number(),
        "TotalAmount": total_amount,
        "NumberOfItem": num_items,
        "PaymentMethod": random.choice(["CASH", "CARD", "UPI"]),
        "TaxableAmount": taxable_amount,
        "CGST": cgst,
        "SGCT": sgct,
        "CESS": 0.0,
        "InvoiceLineItems": line_items,
        "StoreID": f"STR-{random.randint(100, 999)}",
        "PosID": f"POS-{random.randint(100, 999)}",
        "CustomerType": random.choice(["REGULAR", "PRIME"]),
        "DeliveryType": random.choice(["HOME-DELIVERY", "PICK-UP"]),
        "DeliveryAddress": {
            "AddressLine": faker.street_address(),
            "City": faker.city(),
            "State": faker.state(),
            "PinCode": faker.postcode(),
            "ContactNumber": faker.phone_number() if random.random() > 0.3 else None
        }
    }
# invoice = create_random_invoice()
# print(invoice)
