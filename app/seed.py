from datetime import date, time, timedelta

from app import db
from app.models import Event, Registration, User
from app.services.qr_service import create_registration_qr


def seed_database():
    if User.query.first():
        existing_events = Event.query.order_by(Event.id).all()
        image_urls = [
            "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=1200&q=85",
            "https://images.unsplash.com/photo-1503095396549-807759245b35?auto=format&fit=crop&w=1200&q=85",
            "https://images.unsplash.com/photo-1556761175-b413da4baf72?auto=format&fit=crop&w=1200&q=85",
        ]
        changed = False
        for event, image_url in zip(existing_events, image_urls):
            if not event.image:
                event.image = image_url
                changed = True
        if changed:
            db.session.commit()
        _add_expanded_events()
        return
    admin = User(full_name="Avery Morgan", email="admin@campus.local", role="ADMIN")
    organizer = User(full_name="Jordan Lee", email="organizer@campus.local", role="EVENT ORGANIZER")
    students = [User(full_name="Maya Chen", email="maya@campus.local", student_id="STU-1001"), User(full_name="Noah Williams", email="noah@campus.local", student_id="STU-1002")]
    for user in [admin, organizer, *students]:
        user.set_password("password123")
        db.session.add(user)
    db.session.flush()
    events = [
        Event(title="Campus Hack Night", description="A hands-on evening for students building prototypes, testing ideas and collaborating across disciplines. Bring a laptop, form a team and build something useful before the night ends.", category="Technical", event_date=date.today() + timedelta(days=9), start_time=time(17), end_time=time(22), venue="Innovation Lab", max_participants=200, registration_deadline=date.today() + timedelta(days=7), created_by=organizer.id, image="https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=1200&q=85"),
        Event(title="Spring Arts Showcase", description="A curated evening featuring student theatre, contemporary dance, live music and visual installations from across the university.", category="Cultural", event_date=date.today() + timedelta(days=18), start_time=time(18), end_time=time(21), venue="Main Auditorium", max_participants=240, registration_deadline=date.today() + timedelta(days=15), created_by=organizer.id, image="https://images.unsplash.com/photo-1503095396549-807759245b35?auto=format&fit=crop&w=1200&q=85"),
        Event(title="Career Launch Workshop", description="A practical career session focused on portfolio reviews, interview preparation and one-to-one guidance from alumni and industry mentors.", category="Career", event_date=date.today() + timedelta(days=25), start_time=time(14), end_time=time(17), venue="Business School 204", max_participants=60, registration_deadline=date.today() + timedelta(days=22), created_by=organizer.id, image="https://images.unsplash.com/photo-1556761175-b413da4baf72?auto=format&fit=crop&w=1200&q=85"),
    ]
    db.session.add_all(events)
    db.session.flush()
    for student, event in [(students[0], events[0]), (students[1], events[1])]:
        registration = Registration(user_id=student.id, event_id=event.id)
        db.session.add(registration)
        db.session.flush()
        create_registration_qr(registration)
    _add_expanded_events()
    db.session.commit()


