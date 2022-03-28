# Copyright 2022 Netherlands eScience Center and Vrije Universiteit Amsterdam
# Licensed under the Apache License, version 2.0. See LICENSE for details.

# Extract all named organisations in annual report
# Count the number of times each is mentioned
# Classify relation type:
#   - interne organisatieafhankelijkheid (i.e. daughter or mother company)
#   - financiële relatie
#   - partner (supplies funds, knowledge, goods, people)
#   - marktrelatie (hired to do something)
#   - politiek (is a political bystander or opponent)
# Classify type of organisation:
#   - bedrijf
#   - overheidsinstantie
#   - politieke/belangenorganisatie
#   - NGO
#   - onderwijs-/kennisinstelling
import numpy as np


def count_orgs(text, org):
    ''' Count the number of times an organization is mentioned in a text.'''
    return text.count(org)


def classify_relation_type():
    ''' Classify the relationship between a mentioned organization and the main organization'''
    relation_type = 'none'
    return relation_type


def classify_org_type():
    ''' Classify what kind of organization '''
    org_type = 'none'
    return org_type


def extract_orgs(text, orgs):
    ''' Extract the details of all organizations mentioned in text'''
    orgs_details = np.empty(len(orgs), dtype='U200')
    for i, org in enumerate(orgs):
        org_count = count_orgs(text, org)
        rel_type = classify_relation_type()
        org_type = classify_org_type()
        orgs_details[i] = (str(org) + ' - ' + str(org_count) + ' - ' + str(rel_type) + ' - ' +
                           str(org_type))
    return orgs_details
