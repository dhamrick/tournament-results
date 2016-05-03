#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import sys


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection.
    and a cursor object and raises eceptions if the connection cannot be made.
    """
    try:
        conn = psycopg2.connect("dbname=tournament")
    except psycopg2.DatabaseError:
        print "The program could not connect to the database!"
        sys.exit(1)
    except psycopg2.InterfaceError:
        print ("The program could not connect to the database because of "\
               "a connection.")
        sys.exit(1)
    else:
        cursor = conn.cursor()
        return conn, cursor

def commit_and_close(conn, cursor):
    """Commits all changes from the session and closes connections

    Args:
        conn: The database connection
        cursor: The cursor object
    """
    conn.commit()
    cursor.close()
    conn.close()

def create_tournament(name):
    """Adds a new tournament to the tournaments table.

    The database assigns a unique I.D. and adds a timestamp of when the
    tournament was created.

    Arg:
        name: The name of the tournament.
    """
    conn, cursor = connect()
    cursor.execute("INSERT INTO tournaments (name) VALUES (%s)", (name,))
    commit_and_close(conn, cursor)

def deleteMatches(*tournament_id):
    """Remove all the matches for the specified tournament.

    Will remove the matches and set the wins and matches data from the
    tournament_data table to the default value of 0 for all players in
    that tournament.

    ARGS:
        tournament_id (optional): If omitted, then chages will be made to
        the current tournament.  Otherwise the specified tournment will
        be updated.
        """
    conn, cursor = connect()
    if not tournament_id:
        cursor.execute("DELETE FROM matches \
                       WHERE tournament_id = %s", (get_current_tournament(),))
        cursor.execute("UPDATE tournament_data \
                       SET matches = DEFAULT, wins = DEFAULT \
                       WHERE tournament_id = %s", (get_current_tournament(),))
    else:
        cursor.execute("DELETE FROM matches \
                       WHERE tournament_id = %s", (tournament_id,))
        cursor.execute("UPDATE tournament_data \
                       SET matches = DEFAULT, wins = DEFAULT \
                       WHERE tournament_id = %s", (tournament_id,))
    commit_and_close(conn, cursor)

def deletePlayers(player_id, *tournament_id):
    """Removes player records from specified tournaments

    Depending on the arguments, this fucntion can remove a player's info
    from a certain tournament, all player info for a certain tournament,
    or a player's data from all tournaments and change their active status
    to 'no'.

    ARGS:
        player_id: If set to 'ALL', then all records for the
        specified tournament are deleted.  If it is a player_id,
        then only the that player's reords are deleted.
        *tournament_id: If omitted, then only the latest tournament's data
        will be edited.  If the value is 'ALL', then all data for specified
        player will be deleted from all tournaments and players.active
        will be set to 'no'.  Otherwise, only the specified tournament's
        data will be updated.
    """
    conn, cursor = connect()
    if not tournament_id:
        """IF tournament_id is omitted, will check player_id and then
        delete the correct entries.
        """
        if player_id is 'ALL':
            cursor.execute("DELETE FROM tournament_data \
                           WHERE tournament_id = %s", (get_current_tournament(),))
        else:
            cursor.execute("DELETE FROM tournament_data \
                           WHERE tournament_id = %s AND player_id = %s",
                           (get_current_tournament(), player_id))
    elif tournament is 'ALL':
        """Checks if tournament_id is set to 'ALL' and then deletes the
        correct entries and updates players.active"""
        if player_id is 'ALL':
            cursor.execute("DELETE FROM tournament_data")
            cursor.execute("UPDATE players \
                           SET active = 'no'")
        else:
            cursor.execute("DELETE FROM tournament_data \
                           WHERE player_id = %s", (player_id,))
            cursor.execute("UPDATE players \
                           SET active = 'no' \
                           WHERE player_id = %s", (player_id,))
    else:
        cursor.execute("DELETE FROM tournament_data \
                       WHERE player_id = %s", (player_id,))
    commit_and_close(conn, cursor)

def countPlayers(*tournament_id):
    """Returns the number of players.

    Depending on the arguments, this can return the roster for a specific
    tournament or the total count of all active registered players regardless
    of their tournament participation.

    ARGS:
        tournament_id (optional): IF omitted, will return the registration
        for the current tournament.  IF set to 'ALL', then will return
        the total count of active players.  Otherwise will return the
        registration for the specified tournament.
    """
    conn, cursor = connect()
    if not tournament_id:
        cursor.execute("SELECT count(player_id) FROM tournament_data \
                       WHERE tournament_id = %s", (get_current_tournament(),))
        player_count = cursor.fetchone()
    elif tournament_id is 'ALL':
        cursor.execute("SELECT count(player_id) FROM players \
                       WHERE active = 'yes'")
        player_count = cursor.fetchone()
    else:
        cursor.execute("SELECT count(player_id) FROM tournament_data \
                       WHERE tournament_id = %s", (tournament_id,))
        player_count = cursor.fetchone()
    player_count = player_count[0]
    commit_and_close(conn, cursor)
    return player_count

def registerPlayer(name, email_address):
    """Adds a player to players table and current tournament.

    If the player is already registered, but marked as inactive, then
    this will set players.active to 'yes' (based on email-address),
    otherwise the player is added to the player's table.  The player is
    then added to the current tournament.

    Args:
      name: the player's full name (need not be unique)
      email_address: the player's email address (must be unique)
    """
    conn, cursor = connect()
    cursor.execute("SELECT (player_id, active) FROM players \
                   WHERE email = %s", (email_address,))
    already_registered = cursor.fetchone()
    if already_registered is None:
        """IF the player's email address is not already in the players
        table, then the player is added to players and the current tourney.
        """
        cursor.execute("INSERT INTO players (name, email) \
                       VALUES (%s, %s)", (name, email_address))
        conn.commit()
        cursor.execute("SELECT * FROM last_registered_player")
        newest_player = cursor.fetchone()
        newest_player = newest_player[0]
        register_tournament_player(newest_player)
    else:
        player_id = already_registered[0]
        player_active = already_registered[1]
        if player_active is 'no':
            """IF the player is in the players table already, but inactive,
            then the player is set to active and registered to the current
            tourney.
            """
            cursor.execute("UPDATE players \
                           SET active = 'yes' \
                           WHERE player_id = %s", (player_id,))
            register_tournament_player(player_id)
        else:
            register_tournament_player(player_id)
    commit_and_close(conn, cursor)

def register_tournament_player(player_id):
    """Adds a registered player to the current tournament.

    Requires player to already be registered in the players table and
    that a tournament has already been crated in the tournaments table.
    Adds player into the tournament_data table for the current tournament
    and initializes the win/loss records to 0.

    ARGS:
        player_id: The player_id for the player being registered.
    """
    conn, cursor = connect()
    cursor.execute("INSERT INTO tournament_data (tournament_id, player_id) \
                   VALUES (%s, %s)", (get_current_tournament(), player_id))
    commit_and_close(conn, cursor)

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins
    in decending order.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn, cursor = connect()
    cursor.execute("SELECT * \
                   FROM player_standings \
                   ORDER BY wins DESC")
    player_data = cursor.fetchall()
    commit_and_close(conn, cursor)
    return player_data

def reportMatch(winner, loser):
    """Records the outcome of a match in the current tournament.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn, cursor = connect()
    cursor.execute("UPDATE tournament_data \
                        SET wins = wins + 1 \
                        WHERE player_id = %s \
                        AND tournament_id = %s",
                        (winner, get_current_tournament()))
    cursor.execute("UPDATE tournament_data \
                        SET matches = matches + 1 \
                        WHERE (player_id = %s OR player_id = %s) \
                        AND tournament_id = %s",
                        (winner, loser, get_current_tournament()))
    commit_and_close(conn, cursor)

def get_current_tournament():
    """Returns the tournament_id for the current tournament"""

    conn, cursor = connect()
    cursor.execute("SELECT * FROM current_tournament")
    current_tourney = cursor.fetchone()
    current_tourney = current_tourney[0]
    return current_tourney

def swissPairings():
    """Creates the set of matches and returns the list and records the matches
    to the mathes table for the current tournament.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    conn, cursor = connect()
    player_data = playerStandings()
    match_ups = []
    rank = 0
    while rank < (len(player_data)):
        match = (player_data[rank][0], player_data[rank][1],
                 player_data[rank + 1][0], player_data[rank + 1][1])
        match_ups.append(match)
        cursor.execute("INSERT INTO matches (tournament_id, player_1, player_2)"
                       "VALUES (%s, %s, %s)",
                       (get_current_tournament(),match[0], match[2]))
        rank += 2
    commit_and_close(conn, cursor)
    return match_ups




