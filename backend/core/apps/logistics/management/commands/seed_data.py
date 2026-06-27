import random

from django.core.management.base import BaseCommand
from django.db import transaction

from core.apps.accounts.models import Driver, Roles, User
from core.apps.logistics.models import City, Hub


class Command(BaseCommand):
    help = "Seeds the database with mock cities, hubs, customers, and drivers for development."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting database seeding..."))

        # Raw Data Templates
        cities_data = [
            {"name": "Nairobi", "code": "NBO"},
            {"name": "Mombasa", "code": "MBA"},
            {"name": "Kisumu", "code": "KIS"},
            {"name": "Nakuru", "code": "NKR"},
            {"name": "Eldoret", "code": "EDL"},
        ]

        hub_suffixes = ["Central Sorting Alpha", "Express Hub", "Distribution Center", "West Station"]

        try:
            with transaction.atomic():
                # 1. Seed Cities and Hubs
                self.stdout.write("Seeding Cities and Hubs...")
                created_hubs = []

                for c_data in cities_data:
                    city, created = City.objects.get_or_create(name=c_data["name"], code=c_data["code"])
                    if created:
                        self.stdout.write(f"Created City: {city.name}")

                    # Create 4 Hubs per City to test pagination (Total: 20 Hubs)
                    for suffix in hub_suffixes:
                        hub_name = f"{city.name} {suffix}"
                        hub, hub_created = Hub.objects.get_or_create(
                            name=hub_name,
                            defaults={
                                "city": city,
                                "address": f"Industrial Area, {city.name}, Kenya",
                                "is_active": True,
                            },
                        )
                        if hub_created:
                            created_hubs.append(hub)

                self.stdout.write(self.style.SUCCESS(f"Total Hubs in DB: {Hub.objects.count()}"))

                # 2. Seed Admin User
                self.stdout.write("Seeding Admin...")
                if not User.objects.filter(email="admin@primeflux.com").exists():
                    User.objects.create_superuser(
                        email="admin@primeflux.com",
                        password="AdminPassword123",
                        full_name="System Administrator",
                        phone="0700000000",
                        role=Roles.ADMIN,
                    )
                    self.stdout.write("Created Admin: admin@primeflux.com (Password: AdminPassword123)")

                # 3. Seed Customers (e.g., 15 customers for sorting/pagination)
                self.stdout.write("Seeding Customers...")
                for i in range(1, 16):
                    email = f"customer{i}@gmail.com"
                    phone = f"0711{str(i).zfill(6)}"  # Generates unique 10-digit phone
                    national_id = f"100000{str(i).zfill(2)}"

                    if not User.objects.filter(email=email).exists():
                        User.objects.create_user(
                            email=email,
                            password="CustomerPassword123",
                            full_name=f"Customer John Doe {i}",
                            phone=phone,
                            national_id=national_id,
                            role=Roles.CUSTOMER,
                            is_phone_verified=True,
                            is_email_verified=True,
                        )

                # 4. Seed Drivers allocated across generated hubs
                self.stdout.write("Seeding Drivers and Profiles...")
                all_hubs = list(Hub.objects.all())

                for i in range(1, 11):  # 10 Drivers
                    email = f"driver{i}@primeflux.com"
                    phone = f"0722{str(i).zfill(6)}"
                    national_id = f"200000{str(i).zfill(2)}"
                    license_num = f"DL{str(i).zfill(6)}X"

                    if not User.objects.filter(email=email).exists():
                        user = User.objects.create_user(
                            email=email,
                            password="DriverPassword123",
                            full_name=f"Driver Kamau {i}",
                            phone=phone,
                            national_id=national_id,
                            role=Roles.DRIVER,
                            is_phone_verified=True,
                            is_email_verified=True,
                        )

                        # Assign random active hub to driver
                        assigned_hub = random.choice(all_hubs) if all_hubs else None

                        Driver.objects.get_or_create(
                            user=user,
                            defaults={
                                "license_number": license_num,
                                "is_available": True,
                                "is_verified": True,
                                "current_hub": assigned_hub,
                            },
                        )

            self.stdout.write(self.style.SUCCESS("Database seeded successfully with test workflows setup!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Seeding failed: {str(e)}"))
