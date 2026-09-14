# CampusFlow

CampusFlow is a complete Flask + SQLite college event management system for planning events, handling student registrations, issuing QR passes, and recording attendance.

## Features

- Secure Flask-Login authentication with hashed passwords and role-based access for admins, students, and event organizers.
- Event CRUD with categories, capacity checks, registration deadlines, status, search, and filtering.
- Student registration with unique registration codes and generated QR images.
- Organizer/admin attendance scanner workflow with duplicate prevention and clear success/error messages.
- Responsive Bootstrap dashboard, event catalog, event detail pages, admin event forms, scanner, empty states, alerts, and loading states.
- REST API for authentication, events, registrations, QR attendance scanning, and event attendance.
- CSV attendance export.
- Seeded demo accounts, events, and registrations on first run.

## Run locally or in Codespaces

```bash
pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:5000`.

Demo password for every seeded account: `password123`

- Admin: `admin@campus.local`
- Organizer: `organizer@campus.local`
- Students: `maya@campus.local`, `noah@campus.local`

Set `SECRET_KEY` and optionally `DATABASE_URL` in the environment for deployment. SQLite is the default; SQLAlchemy can use PostgreSQL by supplying a PostgreSQL URL.

## Structure

```text
app/
	models/       User, Event, Registration, Attendance
	routes/       HTML routes and REST API
	services/     QR generation and attendance validation
	templates/    Bootstrap/Jinja pages
	static/       CSS, JavaScript, generated QR codes
config.py       environment-backed configuration
run.py          application entry point
```

## Database design

`users` stores identities and roles. `events` references its creator. `registrations` joins students to events with a unique `(user_id, event_id)` constraint and unique QR registration code. `attendance` references a registration with a unique registration constraint, making repeated scans safe.

## API

- `POST /api/auth/register` with `full_name`, `email`, `password`
- `POST /api/auth/login` with `email`, `password`
- `GET /api/events`
- `GET /api/events/<id>`
- `POST /api/registrations` with `event_id` (authenticated)
- `POST /api/attendance/scan` with `registration_code` (authenticated organizer/admin)
- `GET /api/attendance/event/<event_id>` (authenticated)

The HTML session cookie authenticates protected API calls. Production deployments should add CSRF protection and a token-based API auth layer for third-party clients.

## QR workflow

After a student registers, the server generates a random registration code and stores a QR image containing that code. An organizer enters or scans that code. The attendance service verifies the registration is active, finds the event and student through the registration relationship, then creates exactly one attendance record. Repeated scans return `Attendance Already Recorded`.

## Future enhancements

Add an external object store for event images, native camera decoding with `html5-qrcode`, email notifications, PostgreSQL migrations, richer analytics charts, and audit logs.

## Event Campus frontend

The application now uses an immersive `Event Campus` interface on top of the existing Flask routes and database. The landing page is built with Jinja and CSS, so the real event records, registration links, authentication, and QR workflows remain server-backed.

- Dark glassmorphic visual system with persistent light/dark theme preference.
- Three.js low-poly campus visualization with buildings, paths, trees, lighting, fog, pointer interaction, and responsive pixel-ratio limits.
- GSAP entrance animations, event-card pointer tilt, marquee category rail, featured event panel, campus location links, and responsive mobile navigation.
- Event imagery and category filtering continue to use the existing `Event` model and `/events` route.
- QR passes retain the real registration code and attendance validation while presenting a premium identity pass.
- `prefers-reduced-motion` disables decorative movement for accessibility.

### UI architecture

`base.html` owns the global Event Campus navigation, theme toggle, fonts, Three.js/GSAP script dependencies, and footer. `index.html` composes the interactive campus landing experience. `campus.css` contains the visual system and responsive layout; `app.js` owns theme persistence, navigation state, card tilt, GSAP reveals, and the Three.js scene.

The dedicated `/campus` route is a separate light-first campus directory. It uses an architectural SVG site plan instead of WebGL, loads event data from `/api/events`, and provides venue selection, event markers, search, filters, map zoom/reset, keyboard access, and responsive tablet/mobile layouts. Its styling lives in `campus-directory.css` and its behavior in `campus-directory.js`.

### Running and screenshots

```bash
pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:5000` to view the experience. For a phone-accessible QR verification link in Codespaces, set `APP_BASE_URL` to the forwarded application URL. Recommended screenshots include the landing campus hero, interactive location grid, featured event, event catalog, dashboard, and QR admission pass.