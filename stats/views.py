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
    if cursor:
        players = api.mlb.players.list(team_ids=[id], cursor=cursor)
    else:
        players = api.mlb.players.list(team_ids=[id])
    selected_team = api.mlb.teams.get(id)
    context = {
        'teams': teams,
        'players': players,
        'selected_team': selected_team,
        'next_cursor': players.meta.next_cursor,
    }
    return render(request, 'stats/template.html', context)
