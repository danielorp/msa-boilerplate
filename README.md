## Use cases

Most important: 
- Logistics Operator must be able to accept an order and publish it to Carriers.
- Carrier must be able to accept a shipment order and turn it into a shipment.
- Shipper must be able to receive all the shipment information.
- Carrier should be able to signal the pick up load start and finish.
- Carrier should be able to signal the pick up delivery start and finish.

Less important:
- Shipper should be able to ask and receive a shipment quote.
- Shipper must be able to turn the quote into an order.
- Logistics Operator should be able to pay the Carrier and generate invoice to Shipper.


## Entities

- Shipper
- Logistics Operator
- Carrier
- Order
- Shipment
- Pickup
- Delivery

## Endpoints

```
POST /order -> Order
Body: {
    pickupLocation,
    deliveryDestination,
    weight,
    volume,
    pickupDatetime
}
/* Returns an Order object containing the orderId along with Carrier information */
```

```
POST /shipment -> Shipment
Body: {
    orderId
}
```

```

```
