from django.shortcuts import render
from balldontlie import BalldontlieAPI
from datetime import datetime

api = BalldontlieAPI(api_key="24cfe1d1-3f67-4778-8c53-fbb8e77e2016")
teams = api.mlb.teams.list()


def index(request):
    if request.method == 'GET' and 'team' in request.GET:
        id = request.GET['team']
    else:
        id = 1

    cursor = request.GET.get('cursor')
    direction = request.GET.get('direction')

    if 'cursors' not in request.session:
        request.session['cursors'] = []
        request.session.modified = True

    if direction == 'prev':
        if request.session['cursors']:
            request.session['cursors'].pop()
            request.session.modified = True
            if request.session['prev_cursor']:
                players = api.mlb.players.list(
                    team_ids=[id],
                    cursor=request.session['prev_cursor']
                )
            else:
                players = api.mlb.players.list(
                    team_ids=[id]
                )
            if len(request.session['cursors']) > 1:
                request.session['prev_cursor'] = request.session['cursors'][-2]
                request.session.modified = True
            else:
                request.session['prev_cursor'] = None
                request.session.modified = True
        else:
            players = api.mlb.players.list(team_ids=[id])
    else:
        if cursor:
            request.session['cursors'].append(cursor)
            request.session.modified = True
            if len(request.session['cursors']) > 1:
                request.session['prev_cursor'] = request.session['cursors'][-2]
            else:
                request.session['prev_cursor'] = None
            request.session.modified = True
            players = api.mlb.players.list(team_ids=[id], cursor=cursor)
        else:
            players = api.mlb.players.list(team_ids=[id])
            request.session['cursors'] = []
            request.session.modified = True

    if hasattr(players.meta, 'next_cursor'):
        next_cursor = players.meta.next_cursor
    else:
        next_cursor = None

    selected_team = api.mlb.teams.get(id)
    request.session.modified = True

    context = {
        'teams': teams,
        'players': players,
        'selected_team': selected_team,
        'team_id': selected_team.data.id,
        'next_cursor': next_cursor,
        'prev_cursor': request.session['prev_cursor'],
    }

    return render(request, 'stats/template.html', context)


def player(request):
    player_id = request.GET.get('player')
    player = api.mlb.players.get(player_id)
    dob_time = datetime.strptime(player.data.dob, "%d/%m/%Y")
    if player.data.debut_year:
        debut_yr = int(player.data.debut_year)
    else:
        debut_yr = 'n/a'
    day = dob_time.strftime("%A")
    month_name = str(dob_time.strftime("%B"))
    day_num = str(int(dob_time.strftime("%d")))
    yr_num = str(dob_time.strftime("%Y"))
    dob_formatted = day + ', ' + month_name + ' ' + day_num + ', ' + yr_num
    context = {
        'player': player,
        'dob_formatted': dob_formatted,
        'debut_yr_int': debut_yr,
        'bats': player.data.bats_throws.split("/")[0],
        'throws': player.data.bats_throws.split("/")[1],
    }
    return render(request, 'stats/player.html', context)
