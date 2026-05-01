-- ============================================================
-- TimeBank: Seed Data
-- Realistic sample data for all tables
-- ============================================================

-- ============================================================
-- 1. Insert Members (8 community members)
-- ============================================================
INSERT INTO Member (first_name, last_name, email, phone, date_of_birth, address, city, state, zip_code, is_verified, credit_balance)
VALUES
    ('Aarav', 'Sharma', 'aarav.sharma@email.com', '9876543210', '1995-03-15', '42 MG Road', 'Mumbai', 'Maharashtra', '400001', TRUE, 5.00),
    ('Priya', 'Patel', 'priya.patel@email.com', '9876543211', '1998-07-22', '15 Brigade Road', 'Bangalore', 'Karnataka', '560001', TRUE, 5.00),
    ('Rohan', 'Gupta', 'rohan.gupta@email.com', '9876543212', '1993-11-08', '78 Park Street', 'Kolkata', 'West Bengal', '700016', TRUE, 5.00),
    ('Ananya', 'Reddy', 'ananya.reddy@email.com', '9876543213', '2000-01-25', '23 Jubilee Hills', 'Hyderabad', 'Telangana', '500033', TRUE, 5.00),
    ('Vikram', 'Singh', 'vikram.singh@email.com', '9876543214', '1997-05-30', '56 Connaught Place', 'New Delhi', 'Delhi', '110001', TRUE, 5.00),
    ('Meera', 'Joshi', 'meera.joshi@email.com', '9876543215', '1996-09-12', '89 FC Road', 'Pune', 'Maharashtra', '411004', FALSE, 5.00),
    ('Arjun', 'Nair', 'arjun.nair@email.com', '9876543216', '1994-12-03', '34 Marine Drive', 'Kochi', 'Kerala', '682001', TRUE, 5.00),
    ('Divya', 'Kumar', 'divya.kumar@email.com', '9876543217', '1999-04-18', '67 Anna Nagar', 'Chennai', 'Tamil Nadu', '600040', TRUE, 5.00);

-- ============================================================
-- 2. Insert Skills (12 skills across categories)
-- ============================================================
INSERT INTO Skill (skill_name, category, description)
VALUES
    ('Mathematics Tutoring', 'Education', 'Help with algebra, calculus, statistics, and other math subjects'),
    ('Web Development', 'Technology', 'Building websites using HTML, CSS, JavaScript, and frameworks'),
    ('Guitar Lessons', 'Music', 'Teaching acoustic or electric guitar for beginners to intermediate'),
    ('Yoga Instruction', 'Health & Wellness', 'Teaching yoga poses, breathing techniques, and meditation'),
    ('Home Cooking Classes', 'Cooking', 'Teaching Indian and international cuisine cooking techniques'),
    ('Graphic Design', 'Creative Arts', 'Logo design, poster creation, and visual branding'),
    ('Python Programming', 'Technology', 'Teaching Python basics, data structures, and problem solving'),
    ('Spanish Language', 'Language', 'Conversational Spanish and grammar lessons'),
    ('Photography', 'Creative Arts', 'Digital photography techniques, composition, and editing'),
    ('Gardening Help', 'Home & Garden', 'Plant care, garden layout, and seasonal planting advice'),
    ('Resume Writing', 'Business', 'Professional resume and cover letter writing assistance'),
    ('Fitness Training', 'Sports & Fitness', 'Personalized workout plans and fitness coaching');

