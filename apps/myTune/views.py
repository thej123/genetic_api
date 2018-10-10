# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
import requests # import requests to make api calls.
import json # to serialize unicode
import random #random generator for the fun part
import bisect #for deciding if beethoven or cat! It is a binary search instead linear search if I try to if statements.

def home(request):
    request.session.clear()
    headers = {"Authorization" : "Bearer demo_oauth_token"} #for authentication
    user_response = requests.get("https://api.23andme.com/3/profile/demo_profile_id/", headers=headers) # making api call and giving authorization through the header
    user = user_response.json() #turning response into iteratable JSON format
    request.session['name'] = user['first_name']
    return render(request, 'myTune/home.html')

def give_score(request):
    headers = {"Authorization" : "Bearer demo_oauth_token"} #for authentication
    markers = ["rs4630083", "rs13146789", "rs4349633", "rs3803"] #all the markers needed

    all_responses = []
    all_responses_formatted = []
    all_alleles = []

    # for loop to make all necessary api calls to get info on all the markers
    for marker in markers:
        all_responses.append(requests.get("https://api.23andme.com/3/profile/demo_profile_id/marker/" + marker , headers=headers))

    # change all the responses into JSON format so that we can iterate through it
    for response in all_responses:
        all_responses_formatted.append(response.json())

    # use get_alleles method to get each markers alleles
    for formatted_response in all_responses_formatted:
        all_alleles.append(get_alleles(formatted_response))

    # sending the alleles to find_music_score method to get a score
    score = find_music_score(all_alleles)
    context = {
        "music_score" : score,
        "your_alleles" : json.dumps(all_alleles),
        "description" : score_description(score), #sending the score to get a description
    }
    return render(request, 'myTune/home.html', context)


# this function will take in the JSON data from the api calls and return a list of variants and thier alleles
def get_alleles(marker):
    
    myAlleles = {}
    variant = marker['id']
    alleleOne = marker['variants'][0]['allele'] # find the allele
    # we know the total number alleles should always be 2
    # so if 2 of the above alleles are there then we dont have to check further
    if marker['variants'][0]['dosage'] == 2:
        myAlleles[variant] = [alleleOne, alleleOne]
        return myAlleles

    alleletwo = marker['variants'][1]['allele']
    if marker['variants'][1]['dosage'] == 2:
        myAlleles[variant] = [alleletwo, alleletwo]
        return myAlleles
    # since this variant has no 2 of the same alleles, we can gather that it has one of each
    else:
        myAlleles[variant] = [alleleOne, alleletwo]
        return myAlleles

# this function will take in a list of variants and alleles and return a muscial score
def find_music_score(the_alleles):

    # the musical weightage dictionary
    musical_weightage = {
        "rs4630083" : {
            "description" : "general musical aptitude",
            "GG" : 2.24,
            "AG" : 1.32,
            "AA" : 0,
        },
        "rs13146789" : {
            "description" : "hearing pitch",
            "TT" : 1.0,
            "TG" : 0.82,
            "GG" : 0,
        },
        "rs4349633" : {
            "description" : "more hearing pitch",
            "AA" : 1.11,
            "AG" : 0,
            "GG" : 0,
        },
        "rs3803" : {
            "description" : "inner ear development",
            "AA" : 0.65,
            "AG" : 0,
            "GG" : 0,
        },
    }

    music_score = 0

    # loop through the list of  - {variants: alleles}
    for variants in the_alleles:
        # iterate through the dictionary
        for key, value in variants.iteritems():
            value_string = ''.join(value) #join the ['A','G'] into 'AG'

            # sometimes alleles may be stored in reverse
            reverse_value_string = value_string[::-1] #get the reverse value_string also i.e 'GA'
            
            #check is variant in the musical_weightage dictionary
            if key in musical_weightage:
                #check is allele combination is in the variant and add it values to the music_score
                if value_string in musical_weightage[key]:
                    music_score += musical_weightage[key][value_string]
                #check is the reverse allele combination is in the variant and add it value
                elif reverse_value_string in musical_weightage[key]:
                    music_score += musical_weightage[key][reverse_value_string]
    
    return music_score

# takes in a music value and returns a music description about the person
def score_description(val):

    descriptions = [
        (1, 'You are a cat walking over a piano'),
        (2, 'You are a noob'),
        (3, 'Platinum Elo noob'),
        (4, 'Diamond Elo noob'),
        (5, 'Almost Bethoven'),
        (6, 'Alright you are Bethoven'),
    ]
    descriptions.sort() # list must be sorted for bisecting
    pos = bisect.bisect_left(descriptions, (val,)) # find the pos of the description that is 'left' of the value range
    return json.dumps(descriptions[pos][1]) #return the only description that is at the position


# uses the random alleles generator to create scores and description - just for fun
def make_my_own(request):
    alleles = random_alleles(request)
    score = find_music_score(alleles)

    context = {
        "music_score" : score,
        "your_alleles" : json.dumps(alleles),
        "description" : score_description(score), #sending the score to get a description
    }  

    return render(request, 'myTune/home.html', context)


# created random alleles - just for fun
def random_alleles(request):

    alleles_list = [[{"rs4630083": ["A", "A"]}, {"rs13146789": ["G", "G"]}, {"rs4349633": ["G", "G"]}, {"rs3803": ["A", "A"]}], [{"rs4630083": ["A", "A"]}, {"rs13146789": ["G", "G"]}, {"rs4349633": ["A", "A"]}, {"rs3803": ["A", "A"]}], [{"rs4630083": ["G", "G"]}, {"rs13146789": ["G", "G"]}, {"rs4349633": ["G", "G"]}, {"rs3803": ["A", "A"]}], [{"rs4630083": ["G", "G"]}, {"rs13146789": ["T", "T"]}, {"rs4349633": ["G", "G"]}, {"rs3803": ["A", "A"]}], [{"rs4630083": ["G", "G"]}, {"rs13146789": ["T", "T"]}, {"rs4349633": ["A", "A"]}, {"rs3803": ["A", "A"]}], [{"rs4630083": ["G", "G"]}, {"rs13146789": ["T", "T"]}, {"rs4349633": ["A", "A"]}, {"rs3803": ["G", "G"]}]]

    index = random.randrange(6)

    if 'random_number' in request.session:
        while request.session['random_number'] == index:
            index = random.randrange(6)

    request.session['random_number'] = index
    
    return alleles_list[index]