def _add_expanded_events():
    organizer = User.query.filter_by(role="EVENT ORGANIZER").first()
    if not organizer:
        return
    existing_titles = {event.title for event in Event.query.all()}
    content_updates = {
        "Campus Hack Night": ("A hands-on evening for students building prototypes, testing ideas and collaborating across disciplines. Bring a laptop, form a team and build something useful before the night ends.", "Technical", 200),
        "Spring Arts Showcase": ("A curated evening featuring student theatre, contemporary dance, live music and visual installations from across the university.", "Cultural", 240),
        "Career Launch Workshop": ("A practical career session focused on portfolio reviews, interview preparation and one-to-one guidance from alumni and industry mentors.", "Career", 60),
        "CU Fest 2026": ("Three days of music, performances, student showcases, competitions and campus-wide activities bringing together students from across the university.", "Cultural", 5000),
        "CU CodeSprint Hackathon": ("A 24-hour engineering challenge where teams solve real-world problems through software, hardware and creative technology.", "Technical", 300),
        "E-Summit Startup Showcase": ("Student founders present their ventures to mentors, investors and industry professionals during an evening of pitches, networking and product demonstrations.", "Competition", 200),
    }
    refreshed = False
    for event in Event.query.all():
        update = content_updates.get(event.title)
        if update and (event.description, event.category, event.max_participants) != update:
            event.description, event.category, event.max_participants = update
            refreshed = True
    if refreshed:
        db.session.commit()
    new_events = [
        Event(title="CU Fest 2026", description="Three days of music, performances, student showcases, competitions and campus-wide activities bringing together students from across the university.", category="Cultural", event_date=date.today() + timedelta(days=34), start_time=time(10), end_time=time(22), venue="Central Grounds", max_participants=5000, registration_deadline=date.today() + timedelta(days=27), created_by=organizer.id, image="https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=1200&q=85"),
        Event(title="CU CodeSprint Hackathon", description="A 24-hour engineering challenge where teams solve real-world problems through software, hardware and creative technology.", category="Technical", event_date=date.today() + timedelta(days=46), start_time=time(9), end_time=time(9), venue="Applied Sciences Block", max_participants=300, registration_deadline=date.today() + timedelta(days=38), created_by=organizer.id, image="https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1200&q=85"),
        Event(title="E-Summit Startup Showcase", description="Student founders present their ventures to mentors, investors and industry professionals during an evening of pitches, networking and product demonstrations.", category="Competition", event_date=date.today() + timedelta(days=58), start_time=time(11), end_time=time(17), venue="Business School Atrium", max_participants=200, registration_deadline=date.today() + timedelta(days=51), created_by=organizer.id, image="https://images.unsplash.com/photo-1556761175-5973dc0f32e7?auto=format&fit=crop&w=1200&q=85"),
        Event(title="CU Inter-College Cricket Cup", description="A high-energy day of competitive cricket, campus rivalries, and community spirit.", category="Sports", event_date=date.today() + timedelta(days=67), start_time=time(8), end_time=time(18), venue="University Sports Complex", max_participants=500, registration_deadline=date.today() + timedelta(days=60), created_by=organizer.id, image="https://images.unsplash.com/photo-1531415074968-036ba1b575da?auto=format&fit=crop&w=1200&q=85"),
        Event(title="TEDx Chandigarh University", description="Ideas worth sharing from students, alumni, researchers, and changemakers shaping tomorrow.", category="Seminar", event_date=date.today() + timedelta(days=79), start_time=time(15), end_time=time(19), venue="University Auditorium", max_participants=700, registration_deadline=date.today() + timedelta(days=72), created_by=organizer.id, image="https://images.unsplash.com/photo-1475721027785-f74eccf877e2?auto=format&fit=crop&w=1200&q=85"),
        Event(title="CU Battle of Bands", description="Turn the volume up for an electrifying student showcase, judged by live audience energy.", category="Cultural", event_date=date.today() + timedelta(days=88), start_time=time(17), end_time=time(21), venue="Open Air Theatre", max_participants=900, registration_deadline=date.today() + timedelta(days=81), created_by=organizer.id, image="https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?auto=format&fit=crop&w=1200&q=85"),
        Event(title="Campus Gaming Arena", description="A fast-paced esports night featuring team battles, arcade challenges, and prizes for the top players.", category="Competition", event_date=date.today() + timedelta(days=95), start_time=time(16), end_time=time(22), venue="Student Activity Centre", max_participants=450, registration_deadline=date.today() + timedelta(days=88), created_by=organizer.id, image="https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=1200&q=85"),
        Event(title="Moonlight Open Mic", description="Bring a poem, a story, a song, or simply your loudest applause for a relaxed night of student talent.", category="Cultural", event_date=date.today() + timedelta(days=102), start_time=time(18), end_time=time(21), venue="Lakeside Amphitheatre", max_participants=350, registration_deadline=date.today() + timedelta(days=96), created_by=organizer.id, image="https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&w=1200&q=85"),
        Event(title="CU Night Market", description="Street food, thrift finds, student brands, live DJs, and a colourful late-evening campus hangout.", category="Other", event_date=date.today() + timedelta(days=109), start_time=time(17), end_time=time(22), venue="North Campus Boulevard", max_participants=1500, registration_deadline=date.today() + timedelta(days=103), created_by=organizer.id, image="https://images.unsplash.com/photo-1517457373958-b7bdd4587205?auto=format&fit=crop&w=1200&q=85"),
        Event(title="Sunrise Fitness Challenge", description="Start the day with a campus-wide fun run, dance workout, and team fitness challenges.", category="Sports", event_date=date.today() + timedelta(days=116), start_time=time(6), end_time=time(10), venue="University Track", max_participants=600, registration_deadline=date.today() + timedelta(days=110), created_by=organizer.id, image="https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=1200&q=85"),
        Event(title="Design Jam: Future Campus", description="Collaborate across disciplines to redesign one part of campus life in a creative afternoon sprint.", category="Workshop", event_date=date.today() + timedelta(days=123), start_time=time(12), end_time=time(18), venue="Design Studio", max_participants=180, registration_deadline=date.today() + timedelta(days=116), created_by=organizer.id, image="https://images.unsplash.com/photo-1558655146-d09347e92766?auto=format&fit=crop&w=1200&q=85"),
    ]
    additions = [event for event in new_events if event.title not in existing_titles]
    if additions:
        db.session.add_all(additions)
        db.session.commit()