-- ============================================================
-- 3. Insert Member Skills (members offering their skills)
-- ============================================================
INSERT INTO Member_Skill (member_id, skill_id, proficiency, hourly_rate, is_active)
VALUES
    -- Aarav: Math Tutoring, Python
    (1, 1, 'Expert', 1.00, TRUE),
    (1, 7, 'Advanced', 1.00, TRUE),
    -- Priya: Web Dev, Graphic Design
    (2, 2, 'Advanced', 1.00, TRUE),
    (2, 6, 'Expert', 1.00, TRUE),
    -- Rohan: Guitar, Photography
    (3, 3, 'Intermediate', 1.00, TRUE),
    (3, 9, 'Advanced', 1.00, TRUE),
    -- Ananya: Yoga, Cooking
    (4, 4, 'Expert', 1.00, TRUE),
    (4, 5, 'Advanced', 1.00, TRUE),
    -- Vikram: Fitness, Spanish
    (5, 12, 'Expert', 1.00, TRUE),
    (5, 8, 'Intermediate', 1.00, TRUE),
    -- Meera: Resume Writing, Web Dev
    (6, 11, 'Advanced', 1.00, TRUE),
    (6, 2, 'Intermediate', 1.00, TRUE),
    -- Arjun: Gardening, Cooking
    (7, 10, 'Advanced', 1.00, TRUE),
    (7, 5, 'Intermediate', 1.00, TRUE),
    -- Divya: Math, Graphic Design
    (8, 1, 'Advanced', 1.00, TRUE),
    (8, 6, 'Intermediate', 1.00, TRUE);

-- ============================================================
-- 4. Insert Service Requests (10 requests)
-- ============================================================
INSERT INTO Service_Request (requester_id, skill_id, title, description, estimated_hours, status, urgency)
VALUES
    (2, 1, 'Need Calculus Help for Exam', 'Preparing for semester exam, need help with integration and differentiation', 3.00, 'Completed', 'High'),
    (3, 2, 'Portfolio Website Design', 'Need a simple portfolio website built with HTML/CSS', 4.00, 'Completed', 'Normal'),
    (5, 4, 'Morning Yoga Sessions', 'Looking for a yoga instructor for 3 morning sessions', 3.00, 'Completed', 'Low'),
    (1, 3, 'Learn Basic Guitar Chords', 'Want to learn basic chords for campfire songs', 2.00, 'Completed', 'Normal'),
    (4, 7, 'Python Basics for Data Science', 'Need help learning Python for data science coursework', 5.00, 'Open', 'High'),
    (6, 12, 'Personal Fitness Plan', 'Need a customized workout routine for weight loss', 2.00, 'Open', 'Normal'),
    (8, 3, 'Guitar for Beginners', 'Want to learn guitar from scratch', 2.00, 'Open', 'Low'),
    (7, 6, 'Logo Design for Startup', 'Need a professional logo for my gardening startup', 3.00, 'Completed', 'High'),
    (1, 5, 'South Indian Cooking Class', 'Want to learn to make dosa, idli, and sambar', 2.00, 'Completed', 'Normal'),
    (3, 11, 'Update My Resume', 'Need help updating my resume for tech job applications', 1.50, 'Open', 'Urgent');

-- ============================================================
-- 5. Insert Service Transactions (5 completed transactions)
-- NOTE: Triggers will automatically handle credit transfers
--       and ledger entries. We insert with status 'Completed'
--       so the trigger fires.
-- ============================================================
INSERT INTO Service_Transaction (request_id, provider_id, requester_id, skill_id, hours_spent, credits_exchanged, status, started_at, completed_at, notes)
VALUES
    (1, 1, 2, 1, 3.00, 3.00, 'Completed', '2026-03-14 09:00:00', '2026-03-15 10:00:00', 'Covered integration, differentiation, and limits. Student understood well.'),
    (2, 2, 3, 2, 4.00, 4.00, 'Completed', '2026-03-17 10:00:00', '2026-03-18 14:00:00', 'Built a responsive portfolio with HTML, CSS, and JavaScript.'),
    (3, 4, 5, 4, 3.00, 3.00, 'Completed', '2026-03-19 06:00:00', '2026-03-20 07:00:00', 'Three morning yoga sessions covering basic asanas and pranayama.'),
    (4, 3, 1, 3, 2.00, 2.00, 'Completed', '2026-03-21 15:00:00', '2026-03-22 16:00:00', 'Taught basic open chords: G, C, D, Em, Am. Practice routine provided.'),
    (8, 2, 7, 6, 3.00, 3.00, 'Completed', '2026-03-24 09:00:00', '2026-03-25 11:00:00', 'Designed logo with 3 iterations. Final version approved by client.');

