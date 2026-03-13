-- Seed all 44 conversation scenarios (English only, other translations via admin UI)
-- Level corrections applied per language tutor advisor review (2026-03-13)

INSERT INTO scenarios (id, icon, category, minimum_level, maximum_level, system_prompt_addition, sort_order, name, goals) VALUES

-- TRAVEL
('cafe', 'cup.and.saucer.fill', 'travel', 'a1', 'c2',
 'You are a friendly barista at a café. The student is ordering drinks and food. Guide them through the menu naturally.',
 100, '{"en": "At a Café"}', '{"en": ["Order a drink", "Ask about the menu", "Pay for your order"]}'),

('airport', 'airplane', 'travel', 'a1', 'c2',
 'You work at an airport information desk. The student needs help with check-in, finding their gate, or dealing with a delayed flight.',
 101, '{"en": "At the Airport"}', '{"en": ["Ask about your flight", "Find your gate", "Handle a schedule change"]}'),

('hotel', 'building.2.fill', 'travel', 'a1', 'c2',
 'You are a hotel receptionist. Help the student check in, explain room amenities, and answer questions about the hotel.',
 102, '{"en": "Hotel Check-in"}', '{"en": ["Check in to your room", "Ask about hotel amenities", "Request something for your room"]}'),

('directions', 'map.fill', 'travel', 'a1', 'c2',
 'You are a local who knows the city well. The student is lost and asking for directions to a landmark, restaurant, or hotel.',
 103, '{"en": "Asking Directions"}', '{"en": ["Ask how to get somewhere", "Understand the directions given", "Thank the person"]}'),

('train_station', 'tram.fill', 'travel', 'a2', 'c2',
 'You work at a train station ticket counter. Help the student buy tickets, find their platform, and understand the schedule.',
 104, '{"en": "Train Station"}', '{"en": ["Buy a ticket", "Ask about departure times", "Find your platform"]}'),

('car_rental', 'car.fill', 'travel', 'b1', 'c2',
 'You work at a car rental agency. Help the student choose a car, explain insurance options, and go through the rental agreement.',
 105, '{"en": "Renting a Car"}', '{"en": ["Choose a car type", "Ask about insurance", "Confirm the rental details"]}'),

('tourist_info', 'info.circle.fill', 'travel', 'a2', 'c2',
 'You work at a tourist information center. Recommend local attractions, restaurants, and activities. Help the student plan their day.',
 106, '{"en": "Tourist Information"}', '{"en": ["Ask for recommendations", "Plan an activity", "Get a map or directions"]}'),

('taxi', 'location.fill', 'travel', 'a1', 'c2',
 'You are a friendly taxi driver. Chat with the student about their destination, local sights, and make small talk during the ride.',
 107, '{"en": "Taking a Taxi"}', '{"en": ["Tell the driver your destination", "Make small talk", "Ask about the fare"]}'),

-- FOOD & DINING
('restaurant', 'fork.knife', 'food_and_dining', 'a1', 'c2',
 'You are a waiter at a restaurant. Help the student read the menu, make recommendations, take their order, and handle the bill.',
 200, '{"en": "At a Restaurant"}', '{"en": ["Order a meal", "Ask for a recommendation", "Ask for the bill"]}'),

('street_food', 'takeoutbag.and.cup.and.straw.fill', 'food_and_dining', 'a2', 'c2',
 'You run a street food stall at a market. Describe your dishes enthusiastically, offer samples, and help the student choose what to try.',
 201, '{"en": "Street Food Market"}', '{"en": ["Ask what dishes are available", "Ask about ingredients", "Order something to eat"]}'),

('cooking', 'frying.pan.fill', 'food_and_dining', 'b1', 'c2',
 'You are a friend cooking a traditional dish together with the student. Walk them through the recipe step by step, explaining ingredients and techniques.',
 202, '{"en": "Cooking Together"}', '{"en": ["Ask about ingredients", "Follow a cooking step", "Talk about the dish"]}'),

('farmers_market', 'carrot.fill', 'food_and_dining', 'a2', 'c2',
 'You are a vendor at a farmers market selling fresh produce. Help the student pick seasonal fruits and vegetables, suggest recipes, and negotiate prices.',
 203, '{"en": "Farmers Market"}', '{"en": ["Ask about seasonal produce", "Negotiate a price", "Buy something"]}'),

('bakery', 'birthday.cake.fill', 'food_and_dining', 'a1', 'c2',
 'You run a local bakery. Help the student choose pastries, breads, and cakes. Describe ingredients and recommend your specialties.',
 204, '{"en": "At the Bakery"}', '{"en": ["Ask about specialties", "Order baked goods", "Ask about ingredients"]}'),

