DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;

\c tournament

CREATE TABLE players
	-- Creates a table called players to hold the player's name and
	-- whether or not they are currently active.
	(
		player_id serial PRIMARY KEY,
		name text,
		email text,
		active text DEFAULT 'yes',
		UNIQUE (email)
	);

CREATE TABLE tournaments
	-- Creates a table that holds the id and name of each tournament
	(
	 	tournament_id serial PRIMARY KEY,
	 	name text,
	 	date_started timestamp DEFAULT current_timestamp
	);

CREATE TABLE tournament_data
	-- Creates a table to hold tournament data like registered players and
	-- their win/loss records.
	(
	 	tournament_id serial REFERENCES tournaments,
	 	player_id serial REFERENCES players,
	 	wins integer DEFAULT 0,
	 	matches integer DEFAULT 0
	);

CREATE TABLE matches
	-- Creates a table to hold all the matchups from the tournaments
	(
	 	tournament_id serial REFERENCES tournaments,
	 	player_1 serial REFERENCES players(player_id),
	 	player_2 serial REFERENCES players(player_id)
	);

CREATE VIEW current_tournament AS
	SELECT max(tournament_id) FROM tournaments;
	-- Creates a view for the current (latest) tournament_id

CREATE VIEW last_registered_player AS
	SELECT max(player_id) FROM players;

CREATE VIEW player_standings AS
	SELECT players.player_id, players.name, tournament_data.wins, tournament_data.matches
	FROM players JOIN tournament_data
	ON (players.player_id = tournament_data.player_id);








