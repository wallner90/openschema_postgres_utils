INSERT INTO AppUser
(id, username, email, password, role) VALUES (uuid_generate_v4(), 'admin', 'admin@domain.com', 'admin', 'ROLE_ADMIN') ON CONFLICT DO NOTHING;
INSERT INTO AppUser
(id, username, email, password, role) VALUES (uuid_generate_v4(), 'userA', 'A@domain.com', 'none', 'ROLE_USER') ON CONFLICT DO NOTHING;
INSERT INTO AppUser
(id, username, email, password, role) VALUES (uuid_generate_v4(), 'userB', 'B@domain.com', 'none', 'ROLE_USER') ON CONFLICT DO NOTHING;
INSERT INTO AppUser
(id, username, email, password, role) VALUES (uuid_generate_v4(), 'userC', 'C@domain.com', 'none', 'ROLE_USER') ON CONFLICT DO NOTHING;
INSERT INTO AppUser
(id, username, email, password, role) VALUES (uuid_generate_v4(), 'userD', 'D@domain.com', 'none', 'ROLE_USER') ON CONFLICT DO NOTHING;
