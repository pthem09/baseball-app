from django.shortcuts import render
from balldontlie import BalldontlieAPI

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
