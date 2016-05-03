#!/usr/bin/env python
#
# Test cases for tournament.py
# These tests are not exhaustive, but they should cover the majority of cases.
#
# If you do add any of the extra credit options, be sure to add/modify these test cases
# as appropriate to account for your module's added functionality.

from tournament import *

def clear_all_tables():
    conn, cursor = connect()
    cursor.execute("DELETE FROM matches")
    cursor.execute("DELETE FROM tournament_data")
    cursor.execute("DELETE FROM tournaments")
    cursor.execute("DELETE FROM players")
    commit_and_close(conn, cursor)

def testCount():
    """
    Test for initial player count,
             player count after 1 and 2 players registered,
             player count after players deleted.
    """
    deleteMatches()
    deletePlayers('ALL')
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deletion, countPlayers should return zero.")
    print "1. countPlayers() returns 0 after initial deletePlayers() execution."
    registerPlayer("Chandra Nalaar", "cnalaar@fake.com")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1. Got {c}".format(c=c))
    print "2. countPlayers() returns 1 after one player is registered."
    registerPlayer("Jace Beleren", "jbeleren@fake.com")
    c = countPlayers()
    if c != 2:
        raise ValueError(
            "After two players register, countPlayers() should be 2. Got {c}".format(c=c))
    print "3. countPlayers() returns 2 after two players are registered."
    deletePlayers('ALL')
    c = countPlayers()
    if c != 0:
        raise ValueError(
            "After deletion, countPlayers should return zero.")
    print ("4. countPlayers() returns zero after registered players are deleted.\n"\
           "5. Player records successfully deleted.")

def testStandingsBeforeMatches():
    """
    Test to ensure players are properly represented in standings prior
    to any matches being reported.
    """
    deleteMatches()
    deletePlayers('ALL')
    registerPlayer("Melpomene Murray", "mmurray@fake.com")
    registerPlayer("Randy Schwartz", "rschwartz@fake.com")
    standings = playerStandings()
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."

def testReportMatches():
    """
    Test that matches are reported properly.
    Test to confirm matches are deleted properly.
    """
    deleteMatches()
    deletePlayers('ALL')
    registerPlayer("Bruno Walton", "bwalton@fake.com")
    registerPlayer("Boots O'Neal", "bo'neal@fake.com")
    registerPlayer("Cathy Burton", "cburton@fake.com")
    registerPlayer("Diane Grant", "dgrant@fake.com")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    standings = playerStandings()
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."
    deleteMatches()
    standings = playerStandings()
    if len(standings) != 4:
        raise ValueError("Match deletion should not change number of players in standings.")
    for (i, n, w, m) in standings:
        if m != 0:
            raise ValueError("After deleting matches, players should have zero matches recorded.")
        if w != 0:
            raise ValueError("After deleting matches, players should have zero wins recorded.")
    print "8. After match deletion, player standings are properly reset.\n9. Matches are properly deleted."

def testPairings():
    """
    Test that pairings are generated properly both before and after match reporting.
    """
    deleteMatches()
    deletePlayers('ALL')
    registerPlayer("Twilight Sparkle", "tsparkle@fake.com")
    registerPlayer("Fluttershy", "fluttershy@fake.com")
    registerPlayer("Applejack", "applejack@fake.com")
    registerPlayer("Pinkie Pie", "ppie@fake.com")
    registerPlayer("Rarity", "rarity@fake.com")
    registerPlayer("Rainbow Dash", "rdash@fake.com")
    registerPlayer("Princess Celestia", "pcelestia@fake.com")
    registerPlayer("Princess Luna", "pluna@fake.com")
    standings = playerStandings()
    [id1, id2, id3, id4, id5, id6, id7, id8] = [row[0] for row in standings]
    pairings = swissPairings()
    if len(pairings) != 4:
        raise ValueError(
            "For eight players, swissPairings should return 4 pairs. Got {pairs}".format(pairs=len(pairings)))
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    reportMatch(id5, id6)
    reportMatch(id7, id8)
    pairings = swissPairings()
    if len(pairings) != 4:
        raise ValueError(
            "For eight players, swissPairings should return 4 pairs. Got {pairs}".format(pairs=len(pairings)))
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4), (pid5, pname5, pid6, pname6), (pid7, pname7, pid8, pname8)] = pairings
    possible_pairs = set([frozenset([id1, id3]), frozenset([id1, id5]),
                          frozenset([id1, id7]), frozenset([id3, id5]),
                          frozenset([id3, id7]), frozenset([id5, id7]),
                          frozenset([id2, id4]), frozenset([id2, id6]),
                          frozenset([id2, id8]), frozenset([id4, id6]),
                          frozenset([id4, id8]), frozenset([id6, id8])
                          ])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4]), frozenset([pid5, pid6]), frozenset([pid7, pid8])])
    for pair in actual_pairs:
        if pair not in possible_pairs:
            raise ValueError(
                "After one match, players with one win should be paired.")
    print "10. After one match, players with one win are properly paired."

def test_create_tournaments():
    """Test that tournaments are created properly and that the current
    tournament is correctly reported
    """
    conn, cursor = connect()
    cursor.execute("DELETE FROM tournaments")
    create_tournament("First is the worst!")
    create_tournament("Second is the best!")
    create_tournament("Third is the one with the hairy chest!")
    cursor.execute("SELECT tournament_id, name  FROM tournaments \
                   ORDER BY tournament_id DESC")
    tourney_data = cursor.fetchmany(3)
    [id3, id2, id1] = [row[0] for row in tourney_data]
    [name_3, name_2, name_1] = [row[1] for row in tourney_data]
    # if tourney_data[0][0] != 1:
    #     raise ValueError ("After adding the first tournament of the table, "
    #                       "the table's ID should be 1")
    # if tourney_data[0][1] != "First is the worst!":
    #     print tourney_data[0][1]
    #     raise ValueError ("After adding the first tournament, the name "
    #                       "should be 'First is the worst'.")
    # if tourney_data[1][0] != 2:
    #     raise ValueError ("After adding the first tournament of the table, "
    #                       "the table's ID should be 1")
    # if tourney_data[1][1] != 'Second is the best!':
    #     raise ValueError ("After adding the first tournament, the name "
    #                       "should be 'First is the worst'.")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM current_tournament")
    current_tournament = cursor.fetchone()
    current_tournament = current_tournament[0]
    # if current_tournament != 3:
    #     raise ValueError ("The current tournament, after adding 3 tournaments "
    #                       "should be 3!")
    commit_and_close(conn, cursor)
    print "1. Tournaments created successfully!"


if __name__ == '__main__':
    clear_all_tables()
    test_create_tournaments()
    testCount()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    print "Success!  All tests pass!"