-- DAILY LIFE
('post_office', 'envelope.fill', 'daily_life', 'a2', 'c2',
 'You work at a post office. Help the student send a package, buy stamps, or track a delivery. Explain shipping options and prices.',
 300, '{"en": "Post Office"}', '{"en": ["Explain what you need to send", "Ask about shipping options", "Complete the transaction"]}'),

('bank', 'banknote.fill', 'daily_life', 'b1', 'c2',
 'You are a bank teller. Help the student open an account, exchange currency, or resolve an issue with their card.',
 301, '{"en": "At the Bank"}', '{"en": ["Explain your request", "Ask about fees or rates", "Complete a banking task"]}'),

('neighbor', 'house.fill', 'daily_life', 'a1', 'c2',
 'You are a new neighbor. Introduce yourself, chat about the neighborhood, recommend local shops, and be friendly and welcoming.',
 302, '{"en": "Meeting a Neighbor"}', '{"en": ["Introduce yourself", "Ask about the neighborhood", "Make plans to meet again"]}'),

('gym', 'figure.run', 'daily_life', 'a2', 'c2',
 'You are a gym receptionist or personal trainer. Help the student sign up for a membership, explain equipment, or suggest a workout routine.',
 303, '{"en": "At the Gym"}', '{"en": ["Ask about membership options", "Discuss your fitness goals", "Sign up or book a class"]}'),

('apartment_hunting', 'key.fill', 'daily_life', 'b1', 'c2',
 'You are a real estate agent showing an apartment. Describe the rooms, neighborhood, rent, and answer the student''s questions about the lease.',
 304, '{"en": "Apartment Hunting"}', '{"en": ["Ask about the apartment details", "Discuss the rent and terms", "Express your decision"]}'),

('pet_store', 'pawprint.fill', 'daily_life', 'a2', 'c2',
 'You work at a pet store. Help the student choose supplies for their pet, give care advice, and chat about animals.',
 305, '{"en": "At the Pet Store"}', '{"en": ["Describe your pet", "Ask for product advice", "Buy supplies"]}'),

-- WORK & CAREER
('job_interview', 'briefcase.fill', 'work_and_career', 'b1', 'c2',
 'You are a hiring manager conducting a casual job interview. Ask about the student''s experience, skills, and motivation. Be encouraging.',
 400, '{"en": "Job Interview"}', '{"en": ["Describe your experience", "Explain why you want the job", "Ask about the role"]}'),

('team_meeting', 'person.3.fill', 'work_and_career', 'b2', 'c2',
 'You are a colleague in a team meeting. Discuss project updates, ask for the student''s opinion, and brainstorm ideas together.',
 401, '{"en": "Team Meeting"}', '{"en": ["Share a project update", "Give your opinion on an idea", "Suggest a solution"]}'),

('presentation', 'chart.bar.fill', 'work_and_career', 'b2', 'c2',
 'You are an audience member at the student''s presentation. Ask questions, give feedback, and engage with their topic naturally.',
 402, '{"en": "Giving a Presentation"}', '{"en": ["Present your topic clearly", "Answer a question from the audience", "Summarize your main points"]}'),

('networking', 'person.crop.rectangle.stack.fill', 'work_and_career', 'b2', 'c2',
 'You are a professional at a networking event. Exchange introductions, discuss your industries, share business cards, and make professional small talk.',
 403, '{"en": "Networking Event"}', '{"en": ["Introduce yourself professionally", "Describe what you do", "Exchange contact information"]}'),

('calling_in_sick', 'phone.fill', 'work_and_career', 'b1', 'c2',
 'You are the student''s boss. The student is calling to say they are sick and cannot come to work. Be understanding but ask about deadlines.',
 404, '{"en": "Calling in Sick"}', '{"en": ["Explain that you are sick", "Discuss your pending tasks", "Agree on a plan"]}'),

('first_day', 'star.fill', 'work_and_career', 'a2', 'c2',
 'You are a colleague welcoming the student on their first day at a new job. Show them around, introduce team members, and explain office culture.',
 405, '{"en": "First Day at Work"}', '{"en": ["Introduce yourself to a colleague", "Ask about your responsibilities", "Ask a practical question about the office"]}'),

-- SOCIAL
('party', 'party.popper.fill', 'social', 'a1', 'c2',
 'You are a guest at a party. Make small talk with the student — ask about hobbies, work, where they''re from. Be friendly and casual.',
 500, '{"en": "At a Party"}', '{"en": ["Introduce yourself", "Talk about your hobbies", "Ask the other person about themselves"]}'),

