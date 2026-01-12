from src.services.delivery_service import DeliveryService
from src.models.package import Package
from src.models.user import User, UserRole
from src.models.delivery import DeliveryStatus


def test_create_and_manage_delivery(db_session):
    # create a package
    pkg = Package(
        title="Box",
        description="Small box",
        sender_name="Alice",
        sender_phone="111",
        sender_address="1 Road",
        recipient_name="Bob",
        recipient_phone="222",
        recipient_address="2 Lane",
    )
    db_session.add(pkg)
    db_session.commit()
    db_session.refresh(pkg)

    service = DeliveryService(db_session)

    # create delivery
    delivery = service.create_delivery(pkg.id)
    assert delivery is not None
    assert delivery.package_id == pkg.id

    # create courier user
    courier = User(email="courier@example.com", name="C", hashed_password="x", role=UserRole.COURIER)
    db_session.add(courier)
    db_session.commit()
    db_session.refresh(courier)

    # assign courier
    assigned = service.assign_courier(delivery.id, courier.id, courier)
    assert assigned is not None
    assert assigned.courier_id == courier.id

    # update status to PICKED_UP
    updated = service.update_status(delivery.id, DeliveryStatus.PICKED_UP)
    assert updated is not None
    assert updated.status == DeliveryStatus.PICKED_UP

    # update location
    loc = service.update_location(delivery.id, 10.0, 20.0)
    assert loc is not None
    assert loc.current_lat == 10.0
    assert loc.current_lng == 20.0
