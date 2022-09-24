from ast import Not
from dataclasses import dataclass
import json
from this import d
from typing import final
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
import requests
from django.views.decorators.csrf import csrf_protect
from django.utils.safestring import SafeString

from .models import GithubUser


def main(request):
    return render(request, "index.html",)


@csrf_protect
def addCandidateToDB(request):
    if request.method == 'POST':
        values = request.POST.dict()
        try:
            GithubUser.objects.update_or_create(**values)
            return HttpResponse(request.POST['name'] + " added in to Listed Candidates!")
        except Exception as error:
            return HttpResponse("An Error Occured: " + str(error))
    else:
        return HttpResponse("An Error Occured: " + str(error))


@csrf_protect
def deleteCandidateFromDB(request, GithubUser_userName):
    try:
        deletedUser = GithubUser.objects.filter(
            userName=GithubUser_userName)
        deletedUser.delete()
        return redirect('../listedCandidates')
    except Exception as error:
        return HttpResponse("An Error Occured: " + str(error))


def listCandidates(request):
    electedUsers = {"storedUsers": GithubUser.objects.all()}
    return render(request, "listedCandidates.html", electedUsers)


# I found it out that github has an grapQL api for developers to fetch relevant informations from them.
# Helpful links: https://www.youtube.com/watch?v=B9PwBp_V0WA&ab_channel=DevSense
# https://docs.github.com/en/graphql/overview/explorer
def _fetchAvaliableCandidatesFromGithub(searchedKeyword):
    # AUMENTAR TAMANO DE DATOS, EXTRAER TODO
    variables = {"searchedKeyword": searchedKeyword + " repos:>0"}
    query = """
    query($searchedKeyword : String!)
    {
        search(query: $searchedKeyword, type:USER, first: 50)
        {
            nodes
            {
                ... on User
                {
                    login,
                    name,
                    avatarUrl,
                    bio,
                    email,
                    location,
                    company,
                    websiteUrl
                    followers(first: 0)
                    {
                        totalCount
                    }
                        repositories(first: 100)
                    {
                        totalCount,
                        nodes
                        {
                            ... on Repository
                            {
                                stargazerCount,
                                forkCount
                                primaryLanguage
                                {
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """

    header = {'Authorization': "bearer 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",
              'content-type': 'application/json'}
    body = {'query': query, 'variables': variables}
    response = requests.post(
        'https://api.github.com/graphql', json=body, headers=header)
    if response.status_code == 200:
        return response.json()
    else:
        return {}


def fetchDataFromGithub(request):
    prefferedLanguages = {}
    result = []
    queryText = request.GET.get('query')
    if queryText is not None and len(queryText) != 0:
        response = _fetchAvaliableCandidatesFromGithub(queryText).get("data")
        filteredUsers = response.get("search")
        filteredUsersNodes = filteredUsers.get("nodes")
        talentedDevelopersArray = filteredUsersNodes
        iterator = 0
        # check whether user already in our DB.
        while iterator < len(talentedDevelopersArray):
            currentCandidate = talentedDevelopersArray[iterator]
            candidateInformations = {
                "userName": currentCandidate.get("login"),
                "name": currentCandidate.get("name").replace('\'', "") if currentCandidate.get("name") is not None else '',
                "email": currentCandidate.get("email") if currentCandidate.get("email") is not None else 'No email',
                "websiteUrl": currentCandidate.get("websiteUrl") if currentCandidate.get("websiteUrl") is not None else 'No Website',
                "location": currentCandidate.get("location").replace('\'', "") if currentCandidate.get("location") is not None else 'No Location',
                "company": currentCandidate.get("company").replace('\'', "") if currentCandidate.get("company") is not None else 'No company',
                "bio": currentCandidate.get("bio").replace('\'', "") if currentCandidate.get("bio") is not None else 'No Bio',
                "avatarUrl": currentCandidate.get("avatarUrl") if currentCandidate.get("avatarUrl") is not None else '',
                "followersCount": currentCandidate.get(
                    "followers").get("totalCount") if currentCandidate.get("followers") is not None else 0,
                "repositoriesCount": currentCandidate.get(
                    "repositories").get("totalCount") if currentCandidate.get("repositories") is not None else 0,

                "forkCount": 0,
                "stargazerCount": 0,
                "mostUsedLanguage": ''
            }

            if currentCandidate.get("repositories") is not None:
                candidateInformations["repositoriesCount"] = currentCandidate.get(
                    "repositories").get("totalCount")
                repositoriesOfCandidate = currentCandidate.get(
                    "repositories").get("nodes")

                for repo in repositoriesOfCandidate:
                    candidateInformations["forkCount"] = repo.get("forkCount") + candidateInformations.get(
                        "forkCount")
                    candidateInformations["stargazerCount"] = repo.get("stargazerCount") + candidateInformations.get(
                        "stargazerCount")

                    primaryLanguage = repo.get("primaryLanguage")
                    if primaryLanguage is not None:
                        primaryLanguage = primaryLanguage.get("name")
                        prefferedLanguages[primaryLanguage] = prefferedLanguages.get(
                            primaryLanguage, 0) + 1

                if (len(prefferedLanguages) > 0):
                    candidateInformations["mostUsedLanguage"] = max(
                        prefferedLanguages, key=prefferedLanguages.get)

                result.append(candidateInformations)
            iterator += 1

        state = {
            "users": result,
            "query": queryText
        }
        return render(request, "fetchDataFromGithub.html", state)

    return render(request, "fetchDataFromGithub.html")
