import time
from fastapi.testclient import TestClient
from src.main import app
from src.services.delivery_service import DeliveryService
from src.models.package import Package


def test_websocket_delivery_streaming(client, db_session, test_user, auth_headers):
    # Create a package tied to the test user
    pkg = Package(
        title="Test Package",
        description="Integration test package",
        sender_name=test_user.name,
        sender_phone="000-000-0000",
        sender_address="123 Test St",
        recipient_name="Recipient",
        recipient_phone="111-222-3333",
        recipient_address="456 Recipient Rd",
        sender_id=test_user.id,
    )
    db_session.add(pkg)
    db_session.commit()
    db_session.refresh(pkg)

    # Create a delivery for the package using the service
    service = DeliveryService(db_session)
    delivery = service.create_delivery(pkg.id)
    assert delivery is not None

    # Extract raw token from auth headers
    token = auth_headers["Authorization"].split()[1]

    # Ensure websocket auth uses the test DB session (SessionLocal override)
    import src.core.database as core_db
    core_db.SessionLocal = lambda: db_session

    # websocket.auth imported SessionLocal at module import time — override there too
    import src.websocket.auth as ws_auth
    ws_auth.SessionLocal = lambda: db_session

    # Connect to websocket
    with client.websocket_connect(f"/api/ws/connect?token={token}") as ws:
        # Receive connection established message
        msg = ws.receive_json()
        assert msg["type"] == "connection_established"

        # Subscribe to the delivery
        ws.send_json({"type": "subscribe_delivery", "delivery_id": delivery.id})
        # Consume messages until we get delivery_subscribed (auto-subscriptions may emit other messages)
        sub_resp = None
        for _ in range(6):
            msg = ws.receive_json()
            if msg.get("type") == "delivery_subscribed" and int(msg.get("delivery_id", -1)) == delivery.id:
                sub_resp = msg
                break
        assert sub_resp is not None

        # Update the delivery location via HTTP API and verify realtime notification
        res = client.put(
            f"/api/deliveries/{delivery.id}/location",
            json={"lat": 12.34, "lng": 56.78},
            headers=auth_headers,
        )
        assert res.status_code == 200

        # Wait for delivery_location message (allow some interleaved messages)
        received = None
        for _ in range(20):
            msg = ws.receive_json()
            if msg.get("type") == "delivery_location" and int(msg.get("delivery_id", -1)) == delivery.id:
                received = msg
                break
        assert received is not None, "Did not receive delivery_location message"
        assert float(received["lat"]) == 12.34
        assert float(received["lng"]) == 56.78
