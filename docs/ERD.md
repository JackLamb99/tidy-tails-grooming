# Entity-Relationship Diagram (ERD)

This diagram reflects the current Django models in the repository:

- `accounts.User`
- `services.Service`
- `bookings.Booking`
- `contact.ContactMessage`

```mermaid
erDiagram
    USER {
        bigint id PK
        string email UK
        string first_name
        string last_name
        bool is_active
        bool is_staff
        datetime date_joined
    }

    SERVICE {
        bigint id PK
        string name UK
        text description
        text includes
        decimal price_small
        decimal price_medium
        decimal price_large
        bool is_active
        datetime created_at
        datetime updated_at
    }

    BOOKING {
        bigint id PK
        bigint user_id FK
        bigint service_id FK nullable
        bigint original_service_id FK nullable
        string service_name_snapshot
        date date
        time time
        string breed_size
        text notes nullable
        string status
        datetime created_at
        datetime updated_at
    }

    CONTACT_MESSAGE {
        bigint id PK
        string email
        string phone nullable
        string first_name
        string last_name
        string subject
        text message
        datetime created_at
    }

    USER ||--o{ BOOKING : places
    SERVICE ||--o{ BOOKING : selected_for
    SERVICE ||--o{ BOOKING : originally_selected_for
```

## Relationship notes

- A `User` can have many `Booking` records (`Booking.user`).
- A `Booking` optionally references a current `Service` (`Booking.service`) because services can be removed/inactivated.
- A `Booking` also optionally stores its original selected `Service` (`Booking.original_service`) to allow historical/revert logic.
- `ContactMessage` is independent and has no foreign keys.

## Constraint notes

- `Booking` enforces a conditional uniqueness rule on `(date, time)` for active statuses (`confirmed`, `completed`), preventing overlapping active appointments.
- `User.email` and `Service.name` are unique.
