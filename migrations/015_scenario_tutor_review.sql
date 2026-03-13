-- Scenario review by language tutor advisor (2026-03-13)
-- Level corrections, removals, and 15 new scenarios

-- ============================================================
-- 1. LEVEL CORRECTIONS
-- ============================================================

-- bank: B1 → A2 (opening account, asking about fees is formulaic enough for A2)
UPDATE scenarios SET minimum_level = 'a2', updated_at = now() WHERE id = 'bank';

-- apartment_hunting: B1 → A2 ("How many rooms? What's the rent?" — accessible for A2)
UPDATE scenarios SET minimum_level = 'a2', updated_at = now() WHERE id = 'apartment_hunting';

-- language_exchange: B1 → A2 (ironic that practicing language is too hard for beginners)
UPDATE scenarios SET minimum_level = 'a2', updated_at = now() WHERE id = 'language_exchange';

-- game_night: B1 → A2 (small talk + simple game interaction is A2)
UPDATE scenarios SET minimum_level = 'a2', updated_at = now() WHERE id = 'game_night';

-- gym: A2 → A1 (simple questions: "How much per month?" "Is there a pool?")
UPDATE scenarios SET minimum_level = 'a1', updated_at = now() WHERE id = 'gym';

-- movie_theater: cap max at B2 (planning movies is too basic for C1/C2)
UPDATE scenarios SET maximum_level = 'b2', updated_at = now() WHERE id = 'movie_theater';

-- library: cap max at B1 (getting a library card, finding books — no challenge after B1)
UPDATE scenarios SET maximum_level = 'b1', updated_at = now() WHERE id = 'library';

-- shopping (clothes): cap max at B2 (transactional, no linguistic challenge after B2)
UPDATE scenarios SET maximum_level = 'b2', updated_at = now() WHERE id = 'shopping';

-- ============================================================
-- 2. NEW SCENARIOS (15)
-- ============================================================

INSERT INTO scenarios (id, icon, category, minimum_level, maximum_level, system_prompt_addition, sort_order, name, goals) VALUES

-- TRAVEL: public transport (A1-B1)
('public_transport', 'bus.fill', 'travel', 'a1', 'b1',
 'You are a helpful commuter on a city bus or metro. The student needs help getting to their destination. Help them with routes, tickets, and stops.',
 108, '{"en": "Taking the Bus/Metro"}', '{"en": ["Ask which bus or metro to take", "Buy a ticket or validate your pass", "Ask when to get off"]}'),

-- TRAVEL: lost item (A2-B1)
('lost_found', 'questionmark.folder.fill', 'travel', 'a2', 'b1',
 'You work at a lost and found office. The student has lost something — a bag, phone, or passport. Help them describe the item and fill out a report.',
 109, '{"en": "Lost & Found"}', '{"en": ["Describe the lost item in detail", "Explain when and where you lost it", "Ask about next steps"]}'),

-- DAILY LIFE: emergency (A2-C2)
('emergency', 'exclamationmark.triangle.fill', 'daily_life', 'a2', 'c2',
 'You are a 911/112 emergency dispatcher. The student is reporting an emergency — an accident, a fire, or someone feeling very sick. Stay calm, ask questions, and give instructions.',
 306, '{"en": "Reporting an Emergency"}', '{"en": ["Describe what happened", "Give your location clearly", "Follow the dispatcher instructions"]}'),

-- DAILY LIFE: flatshare (A2-B2)
('flatshare', 'person.2.badge.key.fill', 'daily_life', 'a2', 'b2',
 'You are looking for a flatmate and the student is interested in the room. Show them around, discuss house rules, lifestyle habits, and rent split.',
 307, '{"en": "Finding a Flatmate"}', '{"en": ["Ask about the room and flat", "Discuss lifestyle and house rules", "Talk about rent and move-in date"]}'),

-- WORK & CAREER: remote meeting (B1-C2)
('remote_meeting', 'video.fill', 'work_and_career', 'b1', 'c2',
 'You are a colleague on a video call. There are typical remote meeting issues — muted mics, screen sharing, connection problems. Discuss a project naturally.',
 406, '{"en": "Remote Video Call"}', '{"en": ["Handle a technical issue politely", "Share your ideas in a discussion", "Confirm action items before ending"]}'),