-- The 5th transaction for request 9 (cooking)
INSERT INTO Service_Transaction (request_id, provider_id, requester_id, skill_id, hours_spent, credits_exchanged, status, started_at, completed_at, notes)
VALUES
    (9, 4, 1, 5, 2.00, 2.00, 'Completed', '2026-03-27 10:00:00', '2026-03-28 12:00:00', 'Taught dosa batter preparation and sambar recipe. Hands-on practice included.');

-- ============================================================
-- 6. Insert Feedback (reviews for completed transactions)
-- ============================================================
INSERT INTO Feedback (transaction_id, reviewer_id, reviewee_id, rating, comment)
VALUES
    -- Transaction 1: Priya reviews Aarav (provider)
    (1, 2, 1, 5, 'Excellent tutor! Explained calculus concepts very clearly. Highly recommended.'),
    -- Transaction 1: Aarav reviews Priya (requester)
    (1, 1, 2, 4, 'Good student, came prepared with questions. Punctual and engaged.'),
    -- Transaction 2: Rohan reviews Priya (provider)
    (2, 3, 2, 5, 'Amazing web developer! My portfolio looks professional and modern.'),
    -- Transaction 2: Priya reviews Rohan (requester)
    (2, 2, 3, 4, 'Clear about requirements. Good communication throughout the project.'),
    -- Transaction 3: Vikram reviews Ananya (provider)
    (3, 5, 4, 5, 'Wonderful yoga instructor. Very patient and knowledgeable about techniques.'),
    -- Transaction 3: Ananya reviews Vikram (requester)
    (3, 4, 5, 5, 'Dedicated student, practiced regularly between sessions. Great attitude.'),
    -- Transaction 4: Aarav reviews Rohan (provider)
    (4, 1, 3, 4, 'Good guitar teacher. Made learning fun with popular song examples.'),
    -- Transaction 5: Arjun reviews Priya (provider)
    (5, 7, 2, 5, 'Outstanding logo design! Very creative and professional work.'),
    -- Transaction 5: Priya reviews Arjun (requester)
    (5, 2, 7, 4, 'Knew exactly what he wanted. Gave constructive feedback on iterations.'),
    -- Transaction 6: Aarav reviews Ananya (provider)
    (6, 1, 4, 5, 'Fantastic cooking class! The dosa turned out perfectly. Great teacher.');

-- ============================================================
-- 7. Insert Welcome Bonus Ledger Entries (for initial members)
-- NOTE: The trigger handles transaction-based entries.
--       We manually insert the welcome bonus entries.
-- ============================================================
-- These are created by sp_register_member in production.
-- For seed data, we insert them manually.
INSERT INTO Time_Credit_Ledger (member_id, credit_type, amount, balance_after, description)
VALUES
    (1, 'BONUS', 5.00, 5.00, 'Welcome bonus: 5 starter credits'),
    (2, 'BONUS', 5.00, 5.00, 'Welcome bonus: 5 starter credits'),
    (3, 'BONUS', 5.00, 5.00, 'Welcome bonus: 5 starter credits'),
    (4, 'BONUS', 5.00, 5.00, 'Welcome bonus: 5 starter credits'),
    (5, 'BONUS', 5.00, 5.00, 'Welcome bonus: 5 starter credits'),
    (6, 'BONUS', 5.00, 5.00, 'Welcome bonus: 5 starter credits'),
    (7, 'BONUS', 5.00, 5.00, 'Welcome bonus: 5 starter credits'),
    (8, 'BONUS', 5.00, 5.00, 'Welcome bonus: 5 starter credits');
