from config import FFLOGS_TOKEN

import pandas as pd
import requests
import json
import time
# from api_queries import damage_events

from dmg_distribution import create_action_df
headers = {}

# API config
url = "https://www.fflogs.com/api/v2/client"
api_key = FFLOGS_TOKEN  # or copy/paste your key here
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}



def damage_events(fight_code, fight_id, job, start_time=0, end_time=int(time.time())):
    actions = []
    query = """
            query DpsActions(
                $code: String!
                $id: [Int]!
                $job: String!
                $endTime: Float!
                $startTime: Float!
            ) {
                reportData {
                    report(code: $code) {
                        events(
                            fightIDs: $id
                            startTime: $startTime
                            endTime: $endTime
                            dataType: DamageDone
                            sourceClass: $job
                            viewOptions: 1
                        ) {
                            data
                            nextPageTimestamp
                        }
                        table(fightIDs: $id, dataType: DamageDone)
                        fights(fightIDs: $id, translate: true) {
                            encounterID
                            kill,
                            startTime,
                            endTime,
                            name
                        }
                    }
                }
            }
    """
    # Initial query that gets the fight duration
    variables = {
        "code": fight_code,
        "id": [fight_id],
        "job": job,
        "startTime": start_time,
        "endTime": end_time,
    }
    json_payload = {
        "query": query,
        "variables": variables,
        "operationName": "DpsActions",
    }
    r = requests.post(url=url, json=json_payload, headers=headers)
    r = json.loads(r.text)
    next_timestamp = r["data"]["reportData"]["report"]["events"]["nextPageTimestamp"]
    actions.extend(r["data"]["reportData"]["report"]["events"]["data"])

    # Then remove that because damage done table and fight table doesn't need to be queried for every new page.
    # There might be a more elegant way to do this, but this is good enough.
    query = """
            query DpsActions(
                $code: String!
                $id: [Int]!
                $job: String!
                $endTime: Float!
                $startTime: Float!
            ) {
                reportData {
                    report(code: $code) {
                        events(
                            fightIDs: $id
                            startTime: $startTime
                            endTime: $endTime
                            dataType: DamageDone
                            sourceClass: $job
                            viewOptions: 1
                        ) {
                            data
                            nextPageTimestamp
                        }
                    }
                }
            }
            """
    variables = {
        "code": fight_code,
        "id": [fight_id],
        "job": job,
        "startTime": next_timestamp,
        "endTime": end_time,
    }

    # Get fight time by subtracting downtime from the total time
    # Downtime wont exist as a key if there is no downtime, so a try/except is needed.
    fight_time = r["data"]["reportData"]["report"]["table"]["data"]["totalTime"]
    try:
        downtime = r["data"]["reportData"]["report"]["table"]["data"]["downtime"]
    except KeyError:
        downtime = 0

    fight_time = (fight_time - downtime) / 1000
    fight_name = r["data"]["reportData"]["report"]["fights"][0]["name"]
    # Loop until no more pages
    while next_timestamp is not None:
        json_payload = {
            "query": query,
            "variables": variables,
            "operationName": "DpsActions",
        }

        r = requests.post(url=url, json=json_payload, headers=headers)
        r = json.loads(r.text)
        next_timestamp = r["data"]["reportData"]["report"]["events"][
            "nextPageTimestamp"
        ]
        actions.extend(r["data"]["reportData"]["report"]["events"]["data"])
        variables = {
            "code": fight_code,
            "id": [fight_id],
            "job": job,
            "startTime": next_timestamp,
            "endTime": end_time,
        }
        print(variables)

    return actions, fight_time, fight_name





if __name__ == "__main__":

    code = "gbkzXDBTFAQqjxpL"
    fight_id = 34


    damage = damage_events("gbkzXDBTFAQqjxpL", 34, "Warrior")
    action_df = create_action_df(damage[0], 2576, 940, 2182, "Warrior", 3)