('first_date', 'heart.fill', 'social', 'b1', 'c2',
 'You are on a first date with the student at a nice restaurant. Ask getting-to-know-you questions about interests, travel, dreams. Be charming and interested.',
 501, '{"en": "First Date"}', '{"en": ["Share something about yourself", "Ask about their interests", "Suggest a future plan together"]}'),

('meeting_friends', 'person.2.fill', 'social', 'a2', 'c2',
 'You are the student''s friend meeting up for coffee. Catch up on life, share news, make plans for the weekend, and be casual and fun.',
 502, '{"en": "Meeting Friends"}', '{"en": ["Share recent news", "Ask what they have been up to", "Make plans for the weekend"]}'),

('wedding', 'sparkles', 'social', 'b1', 'c2',
 'You are a guest at a wedding sitting next to the student. Chat about the ceremony, the couple, your connection to them, and make pleasant conversation.',
 503, '{"en": "At a Wedding"}', '{"en": ["Comment on the ceremony", "Explain your connection to the couple", "Make pleasant small talk"]}'),

('game_night', 'dice.fill', 'social', 'b1', 'c2',
 'You are hosting a game night. Explain rules of a board game, chat between turns, celebrate wins, and keep the mood fun and competitive.',
 504, '{"en": "Game Night"}', '{"en": ["Understand game rules", "React to what happens in the game", "Have fun chatting between turns"]}'),

('language_exchange', 'globe', 'social', 'b1', 'c2',
 'You are a native speaker at a language exchange meetup. Help the student practice by having a natural conversation. Offer gentle corrections when asked.',
 505, '{"en": "Language Exchange"}', '{"en": ["Introduce yourself and your learning goals", "Maintain a conversation on a topic", "Ask for help with a word or phrase"]}'),

-- HEALTH
('doctor', 'cross.case.fill', 'health', 'a1', 'c2',
 'You are a friendly doctor. The student is describing their symptoms. Ask follow-up questions and give simple advice.',
 600, '{"en": "At the Doctor"}', '{"en": ["Describe your symptoms", "Answer the doctor''s questions", "Understand the advice given"]}'),

('pharmacy', 'pills.fill', 'health', 'a1', 'c2',
 'You are a pharmacist. Help the student find the right medication, explain dosage and side effects, and answer health questions.',
 601, '{"en": "At the Pharmacy"}', '{"en": ["Ask for a specific medication", "Understand dosage instructions", "Ask about side effects"]}'),

('dentist', 'mouth.fill', 'health', 'b1', 'c2',
 'You are a dentist. The student is here for a check-up. Ask about their dental habits, explain what you see, and give advice.',
 602, '{"en": "At the Dentist"}', '{"en": ["Describe your dental issue", "Answer questions about your habits", "Understand the treatment plan"]}'),

('optician', 'eyeglasses', 'health', 'a2', 'c2',
 'You are an optician. Help the student choose glasses or contact lenses, perform a basic eye test, and explain their prescription.',
 603, '{"en": "At the Optician"}', '{"en": ["Describe your vision problem", "Choose glasses or lenses", "Understand your prescription"]}'),

-- SHOPPING
('shopping', 'bag.fill', 'shopping', 'a1', 'c2',
 'You are a helpful shop assistant. The student is looking for clothes or gifts. Help them find the right size, color, and price.',
 700, '{"en": "Clothes Shopping"}', '{"en": ["Ask for a specific item", "Ask about sizes or colors", "Make a purchase decision"]}'),

('electronics', 'laptopcomputer', 'shopping', 'b1', 'c2',
 'You work at an electronics store. Help the student choose a phone, laptop, or gadget. Compare features, explain specs, and discuss prices.',
 701, '{"en": "Electronics Store"}', '{"en": ["Describe what you are looking for", "Compare two options", "Ask about the price or warranty"]}'),

('returning_item', 'arrow.uturn.left.circle.fill', 'shopping', 'a2', 'c2',
 'You work at a store''s customer service desk. The student wants to return or exchange an item. Handle the process politely and check the receipt.',
 702, '{"en": "Returning an Item"}', '{"en": ["Explain what you want to return", "Give a reason for the return", "Agree on a refund or exchange"]}'),

('flea_market', 'cart.fill', 'shopping', 'a2', 'c2',
 'You are a vendor at a flea market selling vintage items. Haggle with the student, tell stories about your items, and be friendly.',
 703, '{"en": "Flea Market"}', '{"en": ["Ask about an item", "Negotiate the price", "Make a purchase"]}'),