-- SOCIAL: apology (B1-C2)
('apology', 'hand.raised.fill', 'social', 'b1', 'c2',
 'You are a friend who is upset because the student forgot an important plan or said something hurtful. Give them a chance to apologize and work things out.',
 506, '{"en": "Apologizing to a Friend"}', '{"en": ["Acknowledge what went wrong", "Express a genuine apology", "Propose how to make it right"]}'),

-- SOCIAL: compliment (A2-B2)
('compliment', 'hand.thumbsup.fill', 'social', 'a2', 'b2',
 'You are a friend or colleague in a casual conversation. The student should practice giving and receiving compliments naturally — about appearance, work, cooking, etc.',
 507, '{"en": "Giving & Receiving Compliments"}', '{"en": ["Give a genuine compliment", "Respond to a compliment gracefully", "Continue the conversation naturally"]}'),

-- SOCIAL: social media (A2-B2)
('social_media', 'iphone', 'social', 'a2', 'b2',
 'You are a friend chatting about social media, trending content, and favorite apps. Discuss what you follow online, share recommendations, and debate screen time.',
 508, '{"en": "Talking About Social Media"}', '{"en": ["Describe your online habits", "Discuss a trending topic", "Share your opinion on social media"]}'),

-- HEALTH: veterinarian (A2-B1)
('vet', 'hare.fill', 'health', 'a2', 'b1',
 'You are a veterinarian. The student has brought their pet in because it seems unwell. Ask about symptoms, examine the pet, and explain the treatment.',
 604, '{"en": "At the Veterinarian"}', '{"en": ["Describe your pet''s symptoms", "Understand the diagnosis", "Ask about medication and follow-up"]}'),

-- SERVICES: tech support (B1-C2)
('tech_support', 'desktopcomputer', 'services', 'b1', 'c2',
 'You are a tech support agent. The student is calling because their internet, phone, or computer is not working. Walk them through troubleshooting steps.',
 1004, '{"en": "Calling Tech Support"}', '{"en": ["Describe the technical problem clearly", "Follow troubleshooting steps", "Ask about next steps if not resolved"]}'),

-- SERVICES: formal complaint (B1-C2)
('complaint', 'exclamationmark.bubble.fill', 'services', 'b1', 'c2',
 'You are a customer service manager. The student has a serious complaint about a service — a late delivery, a broken product, or poor service. Handle it professionally.',
 1005, '{"en": "Making a Complaint"}', '{"en": ["Explain the problem and what happened", "State what resolution you expect", "Respond to the proposed solution"]}'),

-- SERVICES: visa / immigration office (B1-C2)
('visa_office', 'doc.text.fill', 'services', 'b1', 'c2',
 'You work at a visa or immigration office. The student needs help with their visa application, residence permit, or work permit. Ask about their situation and explain the process.',
 1006, '{"en": "Visa / Immigration Office"}', '{"en": ["Explain your situation and purpose of stay", "Answer official questions", "Ask about required documents"]}'),

-- SERVICES: moving abroad (B1-C2)
('moving_abroad', 'globe.europe.africa.fill', 'services', 'b1', 'c2',
 'You are a local helping a newcomer who just moved to your country. Discuss how things work — registering at city hall, opening a bank account, finding a doctor, understanding local customs.',
 1007, '{"en": "Moving to a New Country"}', '{"en": ["Explain your situation as a newcomer", "Ask about local services and how things work", "Discuss cultural differences"]}'),

-- EDUCATION: parent-teacher (already exists as parent_teacher, skip)

-- ENTERTAINMENT: escape room already exists, skip

-- EDUCATION: school enrollment for kids (B1-C2)
('school_enrollment', 'pencil.and.ruler.fill', 'education', 'b1', 'c2',
 'You are a school administrator. A parent (the student) is enrolling their child in school. Discuss requirements, school schedule, and extracurricular activities.',
 804, '{"en": "Enrolling Your Child in School"}', '{"en": ["Ask about enrollment requirements", "Discuss the school schedule and subjects", "Ask about extracurricular activities"]}'),

-- DAILY LIFE: grocery shopping (A1-B1) — filling the A1 daily life gap
('grocery', 'basket.fill', 'daily_life', 'a1', 'b1',
 'You are a shop assistant at a small grocery store. Help the student find products, explain where things are, and help with checkout.',
 308, '{"en": "Grocery Shopping"}', '{"en": ["Ask where to find a product", "Ask about prices", "Pay for your items"]}');
