Unzip the package to your working directory.

Import tournament.sql into psql using the command '\i tournament.sql'.

You can now create a python program and import the tournament file to
get the following functionality:

connect(): Returns a database connection and a cursor object.  It will
raise excpetions if the connection to the database cannot be made.

commit_and_close(conn, cursor): Commits all changes to the database and
close the cursor object and the database connection.  It takes the
databse connection and the cursor object as arguments.

create_tournament(name): Creates a tournament with the given name.  The
database assigns a unique tournament_id and provides a timestamp at the
time of creation.

deleteMatches(*tournament_id): If argument is omitted, then it will delete
the matches from the current tournament and set the wins and matches data in
the tournament_data table to 0 for all players.  Otherwise it will update
the specified tournament's data in the same manner.

deletePlayers(player_id, *tournament_id): Depending on the arguments,
this fucntion can remove a player's info from a certain tournament, all
player info for a certain tournament, or a player's data from all tournaments
and change their active status to 'no'.

countPlayers(*tournament_id): Return the number of registered players from
either the current tournament (if argument is omitted) or from the specified
tournament.

registerPlayer(name, email_address):  If the player is already registered,
but marked as inactive, then this will set players.active to 'yes'
(based on email-address), otherwise the player is added to the player's
table.  The player is then added to the current tournament.

register_tournament_player(player_id): Requires player to already be
registered in the players table and that a tournament has already been
crated in the tournaments table. Adds player into the tournament_data table
for the current tournament and initializes the win/loss records to 0.

playerStandings(): Return a list of the players and their wins in
descending order (most wins first).  Returns a list of tuples containing
(id, name, wins, matches) for each player in the current tournament.

reportMatch(winner, loser): Records the wins and matches where appropriate.
The arguments are the player ids.

get_current_tournament(): Returns the tournament_id for the current tournament.

swissPairings() will return a list of tuples containing the player id and name
of each player in the match.  Each match is created in such a way that each
opponents are neighbors from the playerStanding() function.  The list of
match_ups is returned and each match is recorded in the matches table.