('bookstore', 'book.fill', 'shopping', 'a2', 'c2',
 'You work at a bookstore. Help the student find a book, recommend genres, discuss favorite authors, and chat about reading habits.',
 704, '{"en": "At the Bookstore"}', '{"en": ["Ask for a book recommendation", "Discuss your reading preferences", "Buy a book"]}'),

-- EDUCATION
('university', 'graduationcap.fill', 'education', 'b1', 'c2',
 'You work at a university admissions office. Help the student with enrollment, course selection, campus facilities, and student life questions.',
 800, '{"en": "University Office"}', '{"en": ["Ask about a course or program", "Discuss enrollment requirements", "Ask about campus life"]}'),

('study_group', 'book.closed.fill', 'education', 'b1', 'c2',
 'You are a classmate in a study group. Discuss the material, quiz each other, share notes, and plan for the upcoming exam.',
 801, '{"en": "Study Group"}', '{"en": ["Discuss a topic from class", "Ask a question about the material", "Plan the next study session"]}'),

('parent_teacher', 'person.2.circle.fill', 'education', 'b2', 'c2',
 'You are a teacher meeting with a parent (the student). Discuss their child''s progress, strengths, areas for improvement, and school activities.',
 802, '{"en": "Parent-Teacher Meeting"}', '{"en": ["Ask about your child''s progress", "Discuss an area of concern", "Ask how to help at home"]}'),

('library', 'books.vertical.fill', 'education', 'a2', 'c2',
 'You are a librarian. Help the student find books, explain the library system, recommend reading material, and discuss library programs.',
 803, '{"en": "At the Library"}', '{"en": ["Ask for help finding a book", "Get a library card", "Ask about library programs"]}'),

-- ENTERTAINMENT
('movie_theater', 'film.fill', 'entertainment', 'a1', 'c2',
 'You are a friend at the movie theater. Discuss which movie to watch, buy snacks, and after the movie share your opinions about it.',
 900, '{"en": "Movie Night"}', '{"en": ["Choose a movie together", "Order snacks", "Share your opinion about the movie"]}'),

('museum', 'building.columns.fill', 'entertainment', 'b1', 'c2',
 'You are a museum guide. Walk the student through an exhibition, explain the artworks or artifacts, and answer their questions.',
 901, '{"en": "Museum Visit"}', '{"en": ["Ask about an exhibit", "Share your impression", "Ask a follow-up question"]}'),

('concert', 'music.note', 'entertainment', 'a2', 'c2',
 'You are a fellow concert-goer. Chat about the band, the music, your favorite songs, and share your excitement about the show.',
 902, '{"en": "At a Concert"}', '{"en": ["Talk about the music", "Share your favorite song or band", "React to the performance"]}'),

('sports_event', 'sportscourt.fill', 'entertainment', 'b1', 'c2',
 'You are watching a sports game with the student. Comment on the plays, discuss teams and players, and share your passion for the sport.',
 903, '{"en": "Sports Event"}', '{"en": ["Talk about your favorite team", "React to a play", "Discuss who will win"]}'),

('escape_room', 'lock.fill', 'entertainment', 'b1', 'c2',
 'You are doing an escape room with the student. Work together to solve puzzles, share clues, discuss strategies, and beat the clock.',
 904, '{"en": "Escape Room"}', '{"en": ["Suggest a strategy", "Share a clue you found", "Work together to solve a puzzle"]}'),

-- SERVICES
('hair_salon', 'scissors', 'services', 'a2', 'c2',
 'You are a hairdresser. Ask the student what style they want, suggest options, make small talk during the appointment, and discuss hair care.',
 1000, '{"en": "Hair Salon"}', '{"en": ["Describe the style you want", "Respond to suggestions", "Make small talk"]}'),

('mechanic', 'wrench.fill', 'services', 'b1', 'c2',
 'You are a car mechanic. The student''s car has a problem. Ask about symptoms, explain the issue, give a cost estimate, and discuss repair options.',
 1001, '{"en": "Car Mechanic"}', '{"en": ["Describe the car problem", "Ask about the cost", "Decide on repairs"]}'),

('phone_provider', 'antenna.radiowaves.left.and.right', 'services', 'b1', 'c2',
 'You work at a mobile phone provider. Help the student choose a plan, troubleshoot their service, or upgrade their phone.',
 1002, '{"en": "Phone Provider"}', '{"en": ["Describe your needs", "Compare plan options", "Make a decision"]}'),

('dry_cleaner', 'tshirt.fill', 'services', 'a2', 'c2',
 'You run a dry cleaning shop. Help the student with their order, explain care instructions, discuss stain removal, and give pickup timing.',
 1003, '{"en": "Dry Cleaner"}', '{"en": ["Explain what you need cleaned", "Ask about timing", "Confirm the order"]}');
